"""
Unit tests for config.py models (PromptObject, RequestObject)

Tests cover model validation, serialization, and edge cases.
"""

import pytest
from pydantic import ValidationError
from config.config import PromptObject, RequestObject


class TestPromptObject:
    """Test suite for PromptObject model"""

    def test_prompt_object_valid_initialization(self):
        """Test PromptObject can be initialized with valid data"""
        prompt = PromptObject(
            content="What is the stock price of AAPL?",
            id="msg-1",
            role="user"
        )

        assert prompt.content == "What is the stock price of AAPL?"
        assert prompt.id == "msg-1"
        assert prompt.role == "user"

    def test_prompt_object_with_assistant_role(self):
        """Test PromptObject with assistant role"""
        prompt = PromptObject(
            content="Based on the data, AAPL is trading at $150.25",
            id="msg-2",
            role="assistant"
        )

        assert prompt.content == "Based on the data, AAPL is trading at $150.25"
        assert prompt.id == "msg-2"
        assert prompt.role == "assistant"

    def test_prompt_object_missing_required_field(self):
        """Test PromptObject raises ValidationError when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            PromptObject(
                content="Test message"
                # Missing required 'id' and 'role' fields
            )

        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'id' in error_fields
        assert 'role' in error_fields

    def test_prompt_object_missing_content(self):
        """Test PromptObject raises ValidationError when content is missing"""
        with pytest.raises(ValidationError) as exc_info:
            PromptObject(
                id="msg-1",
                role="user"
                # Missing required 'content' field
            )

        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'content' in error_fields

    def test_prompt_object_empty_string_allowed(self):
        """Test PromptObject allows empty strings for fields"""
        prompt = PromptObject(
            content="",
            id="",
            role=""
        )

        assert prompt.content == ""
        assert prompt.id == ""
        assert prompt.role == ""

    def test_prompt_object_wrong_type_for_content(self):
        """Test PromptObject raises ValidationError for wrong content type"""
        with pytest.raises(ValidationError) as exc_info:
            PromptObject(
                content=123,  # Should be string
                id="msg-1",
                role="user"
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'content' for error in errors)

    def test_prompt_object_wrong_type_for_id(self):
        """Test PromptObject raises ValidationError for wrong id type"""
        with pytest.raises(ValidationError) as exc_info:
            PromptObject(
                content="Test message",
                id=123,  # Should be string
                role="user"
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'id' for error in errors)

    def test_prompt_object_wrong_type_for_role(self):
        """Test PromptObject raises ValidationError for wrong role type"""
        with pytest.raises(ValidationError) as exc_info:
            PromptObject(
                content="Test message",
                id="msg-1",
                role=123  # Should be string
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'role' for error in errors)

    def test_prompt_object_serialization(self):
        """Test PromptObject can be serialized to dict"""
        prompt = PromptObject(
            content="Test message",
            id="msg-1",
            role="user"
        )

        prompt_dict = prompt.model_dump()

        assert prompt_dict == {
            "content": "Test message",
            "id": "msg-1",
            "role": "user"
        }

    def test_prompt_object_json_serialization(self):
        """Test PromptObject can be serialized to JSON"""
        import json

        prompt = PromptObject(
            content="Test message",
            id="msg-1",
            role="user"
        )

        prompt_json = prompt.model_dump_json()

        # Verify it's valid JSON
        parsed = json.loads(prompt_json)
        assert parsed["content"] == "Test message"
        assert parsed["id"] == "msg-1"
        assert parsed["role"] == "user"

    def test_prompt_object_from_dict(self):
        """Test PromptObject can be created from dict"""
        data = {
            "content": "Test message",
            "id": "msg-1",
            "role": "user"
        }

        prompt = PromptObject(**data)

        assert prompt.content == "Test message"
        assert prompt.id == "msg-1"
        assert prompt.role == "user"

    def test_prompt_object_model_fields_set(self):
        """Test PromptObject tracks which fields were set"""
        prompt = PromptObject(
            content="Test message",
            id="msg-1",
            role="user"
        )

        assert prompt.model_fields_set == {'content', 'id', 'role'}

    def test_prompt_object_special_characters_in_content(self):
        """Test PromptObject handles special characters in content"""
        prompt = PromptObject(
            content="What's the price of AAPL? (It's $150.25!)",
            id="msg-1",
            role="user"
        )

        assert "What's" in prompt.content
        assert "$150.25" in prompt.content
        assert "()" in prompt.content


class TestRequestObject:
    """Test suite for RequestObject model"""

    def test_request_object_valid_initialization(self, sample_prompt):
        """Test RequestObject can be initialized with valid data"""
        request = RequestObject(
            prompt=sample_prompt,
            threadId="thread-123",
            responseId="response-456"
        )

        assert request.prompt.content == "What is the stock price of AAPL?"
        assert request.threadId == "thread-123"
        assert request.responseId == "response-456"

    def test_request_object_with_inline_prompt(self):
        """Test RequestObject can be initialized with inline PromptObject"""
        request = RequestObject(
            prompt=PromptObject(
                content="Test message",
                id="msg-1",
                role="user"
            ),
            threadId="thread-123",
            responseId="response-456"
        )

        assert request.prompt.content == "Test message"
        assert request.threadId == "thread-123"
        assert request.responseId == "response-456"

    def test_request_object_missing_required_field(self):
        """Test RequestObject raises ValidationError when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                prompt=PromptObject(
                    content="Test",
                    id="msg-1",
                    role="user"
                ),
                threadId="thread-123"
                # Missing required 'responseId' field
            )

        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'responseId' in error_fields

    def test_request_object_missing_prompt(self):
        """Test RequestObject raises ValidationError when prompt is missing"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                threadId="thread-123",
                responseId="response-456"
                # Missing required 'prompt' field
            )

        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'prompt' in error_fields

    def test_request_object_missing_thread_id(self):
        """Test RequestObject raises ValidationError when threadId is missing"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                prompt=PromptObject(
                    content="Test",
                    id="msg-1",
                    role="user"
                ),
                responseId="response-456"
                # Missing required 'threadId' field
            )

        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'threadId' in error_fields

    def test_request_object_wrong_type_for_prompt(self):
        """Test RequestObject raises ValidationError for wrong prompt type"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                prompt="not a PromptObject",  # Should be PromptObject
                threadId="thread-123",
                responseId="response-456"
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'prompt' for error in errors)

    def test_request_object_wrong_type_for_thread_id(self):
        """Test RequestObject raises ValidationError for wrong threadId type"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                prompt=PromptObject(
                    content="Test",
                    id="msg-1",
                    role="user"
                ),
                threadId=123,  # Should be string
                responseId="response-456"
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'threadId' for error in errors)

    def test_request_object_wrong_type_for_response_id(self):
        """Test RequestObject raises ValidationError for wrong responseId type"""
        with pytest.raises(ValidationError) as exc_info:
            RequestObject(
                prompt=PromptObject(
                    content="Test",
                    id="msg-1",
                    role="user"
                ),
                threadId="thread-123",
                responseId=456  # Should be string
            )

        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'responseId' for error in errors)

    def test_request_object_serialization(self, sample_prompt):
        """Test RequestObject can be serialized to dict"""
        request = RequestObject(
            prompt=sample_prompt,
            threadId="thread-123",
            responseId="response-456"
        )

        request_dict = request.model_dump()

        assert request_dict == {
            "prompt": {
                "content": "What is the stock price of AAPL?",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

    def test_request_object_json_serialization(self, sample_prompt):
        """Test RequestObject can be serialized to JSON"""
        import json

        request = RequestObject(
            prompt=sample_prompt,
            threadId="thread-123",
            responseId="response-456"
        )

        request_json = request.model_dump_json()

        # Verify it's valid JSON
        parsed = json.loads(request_json)
        assert parsed["prompt"]["content"] == "What is the stock price of AAPL?"
        assert parsed["threadId"] == "thread-123"
        assert parsed["responseId"] == "response-456"

    def test_request_object_from_dict(self):
        """Test RequestObject can be created from dict"""
        data = {
            "prompt": {
                "content": "Test message",
                "id": "msg-1",
                "role": "user"
            },
            "threadId": "thread-123",
            "responseId": "response-456"
        }

        request = RequestObject(**data)

        assert request.prompt.content == "Test message"
        assert request.threadId == "thread-123"
        assert request.responseId == "response-456"

    def test_request_object_with_invalid_nested_prompt(self):
        """Test RequestObject raises ValidationError with invalid nested PromptObject"""
        with pytest.raises(ValidationError):
            RequestObject(
                prompt={
                    "content": "Test",
                    # Missing 'id' and 'role' in nested prompt
                },
                threadId="thread-123",
                responseId="response-456"
            )

    def test_request_object_empty_strings_allowed(self):
        """Test RequestObject allows empty strings for threadId and responseId"""
        request = RequestObject(
            prompt=PromptObject(
                content="Test",
                id="msg-1",
                role="user"
            ),
            threadId="",
            responseId=""
        )

        assert request.threadId == ""
        assert request.responseId == ""

    def test_request_object_model_fields_set(self, sample_prompt):
        """Test RequestObject tracks which fields were set"""
        request = RequestObject(
            prompt=sample_prompt,
            threadId="thread-123",
            responseId="response-456"
        )

        assert request.model_fields_set == {'prompt', 'threadId', 'responseId'}


class TestConfigIntegration:
    """Integration tests for config models working together"""

    def test_full_request_creation_workflow(self):
        """Test creating a complete request object from scratch"""
        # Create prompt
        prompt = PromptObject(
            content="What is the stock price of AAPL?",
            id="msg-abc-123",
            role="user"
        )

        # Create request with prompt
        request = RequestObject(
            prompt=prompt,
            threadId="thread-xyz-789",
            responseId="response-def-456"
        )

        # Verify all data is accessible
        assert request.prompt.content == "What is the stock price of AAPL?"
        assert request.prompt.id == "msg-abc-123"
        assert request.prompt.role == "user"
        assert request.threadId == "thread-xyz-789"
        assert request.responseId == "response-def-456"

    def test_round_trip_serialization(self):
        """Test that models can survive serialization and deserialization"""
        original = RequestObject(
            prompt=PromptObject(
                content="Test message",
                id="msg-1",
                role="user"
            ),
            threadId="thread-123",
            responseId="response-456"
        )

        # Serialize to dict
        serialized = original.model_dump()

        # Deserialize back
        deserialized = RequestObject(**serialized)

        # Verify they're equivalent
        assert deserialized.model_dump() == original.model_dump()

    def test_multiple_requests_with_different_prompts(self):
        """Test creating multiple requests with different prompts"""
        user_prompt = PromptObject(
            content="What's the price?",
            id="msg-1",
            role="user"
        )

        assistant_prompt = PromptObject(
            content="The price is $150.25",
            id="msg-2",
            role="assistant"
        )

        request1 = RequestObject(
            prompt=user_prompt,
            threadId="thread-1",
            responseId="response-1"
        )

        request2 = RequestObject(
            prompt=assistant_prompt,
            threadId="thread-1",
            responseId="response-2"
        )

        assert request1.prompt.role == "user"
        assert request2.prompt.role == "assistant"
        assert request1.threadId == request2.threadId  # Same thread
        assert request1.responseId != request2.responseId  # Different responses
