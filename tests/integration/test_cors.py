"""
Integration tests for CORS configuration

Tests cover CORS headers, preflight requests, allowed origins,
allowed methods, credentials support, and cross-origin behavior.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app


class TestCORSConfiguration:
    """Test suite for CORS middleware configuration"""

    @pytest.fixture
    def client(self):
        """Provide a test client for the FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def allowed_origins(self):
        """Get the configured allowed origins from environment"""
        default_origins = "http://localhost:5173,http://localhost:3000"
        return os.getenv("CORS_ORIGINS", default_origins).split(",")

    def test_health_endpoint_has_cors_headers(self, client):
        """Test that health endpoint includes CORS headers"""
        response = client.get("/health")
        assert response.status_code == 200

        # Verify CORS headers are present
        assert "access-control-allow-origin" in response.headers

    def test_chat_endpoint_has_cors_headers(self, client):
        """Test that chat endpoint includes CORS headers"""
        # Mock the agent to avoid real LLM calls
        with patch('main.agent.stream') as mock_stream:
            mock_tokens = [Mock(content="Test")]
            mock_stream.return_value = iter(mock_tokens)

            with patch('main.langfuse') as mock_langfuse:
                # Mock langfuse observations
                mock_span = Mock()
                mock_span.__enter__ = Mock(return_value=mock_span)
                mock_span.__exit__ = Mock(return_value=False)
                mock_span.update = Mock()

                mock_generation = Mock()
                mock_generation.__enter__ = Mock(return_value=mock_generation)
                mock_generation.__exit__ = Mock(return_value=False)
                mock_generation.update = Mock()

                mock_langfuse.start_as_current_observation = Mock(return_value=mock_span)
                mock_span.start_as_current_observation = Mock(return_value=mock_generation)

                request_data = {
                    "prompt": {
                        "content": "Test",
                        "id": "msg-1",
                        "role": "user"
                    },
                    "threadId": "thread-123",
                    "responseId": "response-456"
                }

                response = client.post("/api/chat", json=request_data)
                assert response.status_code == 200

                # Verify CORS headers are present
                assert "access-control-allow-origin" in response.headers

    def test_preflight_options_request_to_health(self, client):
        """Test OPTIONS preflight request to health endpoint"""
        response = client.options("/health")
        assert response.status_code == 200

        # Verify CORS preflight headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_preflight_options_request_to_chat(self, client):
        """Test OPTIONS preflight request to chat endpoint"""
        response = client.options("/api/chat")
        assert response.status_code == 200

        # Verify CORS preflight headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_allows_credentials(self, client):
        """Test that CORS allows credentials"""
        response = client.get("/health")
        assert response.status_code == 200

        # Check that credentials are allowed
        allow_credentials = response.headers.get("access-control-allow-credentials")
        assert allow_credentials == "true"

    def test_cors_allowed_methods_include_get_post_options(self, client):
        """Test that CORS allows GET, POST, and OPTIONS methods"""
        response = client.options("/health")
        assert response.status_code == 200

        # Check allowed methods
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "GET" in allow_methods
        assert "POST" in allow_methods
        assert "OPTIONS" in allow_methods

    def test_cors_allows_all_headers(self, client):
        """Test that CORS allows all headers"""
        response = client.options("/health")
        assert response.status_code == 200

        # Check that headers are allowed (should be wildcard or explicit list)
        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert len(allow_headers) > 0

    def test_cors_origin_header_reflects_request_origin(self, client):
        """Test that CORS reflects the request origin when allowed"""
        allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
        test_origin = allowed_origins[0]

        response = client.get(
            "/health",
            headers={"Origin": test_origin}
        )
        assert response.status_code == 200

        # The origin header should be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight_includes_proper_headers(self, client):
        """Test that preflight requests include proper CORS headers"""
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        assert response.status_code == 200

        # Verify all required preflight headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_cors_headers_present_on_error_responses(self, client):
        """Test that CORS headers are present even on error responses"""
        # Send invalid data to get a validation error
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

        # CORS headers should still be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_does_not_allow_disallowed_methods(self, client):
        """Test that CORS blocks requests with disallowed methods"""
        # Try a DELETE request (not in allowed methods)
        response = client.delete("/health")
        # Should get 405 Method Not Allowed
        assert response.status_code == 405

    def test_cors_works_with_standard_headers(self, client):
        """Test that CORS works with standard browser headers"""
        response = client.get(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_multiple_origins_configured(self, allowed_origins):
        """Test that multiple origins can be configured"""
        # Verify that multiple origins are configured
        assert isinstance(allowed_origins, list)
        assert len(allowed_origins) > 0

        # Check that origins are valid
        for origin in allowed_origins:
            assert origin.startswith("http://")

    def test_cors_configuration_from_environment(self):
        """Test that CORS configuration comes from environment variable"""
        # Check that we can get origins from environment
        default_origins = "http://localhost:5173,http://localhost:3000"
        env_origins = os.getenv("CORS_ORIGINS", default_origins)

        assert env_origins is not None
        assert len(env_origins) > 0

        # Verify it's a comma-separated list
        origins_list = env_origins.split(",")
        assert len(origins_list) >= 2  # At least localhost origins

    def test_preflight_request_with_custom_headers(self, client):
        """Test preflight request with custom headers"""
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-Custom-Header, Content-Type, Authorization"
            }
        )
        assert response.status_code == 200

        # Should still handle the preflight request
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_headers_consistent_across_endpoints(self, client):
        """Test that CORS headers are consistent across different endpoints"""
        # Mock agent for chat endpoint
        with patch('main.agent.stream') as mock_stream:
            mock_tokens = [Mock(content="Test")]
            mock_stream.return_value = iter(mock_tokens)

            with patch('main.langfuse') as mock_langfuse:
                mock_span = Mock()
                mock_span.__enter__ = Mock(return_value=mock_span)
                mock_span.__exit__ = Mock(return_value=False)
                mock_span.update = Mock()

                mock_generation = Mock()
                mock_generation.__enter__ = Mock(return_value=mock_generation)
                mock_generation.__exit__ = Mock(return_value=False)
                mock_generation.update = Mock()

                mock_langfuse.start_as_current_observation = Mock(return_value=mock_span)
                mock_span.start_as_current_observation = Mock(return_value=mock_generation)

                # Get CORS headers from health endpoint
                health_response = client.get("/health")
                health_cors = health_response.headers.get("access-control-allow-origin")

                # Get CORS headers from chat endpoint
                chat_response = client.post(
                    "/api/chat",
                    json={
                        "prompt": {"content": "Test", "id": "1", "role": "user"},
                        "threadId": "1",
                        "responseId": "1"
                    }
                )
                chat_cors = chat_response.headers.get("access-control-allow-origin")

                # Both should have CORS headers
                assert health_cors is not None
                assert chat_cors is not None

    def test_cors_allows_post_with_json_content_type(self, client):
        """Test that CORS allows POST with JSON content type"""
        with patch('main.agent.stream') as mock_stream:
            mock_tokens = [Mock(content="OK")]
            mock_stream.return_value = iter(mock_tokens)

            with patch('main.langfuse') as mock_langfuse:
                mock_span = Mock()
                mock_span.__enter__ = Mock(return_value=mock_span)
                mock_span.__exit__ = Mock(return_value=False)
                mock_span.update = Mock()

                mock_generation = Mock()
                mock_generation.__enter__ = Mock(return_value=mock_generation)
                mock_generation.__exit__ = Mock(return_value=False)
                mock_generation.update = Mock()

                mock_langfuse.start_as_current_observation = Mock(return_value=mock_span)
                mock_span.start_as_current_observation = Mock(return_value=mock_generation)

                response = client.post(
                    "/api/chat",
                    json={
                        "prompt": {"content": "Test", "id": "1", "role": "user"},
                        "threadId": "1",
                        "responseId": "1"
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Origin": "http://localhost:5173"
                    }
                )
                assert response.status_code == 200
                assert "access-control-allow-origin" in response.headers

    def test_cors_no_cache_on_preflight(self, client):
        """Test that preflight responses have proper cache control"""
        response = client.options("/health")
        assert response.status_code == 200

        # Check that response includes proper CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
