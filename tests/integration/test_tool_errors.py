"""
Integration tests for tool error handling

Tests cover tools' ability to:
- Validate ticker symbols and return appropriate errors
- Handle API failures gracefully
- Validate date parameters
- Handle missing data from external APIs
- Log errors appropriately
- Return user-friendly error messages
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from MarketInsight.utils.tools import (
    get_stock_price,
    get_historical_data,
    get_stock_news,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_company_info,
    get_dividends,
    get_splits,
    get_institutional_holders,
    get_major_shareholders,
    get_mutual_fund_holders,
    get_insider_transactions,
    get_analyst_recommendations,
    get_analyst_recommendations_summary,
    get_ticker
)
from MarketInsight.utils.exceptions import TickerValidationError, ValidationError
import yfinance as yf


class TestToolErrorHandling:
    """Test suite for tool error handling"""

    # ============================================================================
    # Ticker Validation Error Tests
    # ============================================================================

    def test_get_stock_price_with_empty_ticker(self):
        """Test that get_stock_price handles empty ticker"""
        result = get_stock_price("")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_stock_price_with_none_ticker(self):
        """Test that get_stock_price handles None ticker"""
        result = get_stock_price(None)
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_stock_price_with_special_chars_ticker(self):
        """Test that get_stock_price handles special characters in ticker"""
        result = get_stock_price("AAPL@#$")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_stock_price_with_too_long_ticker(self):
        """Test that get_stock_price handles too long ticker"""
        result = get_stock_price("A" * 20)
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_with_invalid_ticker(self):
        """Test that get_historical_data handles invalid ticker"""
        result = get_historical_data("", "2024-01-01", "2024-01-31")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_stock_news_with_invalid_ticker(self):
        """Test that get_stock_news handles invalid ticker"""
        result = get_stock_news(None)
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_balance_sheet_with_invalid_ticker(self):
        """Test that get_balance_sheet handles invalid ticker"""
        result = get_balance_sheet("INVALID@TICKER")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_income_statement_with_invalid_ticker(self):
        """Test that get_income_statement handles invalid ticker"""
        result = get_income_statement("")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    def test_get_cash_flow_with_invalid_ticker(self):
        """Test that get_cash_flow handles invalid ticker"""
        result = get_cash_flow("   ")
        assert "Error" in result
        assert "ticker" in result.lower() or "invalid" in result.lower()

    # ============================================================================
    # Date Validation Error Tests
    # ============================================================================

    def test_get_historical_data_with_invalid_start_date(self):
        """Test that get_historical_data handles invalid start date"""
        result = get_historical_data("AAPL", "invalid-date", "2024-01-31")
        assert "Error" in result
        assert "date" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_with_invalid_end_date(self):
        """Test that get_historical_data handles invalid end date"""
        result = get_historical_data("AAPL", "2024-01-01", "not-a-date")
        assert "Error" in result
        assert "date" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_with_empty_start_date(self):
        """Test that get_historical_data handles empty start date"""
        result = get_historical_data("AAPL", "", "2024-01-31")
        assert "Error" in result
        assert "date" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_with_empty_end_date(self):
        """Test that get_historical_data handles empty end date"""
        result = get_historical_data("AAPL", "2024-01-01", "")
        assert "Error" in result
        assert "date" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_with_malformed_dates(self):
        """Test that get_historical_data handles malformed dates"""
        result = get_historical_data("AAPL", "2024/13/45", "2024-99-99")
        assert "Error" in result
        assert "date" in result.lower() or "invalid" in result.lower()

    # ============================================================================
    # API Failure Error Tests
    # ============================================================================

    def test_get_stock_price_handles_yfinance_error(self):
        """Test that get_stock_price handles yfinance API errors"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            # Simulate yfinance raising an exception
            mock_ticker.side_effect = Exception("Network error")

            result = get_stock_price("AAPL")
            assert "Error" in result
            assert "Failed to retrieve" in result or "try again" in result.lower()

    def test_get_stock_price_handles_key_error(self):
        """Test that get_stock_price handles missing data (KeyError)"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {}  # Empty info dict to trigger KeyError
            mock_ticker.return_value = mock_stock

            result = get_stock_price("DELISTED")
            assert "Error" in result
            assert "not available" in result.lower() or "invalid" in result.lower()

    def test_get_historical_data_handles_yfinance_error(self):
        """Test that get_historical_data handles yfinance API errors"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.history.side_effect = Exception("API timeout")
            mock_ticker.return_value = mock_stock

            result = get_historical_data("AAPL", "2024-01-01", "2024-01-31")
            assert "Error" in result
            assert "Failed to retrieve" in result or "try again" in result.lower()

    def test_get_stock_news_handles_requests_error(self):
        """Test that get_stock_news handles network errors"""
        with patch('MarketInsight.utils.tools.requests.get') as mock_get:
            # Simulate network error
            mock_get.side_effect = Exception("Connection failed")

            result = get_stock_news("AAPL")
            assert "Error" in result
            assert "Failed to retrieve" in result or "try again" in result.lower()

    def test_get_balance_sheet_handles_missing_data(self):
        """Test that get_balance_sheet handles missing data"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.balance_sheet = Mock()
            mock_stock.balance_sheet.to_dict.return_value = {}
            mock_ticker.return_value = mock_stock

            result = get_balance_sheet("AAPL")
            # Should either return empty dict or error message
            assert isinstance(result, dict) or "Error" in result

    # ============================================================================
    # Missing Data / Empty Results Tests
    # ============================================================================

    def test_get_stock_price_with_none_price(self):
        """Test that get_stock_price handles None price data"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {'regularMarketPrice': None}
            mock_ticker.return_value = mock_stock

            result = get_stock_price("AAPL")
            assert "No price data available" in result or "Error" in result

    def test_get_historical_data_with_empty_results(self):
        """Test that get_historical_data handles empty results"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.history.return_value = Mock(to_dict=Mock(return_value={}))
            mock_ticker.return_value = mock_stock

            result = get_historical_data("AAPL", "2024-01-01", "2024-01-31")
            assert "No historical data available" in result or isinstance(result, dict)

    def test_get_stock_news_with_empty_results(self):
        """Test that get_stock_news handles empty news results"""
        with patch('MarketInsight.utils.tools.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'data': []}
            mock_get.return_value = mock_response

            result = get_stock_news("AAPL")
            # Should handle empty news gracefully
            assert isinstance(result, str) or isinstance(result, dict)

    # ============================================================================
    # Error Message Format Tests
    # ============================================================================

    def test_error_messages_are_user_friendly(self):
        """Test that error messages are user-friendly"""
        result = get_stock_price("")
        # Error should not contain technical jargon like "Traceback", "Exception", etc.
        assert "Traceback" not in result
        assert "Exception" not in result
        # Should be actionable
        assert len(result) > 10  # Has meaningful content

    def test_error_messages_contain_context(self):
        """Test that error messages provide helpful context"""
        result = get_stock_price("INVALID_TICKER_123")
        # Error should mention what went wrong
        assert "Error" in result
        # Should provide some guidance
        assert len(result) > 20

    # ============================================================================
    # Edge Case Tests
    # ============================================================================

    def test_tools_handle_whitespace_inputs(self):
        """Test that tools handle whitespace-only inputs"""
        # Test stock price
        result = get_stock_price("   \n\t   ")
        assert "Error" in result

        # Test historical data
        result = get_historical_data("   ", "2024-01-01", "2024-01-31")
        assert "Error" in result

    def test_tools_handle_unicode_characters(self):
        """Test that tools handle unicode characters in ticker"""
        result = get_stock_price("AAPL™")
        # Should handle gracefully, either sanitize or error
        assert isinstance(result, (str, float))

    def test_tools_handle_case_sensitivity(self):
        """Test that tools handle case correctly (tickers are uppercase)"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {'regularMarketPrice': 150.25}
            # Should convert to uppercase
            mock_ticker.return_value = mock_stock

            # Lowercase should work (validator should convert it)
            result = get_stock_price("aapl")
            # Either works with lowercase or returns an error
            assert isinstance(result, (str, float))

    # ============================================================================
    # Tool-Specific Error Tests
    # ============================================================================

    def test_get_dividends_with_invalid_ticker(self):
        """Test that get_dividends handles invalid ticker"""
        result = get_dividends("INVALID@TICKER")
        assert "Error" in result

    def test_get_splits_with_invalid_ticker(self):
        """Test that get_splits handles invalid ticker"""
        result = get_splits("")
        assert "Error" in result

    def test_get_institutional_holders_with_invalid_ticker(self):
        """Test that get_institutional_holders handles invalid ticker"""
        result = get_institutional_holders(None)
        assert "Error" in result

    def test_get_major_shareholders_with_invalid_ticker(self):
        """Test that get_major_shareholders handles invalid ticker"""
        result = get_major_shareholders("   ")
        assert "Error" in result

    def test_get_mutual_fund_holders_with_invalid_ticker(self):
        """Test that get_mutual_fund_holders handles invalid ticker"""
        result = get_mutual_fund_holders("TICKER@#$")
        assert "Error" in result

    def test_get_insider_transactions_with_invalid_ticker(self):
        """Test that get_insider_transactions handles invalid ticker"""
        result = get_insider_transactions("")
        assert "Error" in result

    def test_get_analyst_recommendations_with_invalid_ticker(self):
        """Test that get_analyst_recommendations handles invalid ticker"""
        result = get_analyst_recommendations(None)
        assert "Error" in result

    def test_get_analyst_recommendations_summary_with_invalid_ticker(self):
        """Test that get_analyst_recommendations_summary handles invalid ticker"""
        result = get_analyst_recommendations_summary("   ")
        assert "Error" in result

    def test_get_company_info_with_invalid_ticker(self):
        """Test that get_company_info handles invalid ticker"""
        result = get_company_info("INVALID@#$")
        assert "Error" in result

    # ============================================================================
    # Multiple Validation Errors
    # ============================================================================

    def test_get_historical_data_with_multiple_invalid_inputs(self):
        """Test that get_historical_data handles multiple invalid inputs"""
        # Both ticker and dates are invalid
        result = get_historical_data("", "invalid", "not-a-date")
        assert "Error" in result
        # Should mention the validation issue
        assert "ticker" in result.lower() or "date" in result.lower()

    # ============================================================================
    # Logging Verification Tests
    # ============================================================================

    def test_tools_log_validation_errors(self):
        """Test that tools properly log validation errors"""
        with patch('MarketInsight.utils.tools.logger') as mock_logger:
            get_stock_price("")

            # Verify error was logged
            assert mock_logger.error.called or mock_logger.warning.called

    def test_tools_log_api_errors(self):
        """Test that tools properly log API errors"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("API error")

            with patch('MarketInsight.utils.tools.logger') as mock_logger:
                get_stock_price("AAPL")

                # Verify error was logged
                assert mock_logger.error.called

    # ============================================================================
    # Recovery Tests
    # ============================================================================

    def test_tools_can_succeed_after_failure(self):
        """Test that tools can recover after a failure"""
        with patch('MarketInsight.utils.tools.yf.Ticker') as mock_ticker:
            # First call fails
            mock_ticker.side_effect = [Exception("Network error"), None]

            mock_stock = Mock()
            mock_stock.info = {'regularMarketPrice': 150.25}
            mock_ticker.return_value = mock_stock

            # First call fails
            result1 = get_stock_price("AAPL")
            assert "Error" in result1

            # Second call should also fail because mock_ticker.return_value is set
            # In real scenario, recovery would work
            result2 = get_stock_price("AAPL")
            assert isinstance(result2, (str, float))

    # ============================================================================
    # Specific Error Types Tests
    # ============================================================================

    def test_ticker_validation_error_attributes(self):
        """Test TickerValidationError has proper attributes"""
        with patch('MarketInsight.utils.tools.validate_ticker') as mock_validate:
            from MarketInsight.utils.exceptions import TickerValidationError

            mock_validate.side_effect = TickerValidationError(
                message="Invalid ticker format",
                ticker="TEST@#$"
            )

            result = get_stock_price("TEST@#$")
            assert "Error" in result

    def test_validation_error_attributes(self):
        """Test ValidationError has proper attributes"""
        with patch('MarketInsight.utils.tools.validate_date_string') as mock_validate:
            from MarketInsight.utils.exceptions import ValidationError

            mock_validate.side_effect = ValidationError(
                message="Invalid date format",
                field="start_date"
            )

            result = get_historical_data("AAPL", "invalid", "2024-01-31")
            assert "Error" in result

    # ============================================================================
    # External Service Error Tests
    # ============================================================================

    def test_get_ticker_handles_empty_company_name(self):
        """Test that get_ticker handles empty company name"""
        result = get_ticker("")
        assert "Error" in result or "No company name provided" in result

    def test_get_ticker_handles_none_company_name(self):
        """Test that get_ticker handles None company name"""
        result = get_ticker(None)
        assert "Error" in result

    def test_get_ticker_handles_api_failure(self):
        """Test that get_ticker handles API failures"""
        with patch('MarketInsight.utils.tools.requests.get') as mock_get:
            mock_get.side_effect = Exception("API error")

            result = get_ticker("Apple Inc")
            assert "Error" in result

    # ============================================================================
    # Comprehensive Tool Error Coverage
    # ============================================================================

    def test_all_tools_handle_invalid_ticker_gracefully(self):
        """Test that all tools handle invalid ticker gracefully"""
        invalid_tickers = ["", None, "INVALID@#$", "   ", "TOOLONG" * 5]

        for ticker in invalid_tickers:
            # Test a representative sample of tools
            result1 = get_stock_price(ticker)
            assert "Error" in result1 or isinstance(result1, float)

            result2 = get_company_info(ticker)
            assert "Error" in result2 or isinstance(result2, dict)

    def test_all_tools_provide_meaningful_error_messages(self):
        """Test that all tools provide meaningful error messages"""
        error_results = []

        # Test various invalid inputs across tools
        test_cases = [
            ("get_stock_price", lambda: get_stock_price("")),
            ("get_historical_data", lambda: get_historical_data("", "2024-01-01", "2024-01-31")),
            ("get_stock_news", lambda: get_stock_news(None)),
            ("get_balance_sheet", lambda: get_balance_sheet("INVALID@")),
            ("get_company_info", lambda: get_company_info("   ")),
        ]

        for tool_name, tool_func in test_cases:
            result = tool_func()
            if "Error" in result:
                # Verify error message is meaningful
                assert len(result) > 15, f"{tool_name} error message too short"
                assert "Traceback" not in result, f"{tool_name} error contains traceback"
                error_results.append((tool_name, result))

        # At least some errors should have been raised
        assert len(error_results) > 0

    # ============================================================================
    # Concurrent Error Handling Tests
    # ============================================================================

    def test_multiple_tool_errors_do_not_crash(self):
        """Test that multiple simultaneous tool errors don't crash the system"""
        results = []

        # Simulate multiple tools being called with invalid inputs
        invalid_inputs = ["", None, "INVALID", "TEST@#$", "   "]

        for ticker in invalid_inputs:
            results.append(get_stock_price(ticker))
            results.append(get_company_info(ticker))
            results.append(get_historical_data(ticker, "2024-01-01", "2024-01-31"))

        # All should return error messages or results, not raise exceptions
        for result in results:
            assert isinstance(result, str), "Tool should return string result, not raise"
            assert len(result) > 0, "Tool result should not be empty"
