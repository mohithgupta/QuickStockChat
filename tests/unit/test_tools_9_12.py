"""
Unit tests for financial tools 9-12 (get_splits, get_institutional_holders, get_major_shareholders, get_mutual_fund_holders)

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
    get_splits_func as get_splits,
    get_institutional_holders_func as get_institutional_holders,
    get_major_shareholders_func as get_major_shareholders,
    get_mutual_fund_holders_func as get_mutual_fund_holders
)


class TestGetSplits:
    """Test suite for get_splits tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_valid_ticker(self, mock_ticker):
        """Test get_splits returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock Series with split data
        dates = pd.date_range(start='2020-01-01', periods=3, freq='Y')
        mock_series = pd.Series([4.0, 2.0, 1.0], index=dates)

        mock_stock.splits = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_splits("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_empty_series(self, mock_ticker):
        """Test get_splits handles empty Series"""
        # Setup mock
        mock_stock = Mock()
        mock_series = pd.Series(dtype=float)
        mock_stock.splits = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_splits("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_none_result(self, mock_ticker):
        """Test get_splits handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.splits = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_splits("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve stock splits" in str(exc_info.value)

    def test_get_splits_empty_string_ticker(self):
        """Test get_splits handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_splits("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_splits_none_ticker(self):
        """Test get_splits handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_splits(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_splits_non_string_ticker(self):
        """Test get_splits handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_splits(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_exception_handling(self, mock_ticker):
        """Test get_splits handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_splits("AAPL")

        # Verify
        assert "Failed to retrieve stock splits" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_multiple_tickers(self, mock_ticker):
        """Test get_splits works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        dates = pd.date_range(start='2020-01-01', periods=2, freq='Y')
        mock_series = pd.Series([4.0, 2.0], index=dates)
        mock_stock.splits = mock_series
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_splits(ticker)
            assert isinstance(result, dict)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_splits_no_split_company(self, mock_ticker):
        """Test get_splits for company that never had stock splits"""
        # Setup mock - empty series for company with no splits
        mock_stock = Mock()
        mock_series = pd.Series(dtype=float)
        mock_stock.splits = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_splits("TSLA")  # Tesla has had minimal splits

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0


class TestGetInstitutionalHolders:
    """Test suite for get_institutional_holders tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_valid_ticker(self, mock_ticker):
        """Test get_institutional_holders returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame with institutional holders data
        mock_df = pd.DataFrame({
            'Holder': ['Vanguard Group Inc', 'BlackRock Inc', 'State Street Corp'],
            'Shares': [1500000000, 1200000000, 800000000],
            'Date Reported': [pd.Timestamp('2024-03-31'), pd.Timestamp('2024-03-31'), pd.Timestamp('2024-03-31')],
            '% Out': [8.5, 6.8, 4.5],
            'Value': [250000000000, 200000000000, 135000000000]
        })

        mock_stock.institutional_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_institutional_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Holder' in result
        assert 'Shares' in result
        assert len(result['Holder']) == 3
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_empty_dataframe(self, mock_ticker):
        """Test get_institutional_holders handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.institutional_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_institutional_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_none_result(self, mock_ticker):
        """Test get_institutional_holders handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.institutional_holders = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_institutional_holders("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve institutional holders" in str(exc_info.value)

    def test_get_institutional_holders_empty_string_ticker(self):
        """Test get_institutional_holders handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_institutional_holders("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_institutional_holders_none_ticker(self):
        """Test get_institutional_holders handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_institutional_holders(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_institutional_holders_non_string_ticker(self):
        """Test get_institutional_holders handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_institutional_holders(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_exception_handling(self, mock_ticker):
        """Test get_institutional_holders handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_institutional_holders("AAPL")

        # Verify
        assert "Failed to retrieve institutional holders" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_multiple_tickers(self, mock_ticker):
        """Test get_institutional_holders works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Holder': ['Vanguard Group Inc'],
            'Shares': [1500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [8.5],
            'Value': [250000000000]
        })
        mock_stock.institutional_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_institutional_holders(ticker)
            assert isinstance(result, dict)
            assert 'Holder' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_institutional_holders_comprehensive_data(self, mock_ticker):
        """Test get_institutional_holders returns comprehensive holder data"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Holder': ['Vanguard Group Inc', 'BlackRock Inc', 'State Street Corp', 'Geode Capital Management', 'FMR LLC'],
            'Shares': [1500000000, 1200000000, 800000000, 500000000, 450000000],
            'Date Reported': [pd.Timestamp('2024-03-31')] * 5,
            '% Out': [8.5, 6.8, 4.5, 2.8, 2.5],
            'Value': [250000000000, 200000000000, 135000000000, 85000000000, 76000000000]
        })
        mock_stock.institutional_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_institutional_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['Holder']) == 5
        assert result['Shares'][0] == 1500000000
        assert result['% Out'][0] == 8.5


class TestGetMajorShareholders:
    """Test suite for get_major_shareholders tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_valid_ticker(self, mock_ticker):
        """Test get_major_shareholders returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock Series with major holders data
        mock_series = pd.Series([
            15.5,
            8.2,
            5.8,
            4.3,
            3.9,
            2.7
        ], index=[
            'Total Institutional Holdings',
            'Total Insider Holdings',
            'Total Mutual Fund Holdings',
            'Total Hedge Fund Holdings',
            'Total Other Institutional Holdings',
            'Total Government Holdings'
        ])

        mock_stock.major_holders = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_major_shareholders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        assert 'Total Institutional Holdings' in result
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_empty_series(self, mock_ticker):
        """Test get_major_shareholders handles empty Series"""
        # Setup mock
        mock_stock = Mock()
        mock_series = pd.Series(dtype=float)
        mock_stock.major_holders = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_major_shareholders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_none_result(self, mock_ticker):
        """Test get_major_shareholders handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.major_holders = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_major_shareholders("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve major share holders" in str(exc_info.value)

    def test_get_major_shareholders_empty_string_ticker(self):
        """Test get_major_shareholders handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_major_shareholders("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_major_shareholders_none_ticker(self):
        """Test get_major_shareholders handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_major_shareholders(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_major_shareholders_non_string_ticker(self):
        """Test get_major_shareholders handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_major_shareholders(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_exception_handling(self, mock_ticker):
        """Test get_major_shareholders handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_major_shareholders("AAPL")

        # Verify
        assert "Failed to retrieve major share holders" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_multiple_tickers(self, mock_ticker):
        """Test get_major_shareholders works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_series = pd.Series([15.5, 8.2], index=['Total Institutional Holdings', 'Total Insider Holdings'])
        mock_stock.major_holders = mock_series
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_major_shareholders(ticker)
            assert isinstance(result, dict)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_major_shareholders_comprehensive_data(self, mock_ticker):
        """Test get_major_shareholders returns comprehensive data"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_series = pd.Series([
            15.5,
            8.2,
            5.8,
            4.3,
            3.9,
            2.7,
            1.5,
            0.8
        ], index=[
            'Total Institutional Holdings',
            'Total Insider Holdings',
            'Total Mutual Fund Holdings',
            'Total Hedge Fund Holdings',
            'Total Other Institutional Holdings',
            'Total Government Holdings',
            'Total Private Holdings',
            'Total Public Holdings'
        ])
        mock_stock.major_holders = mock_series
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_major_shareholders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert result['Total Institutional Holdings'] == 15.5
        assert result['Total Insider Holdings'] == 8.2
        assert result['Total Mutual Fund Holdings'] == 5.8


class TestGetMutualFundHolders:
    """Test suite for get_mutual_fund_holders tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_valid_ticker(self, mock_ticker):
        """Test get_mutual_fund_holders returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame with mutual fund holders data
        mock_df = pd.DataFrame({
            'Holder': ['Vanguard Total Stock Market Index', 'Fidelity 500 Index', 'SPDR S&P 500 ETF Trust'],
            'Shares': [500000000, 450000000, 380000000],
            'Date Reported': [pd.Timestamp('2024-03-31'), pd.Timestamp('2024-03-31'), pd.Timestamp('2024-03-31')],
            '% Out': [2.8, 2.5, 2.1],
            'Value': [85000000000, 76000000000, 65000000000]
        })

        mock_stock.mutualfund_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_mutual_fund_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Holder' in result
        assert 'Shares' in result
        assert len(result['Holder']) == 3
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_empty_dataframe(self, mock_ticker):
        """Test get_mutual_fund_holders handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.mutualfund_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_mutual_fund_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_none_result(self, mock_ticker):
        """Test get_mutual_fund_holders handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.mutualfund_holders = None
        mock_ticker.return_value = mock_stock

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_mutual_fund_holders("AAPL")

        # Verify - should raise ExternalServiceError
        assert "Failed to retrieve mutual fund holders" in str(exc_info.value)

    def test_get_mutual_fund_holders_empty_string_ticker(self):
        """Test get_mutual_fund_holders handles empty ticker string"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_mutual_fund_holders("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_mutual_fund_holders_none_ticker(self):
        """Test get_mutual_fund_holders handles None ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_mutual_fund_holders(None)

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_get_mutual_fund_holders_non_string_ticker(self):
        """Test get_mutual_fund_holders handles non-string ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            get_mutual_fund_holders(123)

        assert "must be a string" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_exception_handling(self, mock_ticker):
        """Test get_mutual_fund_holders handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        with pytest.raises(ExternalServiceError) as exc_info:
            get_mutual_fund_holders("AAPL")

        # Verify
        assert "Failed to retrieve mutual fund holders" in str(exc_info.value)

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_multiple_tickers(self, mock_ticker):
        """Test get_mutual_fund_holders works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Holder': ['Vanguard Total Stock Market Index'],
            'Shares': [500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [2.8],
            'Value': [85000000000]
        })
        mock_stock.mutualfund_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_mutual_fund_holders(ticker)
            assert isinstance(result, dict)
            assert 'Holder' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_mutual_fund_holders_comprehensive_data(self, mock_ticker):
        """Test get_mutual_fund_holders returns comprehensive holder data"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Holder': [
                'Vanguard Total Stock Market Index',
                'Fidelity 500 Index',
                'SPDR S&P 500 ETF Trust',
                'iShares Core S&P 500 ETF',
                'American Funds Growth Fund'
            ],
            'Shares': [500000000, 450000000, 380000000, 320000000, 280000000],
            'Date Reported': [pd.Timestamp('2024-03-31')] * 5,
            '% Out': [2.8, 2.5, 2.1, 1.8, 1.6],
            'Value': [85000000000, 76000000000, 65000000000, 55000000000, 48000000000]
        })
        mock_stock.mutualfund_holders = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_mutual_fund_holders("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['Holder']) == 5
        assert result['Shares'][0] == 500000000
        assert result['% Out'][1] == 2.5


class TestToolsIntegration:
    """Integration tests for tools 9-12 working together"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_multiple_tools_9_12_same_ticker(self, mock_ticker):
        """Test calling multiple tools 9-12 with the same ticker"""
        # Setup mock
        mock_stock = Mock()

        # Mock all the data
        dates = pd.date_range(start='2020-01-01', periods=2, freq='Y')
        mock_stock.splits = pd.Series([4.0, 2.0], index=dates)

        mock_stock.institutional_holders = pd.DataFrame({
            'Holder': ['Vanguard Group Inc'],
            'Shares': [1500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [8.5],
            'Value': [250000000000]
        })

        mock_stock.major_holders = pd.Series([15.5, 8.2], index=['Total Institutional Holdings', 'Total Insider Holdings'])

        mock_stock.mutualfund_holders = pd.DataFrame({
            'Holder': ['Vanguard Total Stock Market Index'],
            'Shares': [500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [2.8],
            'Value': [85000000000]
        })

        mock_ticker.return_value = mock_stock

        # Call all tools
        splits = get_splits("AAPL")
        institutional_holders = get_institutional_holders("AAPL")
        major_shareholders = get_major_shareholders("AAPL")
        mutual_fund_holders = get_mutual_fund_holders("AAPL")

        # Verify all succeed
        assert isinstance(splits, dict)
        assert isinstance(institutional_holders, dict)
        assert 'Holder' in institutional_holders
        assert isinstance(major_shareholders, dict)
        assert 'Total Institutional Holdings' in major_shareholders
        assert isinstance(mutual_fund_holders, dict)
        assert 'Holder' in mutual_fund_holders

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_tools_9_12_with_invalid_tickers_dont_call_api(self, mock_ticker):
        """Test that invalid tickers don't make API calls for tools 9-12"""
        invalid_inputs = ["", None, 123, [], {}]

        for invalid_input in invalid_inputs:
            get_splits(invalid_input)
            get_institutional_holders(invalid_input)
            get_major_shareholders(invalid_input)
            get_mutual_fund_holders(invalid_input)

        # Verify yf.Ticker was never called
        assert mock_ticker.call_count == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_all_tools_1_12_integration(self, mock_ticker):
        """Test integration of tools 1-8 and 9-12 together"""
        from ..conftest import (
            get_stock_price_func as get_stock_price,
            get_historical_data_func as get_historical_data,
            get_stock_news_func as get_stock_news,
            get_balance_sheet_func as get_balance_sheet,
            get_income_statement_func as get_income_statement,
            get_cash_flow_func as get_cash_flow,
            get_company_info_func as get_company_info,
            get_dividends_func as get_dividends
        )

        # Setup mock
        mock_stock = Mock()

        # Mock all data for all tools
        mock_stock.info = {
            'regularMarketPrice': 150.25,
            'companyName': 'Apple Inc.'
        }
        mock_stock.news = [{'title': 'Test news'}]
        mock_stock.balance_sheet = pd.DataFrame({'Total Assets': [1000000]})
        mock_stock.financials = pd.DataFrame({'Total Revenue': [1000000]})
        mock_stock.cashflow = pd.DataFrame({'Operating Cash Flow': [500000]})

        dates = pd.date_range(start='2024-01-01', end='2024-01-05', freq='D')
        mock_stock.history.return_value = pd.DataFrame({
            'Open': [148.0],
            'Close': [148.5]
        }, index=dates)

        split_dates = pd.date_range(start='2020-01-01', periods=2, freq='Y')
        mock_stock.splits = pd.Series([4.0, 2.0], index=split_dates)

        mock_stock.dividends = pd.Series([0.24], index=pd.DatetimeIndex(['2024-01-01']))

        mock_stock.institutional_holders = pd.DataFrame({
            'Holder': ['Vanguard Group Inc'],
            'Shares': [1500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [8.5],
            'Value': [250000000000]
        })

        mock_stock.major_holders = pd.Series([15.5, 8.2], index=['Total Institutional Holdings', 'Total Insider Holdings'])

        mock_stock.mutualfund_holders = pd.DataFrame({
            'Holder': ['Vanguard Total Stock Market Index'],
            'Shares': [500000000],
            'Date Reported': [pd.Timestamp('2024-03-31')],
            '% Out': [2.8],
            'Value': [85000000000]
        })

        mock_ticker.return_value = mock_stock

        # Call all tools 1-12
        price = get_stock_price("AAPL")
        historical = get_historical_data("AAPL", "2024-01-01", "2024-01-05")
        news = get_stock_news("AAPL")
        balance_sheet = get_balance_sheet("AAPL")
        income_statement = get_income_statement("AAPL")
        cash_flow = get_cash_flow("AAPL")
        company_info = get_company_info("AAPL")
        dividends = get_dividends("AAPL")
        splits = get_splits("AAPL")
        institutional_holders = get_institutional_holders("AAPL")
        major_shareholders = get_major_shareholders("AAPL")
        mutual_fund_holders = get_mutual_fund_holders("AAPL")

        # Verify all succeed
        assert price == 150.25
        assert isinstance(historical, dict)
        assert len(news) == 1
        assert isinstance(balance_sheet, dict)
        assert isinstance(income_statement, dict)
        assert isinstance(cash_flow, dict)
        assert isinstance(company_info, dict)
        assert isinstance(dividends, dict)
        assert isinstance(splits, dict)
        assert isinstance(institutional_holders, dict)
        assert isinstance(major_shareholders, dict)
        assert isinstance(mutual_fund_holders, dict)
