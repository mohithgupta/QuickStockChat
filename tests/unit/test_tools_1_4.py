"""
Unit tests for financial tools 1-4 (get_stock_price, get_historical_data, get_stock_news, get_balance_sheet)

Tests cover:
- Valid input handling
- Invalid input handling
- Error handling and edge cases
- Return value validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Import the raw functions from conftest which unwraps the StructuredTool decorator
from ..conftest import (
    get_stock_price_func as get_stock_price,
    get_historical_data_func as get_historical_data,
    get_stock_news_func as get_stock_news,
    get_balance_sheet_func as get_balance_sheet
)


class TestGetStockPrice:
    """Test suite for get_stock_price tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_price_valid_ticker(self, mock_ticker):
        """Test get_stock_price returns correct price for valid ticker"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = {'regularMarketPrice': 150.25}
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_price("AAPL")

        # Verify
        assert result == 150.25
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_price_none_price(self, mock_ticker):
        """Test get_stock_price handles None price data"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = {'regularMarketPrice': None}
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_price("AAPL")

        # Verify
        assert result == "No price data available for {ticker}"

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_price_missing_key(self, mock_ticker):
        """Test get_stock_price handles missing regularMarketPrice key"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = {}  # Missing regularMarketPrice
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_price("AAPL")

        # Verify - should raise KeyError and return error message
        assert result == "Error: Failed to retrieve stock price. Please try again later."

    def test_get_stock_price_empty_string(self):
        """Test get_stock_price handles empty string"""
        result = get_stock_price("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_stock_price_none_ticker(self):
        """Test get_stock_price handles None ticker"""
        result = get_stock_price(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_stock_price_non_string_ticker(self):
        """Test get_stock_price handles non-string ticker"""
        result = get_stock_price(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_price_exception_handling(self, mock_ticker):
        """Test get_stock_price handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_stock_price("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve stock price. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_price_different_tickers(self, mock_ticker):
        """Test get_stock_price works with different ticker symbols"""
        # Setup mock
        mock_stock = Mock()

        def get_info():
            return {'regularMarketPrice': 150.25}

        mock_stock.info = get_info()
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        for ticker in tickers:
            result = get_stock_price(ticker)
            assert result == 150.25


class TestGetHistoricalData:
    """Test suite for get_historical_data tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_historical_data_valid_inputs(self, mock_ticker):
        """Test get_historical_data returns data for valid inputs"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame
        dates = pd.date_range(start='2024-01-01', end='2024-01-05', freq='D')
        mock_df = pd.DataFrame({
            'Open': [148.0, 149.0, 150.0, 151.0, 152.0],
            'Close': [148.5, 149.5, 150.5, 151.5, 152.5]
        }, index=dates)

        mock_stock.history.return_value = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_historical_data("AAPL", "2024-01-01", "2024-01-05")

        # Verify
        assert isinstance(result, dict)
        assert 'Open' in result
        assert 'Close' in result
        mock_stock.history.assert_called_once_with(start="2024-01-01", end="2024-01-05")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_historical_data_empty_string_ticker(self, mock_ticker):
        """Test get_historical_data handles empty ticker string"""
        result = get_historical_data("", "2024-01-01", "2024-01-05")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."
        mock_ticker.assert_not_called()

    def test_get_historical_data_none_ticker(self):
        """Test get_historical_data handles None ticker"""
        result = get_historical_data(None, "2024-01-01", "2024-01-05")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_historical_data_non_string_ticker(self):
        """Test get_historical_data handles non-string ticker"""
        result = get_historical_data(123, "2024-01-01", "2024-01-05")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_historical_data_exception_handling(self, mock_ticker):
        """Test get_historical_data handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_historical_data("AAPL", "2024-01-01", "2024-01-05")

        # Verify
        assert result == "Error: Failed to retrieve historical data. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_historical_data_none_result(self, mock_ticker):
        """Test get_historical_data handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.history.return_value = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_historical_data("AAPL", "2024-01-01", "2024-01-05")

        # Verify
        assert result == "No historical data available for {ticker}"

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_historical_data_various_date_ranges(self, mock_ticker):
        """Test get_historical_data with different date ranges"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({'Close': [150.0]})
        mock_stock.history.return_value = mock_df
        mock_ticker.return_value = mock_stock

        # Test different date ranges
        test_cases = [
            ("2024-01-01", "2024-01-31"),
            ("2023-01-01", "2023-12-31"),
            ("2020-01-01", "2024-12-31")
        ]

        for start, end in test_cases:
            result = get_historical_data("AAPL", start, end)
            assert isinstance(result, dict)


class TestGetStockNews:
    """Test suite for get_stock_news tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_news_valid_ticker(self, mock_ticker):
        """Test get_stock_news returns news for valid ticker"""
        # Setup mock
        mock_stock = Mock()
        mock_news = [
            {'title': 'Apple announces new product', 'link': 'http://example.com/1'},
            {'title': 'AAPL stock surges', 'link': 'http://example.com/2'}
        ]
        mock_stock.news = mock_news
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_news("AAPL")

        # Verify
        assert result == mock_news
        assert len(result) == 2
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_news_empty_news_list(self, mock_ticker):
        """Test get_stock_news handles empty news list"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.news = []
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_news("AAPL")

        # Verify
        assert result == []

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_news_none_news(self, mock_ticker):
        """Test get_stock_news handles None news"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.news = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_stock_news("AAPL")

        # Verify
        assert result == "No news available for {ticker}"

    def test_get_stock_news_empty_string_ticker(self):
        """Test get_stock_news handles empty ticker string"""
        result = get_stock_news("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_stock_news_none_ticker(self):
        """Test get_stock_news handles None ticker"""
        result = get_stock_news(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_stock_news_non_string_ticker(self):
        """Test get_stock_news handles non-string ticker"""
        result = get_stock_news(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_news_exception_handling(self, mock_ticker):
        """Test get_stock_news handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_stock_news("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve news. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_stock_news_multiple_tickers(self, mock_ticker):
        """Test get_stock_news works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_news = [{'title': 'Test news'}]
        mock_stock.news = mock_news
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_stock_news(ticker)
            assert result == mock_news


class TestGetBalanceSheet:
    """Test suite for get_balance_sheet tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_balance_sheet_valid_ticker(self, mock_ticker):
        """Test get_balance_sheet returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'Total Assets': [1000000, 1100000],
            'Total Liabilities': [500000, 550000]
        })

        mock_stock.balance_sheet = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_balance_sheet("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Total Assets' in result
        assert 'Total Liabilities' in result
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_balance_sheet_empty_dataframe(self, mock_ticker):
        """Test get_balance_sheet handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.balance_sheet = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_balance_sheet("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_balance_sheet_none_result(self, mock_ticker):
        """Test get_balance_sheet handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.balance_sheet = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_balance_sheet("AAPL")

        # Verify - should raise AttributeError and return error message
        assert result == "Error: Failed to retrieve balance sheet. Please try again later."

    def test_get_balance_sheet_empty_string_ticker(self):
        """Test get_balance_sheet handles empty ticker string"""
        result = get_balance_sheet("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_balance_sheet_none_ticker(self):
        """Test get_balance_sheet handles None ticker"""
        result = get_balance_sheet(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_balance_sheet_non_string_ticker(self):
        """Test get_balance_sheet handles non-string ticker"""
        result = get_balance_sheet(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_balance_sheet_exception_handling(self, mock_ticker):
        """Test get_balance_sheet handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_balance_sheet("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve balance sheet. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_balance_sheet_multiple_tickers(self, mock_ticker):
        """Test get_balance_sheet works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({'Total Assets': [1000000]})
        mock_stock.balance_sheet = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_balance_sheet(ticker)
            assert isinstance(result, dict)
            assert 'Total Assets' in result


class TestToolsIntegration:
    """Integration tests for tools working together"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_multiple_tools_same_ticker(self, mock_ticker):
        """Test calling multiple tools with the same ticker"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = {'regularMarketPrice': 150.25}
        mock_stock.news = [{'title': 'Test news'}]
        mock_stock.balance_sheet = pd.DataFrame({'Total Assets': [1000000]})

        mock_ticker.return_value = mock_stock

        # Call all tools
        price = get_stock_price("AAPL")
        news = get_stock_news("AAPL")
        balance_sheet = get_balance_sheet("AAPL")

        # Verify all succeed
        assert price == 150.25
        assert len(news) == 1
        assert isinstance(balance_sheet, dict)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_tools_with_invalid_tickers_dont_call_api(self, mock_ticker):
        """Test that invalid tickers don't make API calls"""
        invalid_inputs = ["", None, 123, [], {}]

        for invalid_input in invalid_inputs:
            get_stock_price(invalid_input)
            get_historical_data(invalid_input, "2024-01-01", "2024-01-05")
            get_stock_news(invalid_input)
            get_balance_sheet(invalid_input)

        # Verify yf.Ticker was never called
        assert mock_ticker.call_count == 0
