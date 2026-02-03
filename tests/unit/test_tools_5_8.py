"""
Unit tests for financial tools 5-8 (get_income_statement, get_cash_flow, get_company_info, get_dividends)

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
from MarketInsight.utils.exceptions import TickerValidationError, ExternalServiceError

# Import the raw functions from conftest which unwraps the StructuredTool decorator
from ..conftest import (
    get_income_statement_func as get_income_statement,
    get_cash_flow_func as get_cash_flow,
    get_company_info_func as get_company_info,
    get_dividends_func as get_dividends
)


class TestGetIncomeStatement:
    """Test suite for get_income_statement tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_income_statement_valid_ticker(self, mock_ticker):
        """Test get_income_statement returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'Total Revenue': [1000000, 1100000],
            'Net Income': [100000, 120000]
        })

        mock_stock.financials = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_income_statement("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Total Revenue' in result
        assert 'Net Income' in result
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_income_statement_empty_dataframe(self, mock_ticker):
        """Test get_income_statement handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.financials = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_income_statement("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_income_statement_none_result(self, mock_ticker):
        """Test get_income_statement handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.financials = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_income_statement("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve income statement" in str(exc_info.value)

    def test_get_income_statement_empty_string_ticker(self):
        """Test get_income_statement handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_income_statement("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_income_statement_none_ticker(self):
        """Test get_income_statement handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_income_statement(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_income_statement_non_string_ticker(self):
        """Test get_income_statement handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_income_statement(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_income_statement_exception_handling(self, mock_ticker):
        """Test get_income_statement handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_income_statement("AAPL")

        # Verify
        assert "Failed to retrieve income statement" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_income_statement_multiple_tickers(self, mock_ticker):
        """Test get_income_statement works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({'Total Revenue': [1000000]})
        mock_stock.financials = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_income_statement(ticker)
            assert isinstance(result, dict)
            assert 'Total Revenue' in result


class TestGetCashFlow:
    """Test suite for get_cash_flow tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_cash_flow_valid_ticker(self, mock_ticker):
        """Test get_cash_flow returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'Operating Cash Flow': [500000, 550000],
            'Capital Expenditure': [-100000, -120000]
        })

        mock_stock.cashflow = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_cash_flow("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Operating Cash Flow' in result
        assert 'Capital Expenditure' in result
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_cash_flow_empty_dataframe(self, mock_ticker):
        """Test get_cash_flow handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.cashflow = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_cash_flow("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_cash_flow_none_result(self, mock_ticker):
        """Test get_cash_flow handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.cashflow = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_cash_flow("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve cash flow" in str(exc_info.value)

    def test_get_cash_flow_empty_string_ticker(self):
        """Test get_cash_flow handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_cash_flow("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_cash_flow_none_ticker(self):
        """Test get_cash_flow handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_cash_flow(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_cash_flow_non_string_ticker(self):
        """Test get_cash_flow handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_cash_flow(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_cash_flow_exception_handling(self, mock_ticker):
        """Test get_cash_flow handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_cash_flow("AAPL")

        # Verify
        assert "Failed to retrieve cash flow" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_cash_flow_multiple_tickers(self, mock_ticker):
        """Test get_cash_flow works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({'Operating Cash Flow': [500000]})
        mock_stock.cashflow = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_cash_flow(ticker)
            assert isinstance(result, dict)
            assert 'Operating Cash Flow' in result


class TestGetCompanyInfo:
    """Test suite for get_company_info tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_valid_ticker(self, mock_ticker):
        """Test get_company_info returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()
        mock_info = {
            'companyName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'marketCap': 2500000000000,
            'peRatio': 25.5
        }
        mock_stock.info = mock_info
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_company_info("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert result['companyName'] == 'Apple Inc.'
        assert result['sector'] == 'Technology'
        assert result['peRatio'] == 25.5
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_empty_dict(self, mock_ticker):
        """Test get_company_info handles empty dictionary"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = {}
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_company_info("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_none_result(self, mock_ticker):
        """Test get_company_info handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.info = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_company_info("AAPL")

        # Verify
        assert "No data available" in str(exc_info.value)

    def test_get_company_info_empty_string_ticker(self):
        """Test get_company_info handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_company_info("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_company_info_none_ticker(self):
        """Test get_company_info handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_company_info(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_company_info_non_string_ticker(self):
        """Test get_company_info handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_company_info(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_exception_handling(self, mock_ticker):
        """Test get_company_info handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_company_info("AAPL")

        # Verify
        assert "Failed to retrieve company info" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_multiple_tickers(self, mock_ticker):
        """Test get_company_info works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_info = {'companyName': 'Test Company', 'sector': 'Technology'}
        mock_stock.info = mock_info
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_company_info(ticker)
            assert isinstance(result, dict)
            assert 'companyName' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_company_info_comprehensive_data(self, mock_ticker):
        """Test get_company_info returns comprehensive company data"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_info = {
            'companyName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'marketCap': 2500000000000,
            'peRatio': 25.5,
            'pbRatio': 35.2,
            'dividendYield': 0.5,
            'beta': 1.2,
            'eps': 6.05,
            'revenueGrowth': 8.5
        }
        mock_stock.info = mock_info
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_company_info("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert result['marketCap'] == 2500000000000
        assert result['peRatio'] == 25.5
        assert result['beta'] == 1.2
        assert result['revenueGrowth'] == 8.5


class TestGetDividends:
    """Test suite for get_dividends tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_valid_ticker(self, mock_ticker):
        """Test get_dividends returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock Series with dividend data
        dates = pd.date_range(start='2024-01-01', periods=4, freq='Q')
        mock_series = pd.Series([0.24, 0.24, 0.24, 0.24], index=dates)

        mock_stock.dividends = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_dividends("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_empty_series(self, mock_ticker):
        """Test get_dividends handles empty Series"""
        # Setup mock
        mock_stock = Mock()
        mock_series = pd.Series(dtype=float)
        mock_stock.dividends = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_dividends("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_none_result(self, mock_ticker):
        """Test get_dividends handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.dividends = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_dividends("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve dividends" in str(exc_info.value)

    def test_get_dividends_empty_string_ticker(self):
        """Test get_dividends handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_dividends("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_dividends_none_ticker(self):
        """Test get_dividends handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_dividends(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_dividends_non_string_ticker(self):
        """Test get_dividends handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_dividends(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_exception_handling(self, mock_ticker):
        """Test get_dividends handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_dividends("AAPL")

        # Verify
        assert "Failed to retrieve dividends" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_multiple_tickers(self, mock_ticker):
        """Test get_dividends works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        dates = pd.date_range(start='2024-01-01', periods=2, freq='Q')
        mock_series = pd.Series([0.24, 0.24], index=dates)
        mock_stock.dividends = mock_series
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_dividends(ticker)
            assert isinstance(result, dict)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_dividends_no_dividend_company(self, mock_ticker):
        """Test get_dividends for company that doesn't pay dividends"""
        # Setup mock - empty series for non-dividend paying company
        mock_stock = Mock()
        mock_series = pd.Series(dtype=float)
        mock_stock.dividends = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_dividends("AMZN")  # Amazon doesn't pay dividends

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0


class TestToolsIntegration:
    """Integration tests for tools 5-8 working together"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_multiple_tools_5_8_same_ticker(self, mock_ticker):
        """Test calling multiple tools 5-8 with the same ticker"""
        # Setup mock
        mock_stock = Mock()

        # Mock all the data
        mock_stock.financials = pd.DataFrame({'Total Revenue': [1000000]})
        mock_stock.cashflow = pd.DataFrame({'Operating Cash Flow': [500000]})
        mock_stock.info = {'companyName': 'Apple Inc.', 'sector': 'Technology'}
        mock_stock.dividends = pd.Series([0.24], index=pd.DatetimeIndex(['2024-01-01']))

        mock_ticker.return_value = mock_stock

        # Call all tools
        income_statement = get_income_statement("AAPL")
        cash_flow = get_cash_flow("AAPL")
        company_info = get_company_info("AAPL")
        dividends = get_dividends("AAPL")

        # Verify all succeed
        assert isinstance(income_statement, dict)
        assert 'Total Revenue' in income_statement
        assert isinstance(cash_flow, dict)
        assert 'Operating Cash Flow' in cash_flow
        assert isinstance(company_info, dict)
        assert company_info['companyName'] == 'Apple Inc.'
        assert isinstance(dividends, dict)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_tools_5_8_with_invalid_tickers_dont_call_api(self, mock_ticker):
        """Test that invalid tickers don't make API calls for tools 5-8"""
        invalid_inputs = ["", None, 123, [], {}]

        for invalid_input in invalid_inputs:
            get_income_statement(invalid_input)
            get_cash_flow(invalid_input)
            get_company_info(invalid_input)
            get_dividends(invalid_input)

        # Verify yf.Ticker was never called
        assert mock_ticker.call_count == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_all_tools_1_8_integration(self, mock_ticker):
        """Test integration of tools 1-4 and 5-8 together"""
        from ..conftest import (
            get_stock_price_func as get_stock_price,
            get_historical_data_func as get_historical_data,
            get_stock_news_func as get_stock_news,
            get_balance_sheet_func as get_balance_sheet
        )

        # Setup mock
        mock_stock = Mock()

        # Mock all data for all tools
        mock_stock.info = {'regularMarketPrice': 150.25, 'companyName': 'Apple Inc.'}
        mock_stock.news = [{'title': 'Test news'}]
        mock_stock.balance_sheet = pd.DataFrame({'Total Assets': [1000000]})
        mock_stock.financials = pd.DataFrame({'Total Revenue': [1000000]})

        dates = pd.date_range(start='2024-01-01', end='2024-01-05', freq='D')
        mock_stock.history.return_value = pd.DataFrame({
            'Open': [148.0],
            'Close': [148.5]
        }, index=dates)

        mock_stock.cashflow = pd.DataFrame({'Operating Cash Flow': [500000]})
        mock_stock.dividends = pd.Series([0.24], index=pd.DatetimeIndex(['2024-01-01']))

        mock_ticker.return_value = mock_stock

        # Call all tools
        price = get_stock_price("AAPL")
        historical = get_historical_data("AAPL", "2024-01-01", "2024-01-05")
        news = get_stock_news("AAPL")
        balance_sheet = get_balance_sheet("AAPL")
        income_statement = get_income_statement("AAPL")
        cash_flow = get_cash_flow("AAPL")
        company_info = get_company_info("AAPL")
        dividends = get_dividends("AAPL")

        # Verify all succeed
        assert price == 150.25
        assert isinstance(historical, dict)
        assert len(news) == 1
        assert isinstance(balance_sheet, dict)
        assert isinstance(income_statement, dict)
        assert isinstance(cash_flow, dict)
        assert isinstance(company_info, dict)
        assert isinstance(dividends, dict)
