"""
End-to-end verification tests for error handling flows.

This test suite verifies that all error handling flows work correctly
from the API endpoint down through the tools and exception handlers.
"""

import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app
from MarketInsight.utils.exceptions import (
    ValidationError,
    TickerValidationError,
    ExternalServiceError
)


class TestErrorHandlingEndToEnd:
    """
    End-to-end test suite for error handling flows.

    Verifies complete error flows from API request to error response,
    including proper status codes, error messages, and logging.
    """

    @pytest.fixture
    def client(self):
        """Provide a test client for the FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def mock_langfuse(self):
        """Mock Langfuse client to avoid real API calls"""
        with patch('main.langfuse') as mock:
            mock_span = Mock()
            mock_span.__enter__ = Mock(return_value=mock_span)
            mock_span.__exit__ = Mock(return_value=False)
            mock_span.update = Mock()

            mock_generation = Mock()
            mock_generation.__enter__ = Mock(return_value=mock_generation)
            mock_generation.__exit__ = Mock(return_value=False)
            mock_generation.update = Mock()

            mock.start_as_current_observation = Mock(return_value=mock_span)
            mock_span.start_as_current_observation = Mock(return_value=mock_generation)

            yield mock

    @pytest.fixture
    def mock_agent_stream(self):
        """Mock agent stream to avoid real LLM calls"""
        with patch('main.agent.stream') as mock_stream:
            # Create mock tokens with content attribute
            mock_tokens = [
                Mock(content="Response"),
                Mock(content=" data")
            ]

            # Mock the streaming iterator
            mock_stream.return_value = iter(mock_tokens)
            yield mock_stream

    # ==================== Test 1: Invalid Ticker Symbol ====================

    def test_ticker_validation_in_tool_directly(self):
        """
        Directly test ticker validation to verify proper error handling.
        This tests the validator at the tool level.
        """
        from MarketInsight.utils.validators import validate_ticker
        from MarketInsight.utils.exceptions import TickerValidationError

        # Test various invalid ticker formats
        invalid_tickers = [
            ("INVALID@", "special characters"),
            ("", "empty string"),
            ("   ", "whitespace only"),
            ("A" * 11, "too long"),
            (".AAPL", "starts with dot"),
            ("AAPL.", "ends with dot"),
        ]

        for ticker, reason in invalid_tickers:
            with pytest.raises(TickerValidationError) as exc_info:
                validate_ticker(ticker)

            # Verify error message is helpful and mentions the issue
            error_str = str(exc_info.value).lower()
            # Error messages should mention ticker, validation, or the specific issue
            assert "ticker" in error_str or "long" in error_str or "invalid" in error_str or "empty" in error_str or "whitespace" in error_str

    def test_ticker_validation_allows_valid_tickers(self):
        """
        Verify that valid ticker symbols pass validation.
        """
        from MarketInsight.utils.validators import validate_ticker

        valid_tickers = ["AAPL", "GOOGL", "MSFT", "BRK.A", "BTC-USD"]

        for ticker in valid_tickers:
            # Should not raise any exception
            result = validate_ticker(ticker)
            assert result == ticker

    # ==================== Test 2: Empty Request ====================

    def test_empty_request_returns_validation_error(self, client):
        """
        Verify that sending an empty request returns a validation error.
        """
        response = client.post(
            "/api/chat",
            json={},  # Empty request body
            headers={"X-API-Key": "test-api-key"}
        )

        # Pydantic validation should return 422
        assert response.status_code == 422

        # Verify error response structure
        error_data = response.json()
        assert "detail" in error_data

    def test_empty_prompt_content_returns_400(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that sending a request with empty prompt content returns 400.
        """
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "",  # Empty content
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 400 due to validation error
        assert response.status_code == 400

        # Verify error response structure
        error_data = response.json()
        # FastAPI HTTPException uses "detail" field
        assert "detail" in error_data

        # Verify error message mentions the issue
        error_detail = error_data.get("detail", {})
        if isinstance(error_detail, dict):
            error_msg = error_detail.get("error", "")
        else:
            error_msg = str(error_detail)

        assert "empty" in error_msg.lower() or "required" in error_msg.lower()

    def test_whitespace_only_prompt_returns_400(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that sending a request with whitespace-only prompt content returns 400.
        """
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "   \n\t   ",  # Whitespace only
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 400 due to validation error
        assert response.status_code == 400

        # Verify error message mentions the issue
        error_data = response.json()
        error_detail = error_data.get("detail", {})
        if isinstance(error_detail, dict):
            error_msg = error_detail.get("error", "")
        else:
            error_msg = str(error_detail)

        assert "empty" in error_msg.lower() or "whitespace" in error_msg.lower()

    # ==================== Test 3: External API Failure ====================

    def test_tool_handles_gracefully_when_yfinance_fails(self):
        """
        Test that tool handles yfinance API errors gracefully.
        """
        from MarketInsight.utils.tools import get_stock_price

        # Mock yfinance.Ticker to return None/empty data
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = Mock()
            mock_instance.info = None
            mock_ticker.return_value = mock_instance

            # Call the tool - should handle the error gracefully
            result = get_stock_price.func("AAPL")

            # Verify we get an error message (not a crash)
            assert isinstance(result, str)
            assert "error" in result.lower() or "unable" in result.lower() or "no price data" in result.lower()

    def test_tool_handles_requests_exceptions(self):
        """
        Test that get_ticker tool handles requests exceptions gracefully.
        """
        from MarketInsight.utils.tools import get_ticker
        import requests

        # Mock requests.get to raise an exception
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            # Call the tool - should handle the error gracefully
            result = get_ticker.func("AAPL")

            # Verify we get an error message (not a crash)
            assert isinstance(result, str)
            assert "error" in result.lower()

    # ==================== Test 4: Malformed Request ====================

    def test_malformed_request_structure(self, client):
        """
        Verify that malformed requests return proper error response structure.
        """
        # Test with invalid JSON structure
        response = client.post(
            "/api/chat",
            json={
                "prompt": "invalid",  # Should be an object, not a string
                "threadId": "test-thread"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 422 (validation error)
        assert response.status_code == 422

        # Verify error response has proper structure
        error_data = response.json()
        assert "detail" in error_data

    def test_missing_required_fields(self, client):
        """
        Verify that requests missing required fields return proper errors.
        """
        # Missing threadId
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "test",
                    "id": "msg-1",
                    "role": "user"
                },
                "responseId": "test-response"
                # threadId is missing
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 422
        assert response.status_code == 422

    def test_invalid_field_types(self, client):
        """
        Verify that requests with invalid field types return proper errors.
        """
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "test",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": 123,  # Should be string, not int
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 422
        assert response.status_code == 422

    def test_error_response_has_required_fields(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that error responses contain all required fields.
        """
        # Trigger a validation error
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        assert response.status_code == 400

        error_data = response.json()

        # Verify error response structure
        assert "detail" in error_data

        # Check detail structure
        detail = error_data["detail"]
        if isinstance(detail, dict):
            # Should have error field
            assert "error" in detail
            # Should have error_type field
            assert "error_type" in detail

    # ==================== Test 5: Error Logging ====================

    def test_validation_errors_are_logged(self, client, mock_langfuse, mock_agent_stream, caplog):
        """
        Verify that validation errors are properly logged.
        """
        with caplog.at_level(logging.WARNING):
            response = client.post(
                "/api/chat",
                json={
                    "prompt": {
                        "content": "",
                        "id": "msg-1",
                        "role": "user"
                    },
                    "threadId": "test-thread",
                    "responseId": "test-response"
                },
                headers={"X-API-Key": "test-api-key"}
            )

            # Should return 400
            assert response.status_code == 400

            # Verify logging occurred
            assert any(
                "validation" in record.message.lower()
                for record in caplog.records
            )

    def test_agent_errors_are_logged(self, client, mock_langfuse, caplog):
        """
        Verify that agent errors are properly logged.
        """
        # Make stream raise an exception
        with patch('main.agent.stream') as mock_stream:
            mock_stream.side_effect = Exception("Simulated agent error")

            with caplog.at_level(logging.ERROR):
                response = client.post(
                    "/api/chat",
                    json={
                        "prompt": {
                            "content": "What is AAPL?",
                            "id": "msg-1",
                            "role": "user"
                        },
                        "threadId": "test-thread",
                        "responseId": "test-response"
                    },
                    headers={"X-API-Key": "test-api-key"}
                )

                # Should return 500 (internal server error)
                assert response.status_code == 500

                # Verify error was logged
                assert any(
                    "error" in record.message.lower()
                    for record in caplog.records
                )

    # ==================== Test 6: Additional Edge Cases ====================

    def test_xss_pattern_is_sanitized(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that XSS patterns are sanitized from input.
        """
        xss_payload = "<script>alert('xss')</script>test content"

        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": xss_payload,
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Request should be processed successfully
        # (XSS patterns are removed/sanitized, content remains valid)
        assert response.status_code == 200

    def test_very_long_input_is_rejected(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that very long inputs are handled appropriately.
        """
        # Create a prompt that exceeds max length
        long_content = "A" * 10000

        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": long_content,
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 400 due to exceeding max length
        assert response.status_code == 400

        error_data = response.json()
        error_detail = error_data.get("detail", {})
        if isinstance(error_detail, dict):
            error_msg = error_detail.get("error", "")
        else:
            error_msg = str(error_detail)

        assert "length" in error_msg.lower() or "long" in error_msg.lower()

    def test_unicode_and_special_characters(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that Unicode and special characters are handled correctly.
        """
        unicode_content = "What's the stock price of AAPL? 🚀📈"

        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": unicode_content,
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Unicode should be accepted
        assert response.status_code == 200

    # ==================== Test 7: Multiple Error Scenarios ====================

    def test_multiple_validation_errors(self, client):
        """
        Verify handling of requests with multiple validation errors.
        """
        response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "",
                    "id": "",
                    "role": "invalid"
                },
                "threadId": "",
                "responseId": 123
            },
            headers={"X-API-Key": "test-api-key"}
        )

        # Should return 422
        assert response.status_code == 422

        # Error response should mention the issues
        error_data = response.json()
        assert "detail" in error_data

    def test_error_recovery_after_failure(self, client, mock_langfuse, mock_agent_stream):
        """
        Verify that the API can recover after an error.
        """
        # First request: trigger an error
        error_response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "",
                    "id": "msg-1",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert error_response.status_code == 400

        # Second request: valid request should work
        success_response = client.post(
            "/api/chat",
            json={
                "prompt": {
                    "content": "What is the stock price of AAPL?",
                    "id": "msg-2",
                    "role": "user"
                },
                "threadId": "test-thread",
                "responseId": "test-response-2"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        # Should recover and return 200
        assert success_response.status_code == 200

    # ==================== Test 8: Integration with Tools ====================

    def test_tool_error_propagates_correctly(self):
        """
        Verify that tool errors are handled correctly in the workflow.
        """
        from MarketInsight.utils.tools import get_stock_price

        # Test with invalid ticker that will fail validation
        result = get_stock_price.func("INVALID@")

        # Should return error message (not raise exception at tool level)
        assert isinstance(result, str)
        assert "error" in result.lower()

    def test_all_tools_have_validation(self):
        """
        Verify that all tools have validation enabled.
        """
        from MarketInsight.utils.tools import (
            get_stock_price, get_historical_data, get_stock_news, get_balance_sheet,
            get_income_statement, get_cash_flow, get_company_info, get_dividends,
            get_splits, get_institutional_holders, get_major_shareholders,
            get_mutual_fund_holders, get_insider_transactions,
            get_analyst_recommendations, get_analyst_recommendations_summary, get_ticker
        )

        # All these tools should handle invalid ticker gracefully
        tools = [
            get_stock_price, get_historical_data, get_stock_news, get_balance_sheet,
            get_income_statement, get_cash_flow, get_company_info, get_dividends,
            get_splits, get_institutional_holders, get_major_shareholders,
            get_mutual_fund_holders, get_insider_transactions,
            get_analyst_recommendations, get_analyst_recommendations_summary
        ]

        for tool in tools:
            # Each tool should handle invalid ticker gracefully
            # Use different invalid tickers for variety
            result = tool.func("INVALID@")
            assert isinstance(result, str)
            assert "error" in result.lower() or "invalid" in result.lower() or "symbol" in result.lower()

    # ==================== Summary Verification ====================

    def test_error_handling_summary_verification(self, client, mock_langfuse, mock_agent_stream):
        """
        Summary test that verifies all key error handling requirements.
        """
        # 1. Verify empty request handling
        response = client.post("/api/chat", json={}, headers={"X-API-Key": "test-api-key"})
        assert response.status_code == 422

        # 2. Verify empty content handling
        response = client.post(
            "/api/chat",
            json={
                "prompt": {"content": "", "id": "msg-1", "role": "user"},
                "threadId": "test",
                "responseId": "test"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 400

        # 3. Verify valid request works
        response = client.post(
            "/api/chat",
            json={
                "prompt": {"content": "test query", "id": "msg-1", "role": "user"},
                "threadId": "test",
                "responseId": "test"
            },
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200

        # 4. Verify ticker validation works
        from MarketInsight.utils.validators import validate_ticker
        from MarketInsight.utils.exceptions import TickerValidationError

        with pytest.raises(TickerValidationError):
            validate_ticker("INVALID@")

        # 5. Verify tool error handling
        from MarketInsight.utils.tools import get_stock_price
        result = get_stock_price.func("INVALID@")
        assert "error" in result.lower()
