"""
Integration tests for API authentication

Tests cover the authentication functionality for protected endpoints,
including API key validation via headers and query parameters.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app


class TestAuthIntegration:
    """Test suite for API authentication integration"""

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
                Mock(content="Hello"),
                Mock(content="!"),
                Mock(content=" How"),
                Mock(content=" can"),
                Mock(content=" I"),
                Mock(content=" help"),
                Mock(content=" you"),
                Mock(content="?")
            ]

            # Mock the streaming iterator
            mock_stream.return_value = iter(mock_tokens)
            yield mock_stream


class TestAuthDisabled(TestAuthIntegration):
    """Test suite for behavior when authentication is disabled"""

    def test_chat_endpoint_allways_access_without_auth_when_disabled(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint allows requests without auth when REQUIRE_API_KEY is false"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
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

    def test_chat_endpoint_ignores_invalid_key_when_disabled(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint ignores invalid keys when auth is disabled"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Provide an invalid API key
            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "invalid-key"}
            )
            assert response.status_code == 200

    def test_chat_endpoint_env_var_not_set(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint allows requests when REQUIRE_API_KEY is not set"""
        # Remove REQUIRE_API_KEY from environment
        env_copy = os.environ.copy()
        env_copy.pop("REQUIRE_API_KEY", None)

        with patch.dict(os.environ, env_copy, clear=True):
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


class TestAuthEnabled(TestAuthIntegration):
    """Test suite for behavior when authentication is enabled"""

    def test_chat_endpoint_with_valid_header_key(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint accepts valid API key via X-API-Key header"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "test-valid-api-key"}
            )
            assert response.status_code == 200

    def test_chat_endpoint_with_valid_query_param_key(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint accepts valid API key via api_key query parameter"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat?api_key=test-valid-api-key",
                json=request_data
            )
            assert response.status_code == 200

    def test_chat_endpoint_header_takes_precedence(self, client, mock_langfuse, mock_agent_stream):
        """Test that X-API-Key header takes precedence over query parameter"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "test-valid-api-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Both header and query param, but only header is valid
            response = client.post(
                "/api/chat?api_key=wrong-query-key",
                json=request_data,
                headers={"X-API-Key": "test-valid-api-key"}
            )
            assert response.status_code == 200

    def test_chat_endpoint_with_special_characters_in_key(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint works with special characters in API key"""
        special_key = "key-with-special.chars_123"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": special_key
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": special_key}
            )
            assert response.status_code == 200

    def test_chat_endpoint_with_uuid_key(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint works with UUID-like API key"""
        uuid_key = "550e8400-e29b-41d4-a716-446655440000"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": uuid_key
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": uuid_key}
            )
            assert response.status_code == 200


class TestAuthErrors(TestAuthIntegration):
    """Test suite for authentication error handling"""

    def test_chat_endpoint_returns_401_without_key(self, client, mock_langfuse):
        """Test that chat endpoint returns 401 when no API key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "expected-key"
        }):
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
            assert response.status_code == 401
            assert "API key is required" in response.json()["detail"]

    def test_chat_endpoint_returns_401_with_empty_key(self, client, mock_langfuse):
        """Test that chat endpoint returns 401 when empty API key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "expected-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": ""}
            )
            assert response.status_code == 401

    def test_chat_endpoint_returns_403_with_invalid_header_key(self, client, mock_langfuse):
        """Test that chat endpoint returns 403 when invalid header key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "wrong-key"}
            )
            assert response.status_code == 403
            assert "Invalid API key" in response.json()["detail"]

    def test_chat_endpoint_returns_403_with_invalid_query_key(self, client, mock_langfuse):
        """Test that chat endpoint returns 403 when invalid query key is provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat?api_key=wrong-key",
                json=request_data
            )
            assert response.status_code == 403
            assert "Invalid API key" in response.json()["detail"]

    def test_chat_endpoint_case_sensitive_key(self, client, mock_langfuse):
        """Test that API key is case-sensitive"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "SecretKey"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "secretkey"}
            )
            assert response.status_code == 403

    def test_chat_endpoint_whitespace_matters(self, client, mock_langfuse):
        """Test that whitespace in API key is significant"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "my-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": " my-key "}
            )
            assert response.status_code == 403

    def test_chat_endpoint_returns_500_when_api_key_not_configured(self, client, mock_langfuse):
        """Test that chat endpoint returns 500 when API_KEY env var is not set"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "true"}, clear=True):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "some-key"}
            )
            assert response.status_code == 500
            assert "Server configuration error" in response.json()["detail"]
            assert "API key not configured" in response.json()["detail"]

    def test_chat_endpoint_returns_500_when_api_key_env_empty(self, client, mock_langfuse):
        """Test that chat endpoint returns 500 when API_KEY env var is empty"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": ""
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "some-key"}
            )
            assert response.status_code == 500


class TestAuthWithRateLimiting(TestAuthIntegration):
    """Test suite for authentication interaction with rate limiting"""

    def test_auth_checked_before_rate_limit(self, client, mock_langfuse):
        """Test that authentication is checked before rate limiting"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "valid-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Invalid key should return 403, not 429
            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "invalid-key"}
            )
            assert response.status_code == 403

    def test_valid_auth_allows_rate_limiting(self, client, mock_langfuse, mock_agent_stream):
        """Test that valid authentication allows rate limiting to work"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "valid-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Valid key should return 200 (rate limiting applies separately)
            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": "valid-key"}
            )
            assert response.status_code == 200


class TestAuthWithDifferentKeys(TestAuthIntegration):
    """Test suite for authentication with different API key formats"""

    def test_very_long_api_key(self, client, mock_langfuse, mock_agent_stream):
        """Test authentication with very long API key"""
        long_key = "a" * 1000
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": long_key
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": long_key}
            )
            assert response.status_code == 200

    def test_api_key_with_unicode(self, client, mock_langfuse, mock_agent_stream):
        """Test authentication with unicode characters in API key"""
        unicode_key = "key-with-émojis-🔑"
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": unicode_key
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            response = client.post(
                "/api/chat",
                json=request_data,
                headers={"X-API-Key": unicode_key}
            )
            assert response.status_code == 200

    def test_query_param_fallback_with_invalid_header(self, client, mock_langfuse, mock_agent_stream):
        """Test that query param is used when header is None"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Query param has valid key, header is not provided
            response = client.post(
                "/api/chat?api_key=correct-key",
                json=request_data
            )
            assert response.status_code == 200

    def test_both_params_invalid(self, client, mock_langfuse):
        """Test that authentication fails when both params are invalid"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "correct-key"
        }):
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "thread-123",
                "responseId": "response-456"
            }

            # Both header and query param are wrong
            response = client.post(
                "/api/chat?api_key=wrong-query-key",
                json=request_data,
                headers={"X-API-Key": "wrong-header-key"}
            )
            assert response.status_code == 403


class TestHealthCheckEndpoint(TestAuthIntegration):
    """Test suite for health check endpoint authentication"""

    def test_health_check_no_auth_required(self, client):
        """Test that health check endpoint does not require authentication"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "some-key"
        }):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"

    def test_health_check_ignores_auth_header(self, client):
        """Test that health check endpoint ignores auth header if provided"""
        with patch.dict(os.environ, {
            "REQUIRE_API_KEY": "true",
            "API_KEY": "some-key"
        }):
            response = client.get(
                "/health",
                headers={"X-API-Key": "invalid-key"}
            )
            assert response.status_code == 200
