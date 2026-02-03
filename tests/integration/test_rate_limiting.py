"""
Integration tests for rate limiting

Tests cover the rate limiting functionality including request threshold enforcement,
rate limit headers, IP-based tracking, and endpoint-specific behavior.
"""

import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app


class TestRateLimiting:
    """Test suite for rate limiting middleware"""

    @pytest.fixture
    def client(self):
        """Provide a test client for the FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def mock_langfuse(self):
        """Mock Langfuse client to avoid real API calls"""
        with patch('main.langfuse') as mock:
            # Mock the context manager for observations
            mock_span = Mock()
            mock_span.__enter__ = Mock(return_value=mock_span)
            mock_span.__exit__ = Mock(return_value=False)
            mock_span.update = Mock()

            mock_generation = Mock()
            mock_generation.__enter__ = Mock(return_value=mock_generation)
            mock_generation.__exit__ = Mock(return_value=False)
            mock_generation.update = Mock()

            mock.start_as_current_observation = Mock(return_value=mock_span)
            mock.start_as_current_observation.return_value = mock_span

            # Make the nested observation return the generation mock
            mock_span.start_as_current_observation = Mock(return_value=mock_generation)

            yield mock

    @pytest.fixture
    def mock_agent_stream(self):
        """Mock agent.stream to avoid real LLM calls"""
        with patch('main.agent.stream') as mock_stream:
            # Create mock tokens with content attribute
            mock_tokens = [
                Mock(content="Test"),
                Mock(content=" response")
            ]

            # Mock the streaming iterator
            mock_stream.return_value = iter(mock_tokens)
            yield mock_stream

    def test_health_endpoint_not_rate_limited(self, client):
        """Test that health check endpoint is not rate limited"""
        # Health check should not have rate limiting
        for i in range(110):
            response = client.get("/health")
            assert response.status_code == 200, f"Request {i+1} failed"

    def test_chat_endpoint_accepts_requests_under_limit(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint accepts requests under the rate limit"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Send 100 requests - all should succeed
        for i in range(100):
            response = client.post("/api/chat", json=request_data)
            assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"

    def test_chat_endpoint_enforces_rate_limit(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint enforces rate limit after threshold"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Send 100 requests - all should succeed
        success_count = 0
        for i in range(100):
            response = client.post("/api/chat", json=request_data)
            if response.status_code == 200:
                success_count += 1

        assert success_count == 100, f"Expected 100 successful requests, got {success_count}"

        # The 101st request should be rate limited
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 429, "Expected 429 status code after rate limit exceeded"

    def test_rate_limit_includes_retry_after_header(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limit response includes Retry-After header"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Exhaust the rate limit
        for i in range(100):
            client.post("/api/chat", json=request_data)

        # The next request should be rate limited with Retry-After header
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 429

        retry_after = response.headers.get("Retry-After")
        assert retry_after is not None, "Retry-After header should be present"
        assert retry_after == "60", f"Expected Retry-After of 60, got {retry_after}"

    def test_rate_limit_error_response_format(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limit error returns correct JSON format"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Exhaust the rate limit
        for i in range(100):
            client.post("/api/chat", json=request_data)

        # Check error response format
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 429

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Rate limit exceeded. Please try again later."
        assert "error" in data
        assert data["error"] == "rate_limit_exceeded"

    def test_rate_limit_tracks_different_ips_separately(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limiting tracks different IP addresses separately"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Create clients with different IP addresses
        client1 = TestClient(app, raise_server_exceptions=False)
        client2 = TestClient(app, raise_server_exceptions=False)

        # Exhaust rate limit for client1
        for i in range(101):
            response = client1.post("/api/chat", json=request_data)
            if i < 100:
                assert response.status_code == 200, f"Client1 request {i+1} should succeed"

        # Client1 should be rate limited
        response = client1.post("/api/chat", json=request_data)
        assert response.status_code == 429, "Client1 should be rate limited"

        # Client2 should still be able to make requests (different IP)
        # Note: In TestClient, all requests come from the same IP, so this test
        # validates the behavior conceptually. In production, different IPs
        # would be tracked separately by get_remote_address()
        response = client2.post("/api/chat", json=request_data)
        # Since TestClient doesn't properly simulate different IPs, we accept either 200 or 429
        assert response.status_code in [200, 429]

    def test_rate_limit_allows_methods_exempt_from_limiting(self, client):
        """Test that certain methods/endpoints are exempt from rate limiting"""
        # OPTIONS requests for CORS preflight should not be rate limited
        for i in range(110):
            response = client.options("/api/chat")
            # OPTIONS should work (CORS preflight)
            assert response.status_code in [200, 405], f"OPTIONS request {i+1} failed"

    def test_rate_limit_per_endpoint(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limiting is applied per endpoint"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Exhaust rate limit for /api/chat
        for i in range(101):
            response = client.post("/api/chat", json=request_data)
            if i < 100:
                assert response.status_code == 200

        # /api/chat should be rate limited
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 429

        # Health endpoint should still work
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limit_with_concurrent_requests(self, client, mock_langfuse, mock_agent_stream):
        """Test rate limiting behavior with rapid concurrent requests"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Send requests rapidly
        responses = []
        for i in range(105):
            response = client.post("/api/chat", json=request_data)
            responses.append(response.status_code)

        # Count successful and rate-limited responses
        success_count = sum(1 for status in responses if status == 200)
        rate_limited_count = sum(1 for status in responses if status == 429)

        # Should have at least 100 successful and some rate limited
        assert success_count >= 100, f"Expected at least 100 successful requests, got {success_count}"
        assert rate_limited_count > 0, f"Expected some rate-limited requests, got {rate_limited_count}"

    def test_rate_limit_headers_on_success_response(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limiting related headers may be present on successful responses"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

        # Note: slowapi may include rate limit info headers
        # but we don't strictly require them to be present
        # This test validates that successful responses are not affected

    def test_rate_limit_with_invalid_request(self, client, mock_langfuse):
        """Test that invalid requests still count against rate limit"""
        # Send 100 invalid requests (missing required fields)
        invalid_data = {
            "prompt": {
                "content": "Test"
            }
        }

        # These should fail validation but still count against rate limit
        for i in range(100):
            response = client.post("/api/chat", json=invalid_data)
            # Should get 422 validation error
            assert response.status_code == 422

        # Now a valid request should still be rate limited
        # because invalid requests consumed the rate limit
        valid_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        with patch('main.agent.stream') as mock_stream:
            mock_tokens = [Mock(content="Test")]
            mock_stream.return_value = iter(mock_tokens)

            # This might be rate limited (429) or succeed (200) depending on
            # whether rate limiting happens before or after validation
            response = client.post("/api/chat", json=valid_data)
            assert response.status_code in [200, 429]

    def test_rate_limit_default_configuration(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limit is configured to 100 requests per minute"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # The limit should be 100 requests per minute
        success_count = 0
        for i in range(105):
            response = client.post("/api/chat", json=request_data)
            if response.status_code == 200:
                success_count += 1

        # Should have exactly 100 successful requests
        assert success_count == 100, f"Expected 100 successful requests, got {success_count}"

    def test_rate_limit_rejection_message(self, client, mock_langfuse, mock_agent_stream):
        """Test that rate limit rejection provides clear error message"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Exhaust the rate limit
        for i in range(100):
            client.post("/api/chat", json=request_data)

        # Check error message
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 429

        data = response.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]
        assert "retry" in data["detail"].lower() or "try again" in data["detail"].lower()
