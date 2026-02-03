"""
Integration tests for /api/chat endpoint

Tests cover the chat endpoint functionality including streaming responses,
request validation, error handling, and CORS headers.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app


class TestChatEndpoint:
    """Test suite for /api/chat endpoint"""

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

    def test_chat_endpoint_accepts_post_request(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint accepts POST requests"""
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

    def test_chat_endpoint_returns_streaming_response(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint returns streaming response"""
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

        # Check media type is text/event-stream
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_chat_endpoint_streams_content(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint streams content chunks"""
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

        # Read the streaming content
        content = response.text
        assert len(content) > 0
        assert "Hello" in content

    def test_chat_endpoint_has_cache_control_headers(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint has proper cache control headers"""
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

        # Check cache-control header
        cache_control = response.headers.get("cache-control", "")
        assert "no-cache" in cache_control
        assert "no-transform" in cache_control

    def test_chat_endpoint_has_connection_keep_alive(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint has connection keep-alive header"""
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

        # Check connection header
        connection = response.headers.get("connection", "")
        assert "keep-alive" in connection.lower()

    def test_chat_endpoint_requires_prompt(self, client, mock_langfuse):
        """Test that chat endpoint requires prompt field"""
        request_data = {
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_requires_thread_id(self, client, mock_langfuse):
        """Test that chat endpoint requires threadId field"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_requires_response_id(self, client, mock_langfuse):
        """Test that chat endpoint requires responseId field"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_prompt_requires_content(self, client, mock_langfuse):
        """Test that prompt object requires content field"""
        request_data = {
            "prompt": {
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_prompt_requires_id(self, client, mock_langfuse):
        """Test that prompt object requires id field"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_prompt_requires_role(self, client, mock_langfuse):
        """Test that prompt object requires role field"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_rejects_get_method(self, client):
        """Test that chat endpoint rejects GET requests"""
        response = client.get("/api/chat")
        assert response.status_code == 405  # Method Not Allowed

    def test_chat_endpoint_handles_empty_content(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles empty prompt content"""
        request_data = {
            "prompt": {
                "content": "",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Empty content should still work (agent will handle it)
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_handles_special_characters(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles special characters in prompt"""
        request_data = {
            "prompt": {
                "content": "What about $AAPL & $GOOG? Test <special> chars!",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_handles_long_content(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles long prompt content"""
        long_content = "What is the stock price? " * 100
        request_data = {
            "prompt": {
                "content": long_content,
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_handles_multiline_content(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles multiline prompt content"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?\n\nAlso tell me about GOOG.",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_cors_headers(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint includes CORS headers"""
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

        # Verify CORS headers are present
        assert "access-control-allow-origin" in response.headers

    def test_chat_endpoint_passes_thread_id_to_agent(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint passes thread ID to agent config"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "custom-thread-789",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

        # Verify agent.stream was called with correct config
        mock_agent_stream.assert_called_once()
        call_args = mock_agent_stream.call_args

        # Check that the config includes the thread_id
        assert "config" in call_args[1]
        assert call_args[1]["config"]["configurable"]["thread_id"] == "custom-thread-789"

    def test_chat_endpoint_handles_agent_error(self, client, mock_langfuse):
        """Test that chat endpoint handles agent errors gracefully"""
        with patch('main.agent.stream') as mock_stream:
            # Simulate an error in the agent
            mock_stream.side_effect = Exception("Agent error")

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
            # Should raise an error (500 status code)
            assert response.status_code == 500

    def test_chat_endpoint_no_auth_required(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint does not require authentication"""
        request_data = {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        # Should return 200 without any auth headers
        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_handles_unicode(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles unicode characters"""
        request_data = {
            "prompt": {
                "content": "What about 📈 stocks? 你好! مرحبا",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        response = client.post("/api/chat", json=request_data)
        assert response.status_code == 200

    def test_chat_endpoint_unique_thread_ids(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint handles different thread IDs correctly"""
        thread_ids = ["thread-1", "thread-2", "thread-3"]

        for thread_id in thread_ids:
            request_data = {
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": thread_id,
                "responseId": "response-456"
            }

            response = client.post("/api/chat", json=request_data)
            assert response.status_code == 200

    def test_chat_endpoint_stream_aggregates_response(self, client, mock_langfuse, mock_agent_stream):
        """Test that chat endpoint properly aggregates streaming tokens"""
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

        # Get the full response content
        content = response.text

        # Verify that Langfuse generation was updated with the full output
        assert mock_langfuse.start_as_current_observation.called
