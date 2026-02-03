"""
Unit tests for financial tools 13-16 (get_insider_transactions, get_analyst_recommendations, get_analyst_recommendations_summary, get_ticker)

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
import requests

# Import the raw functions from conftest which unwraps the StructuredTool decorator
from ..conftest import (
    get_insider_transactions_func as get_insider_transactions,
    get_analyst_recommendations_func as get_analyst_recommendations,
    get_analyst_recommendations_summary_func as get_analyst_recommendations_summary,
    get_ticker_func as get_ticker
)


class TestGetInsiderTransactions:
    """Test suite for get_insider_transactions tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_valid_ticker(self, mock_ticker):
        """Test get_insider_transactions returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame with insider transaction data
        mock_df = pd.DataFrame({
            'Start Date': [pd.Timestamp('2024-01-15'), pd.Timestamp('2024-02-20'), pd.Timestamp('2024-03-10')],
            'Insider': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'Trade': ['Sale', 'Purchase', 'Sale'],
            'Price': [150.25, 148.50, 152.30],
            'Quantity': [1000, 500, 750],
            'Owned': [50000, 45000, 42000],
            'Value': [150250, 74250, 114225]
        })

        mock_stock.insider_transactions = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Insider' in result
        assert 'Trade' in result
        assert len(result['Insider']) == 3
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_empty_dataframe(self, mock_ticker):
        """Test get_insider_transactions handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.insider_transactions = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_none_result(self, mock_ticker):
        """Test get_insider_transactions handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.insider_transactions = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify - should raise AttributeError and return error message
        assert result == "Error: Failed to retrieve insider transactions. Please try again later."

    def test_get_insider_transactions_empty_string_ticker(self):
        """Test get_insider_transactions handles empty ticker string"""
        result = get_insider_transactions("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_insider_transactions_none_ticker(self):
        """Test get_insider_transactions handles None ticker"""
        result = get_insider_transactions(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_insider_transactions_non_string_ticker(self):
        """Test get_insider_transactions handles non-string ticker"""
        result = get_insider_transactions(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_exception_handling(self, mock_ticker):
        """Test get_insider_transactions handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve insider transactions. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_multiple_tickers(self, mock_ticker):
        """Test get_insider_transactions works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Start Date': [pd.Timestamp('2024-01-15')],
            'Insider': ['John Doe'],
            'Trade': ['Sale'],
            'Price': [150.25],
            'Quantity': [1000],
            'Owned': [50000],
            'Value': [150250]
        })
        mock_stock.insider_transactions = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_insider_transactions(ticker)
            assert isinstance(result, dict)
            assert 'Insider' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_comprehensive_data(self, mock_ticker):
        """Test get_insider_transactions returns comprehensive transaction data"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Start Date': [
                pd.Timestamp('2024-01-15'),
                pd.Timestamp('2024-02-20'),
                pd.Timestamp('2024-03-10'),
                pd.Timestamp('2024-04-05'),
                pd.Timestamp('2024-05-12')
            ],
            'Insider': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown'],
            'Trade': ['Sale', 'Purchase', 'Sale', 'Sale', 'Purchase'],
            'Price': [150.25, 148.50, 152.30, 155.40, 153.80],
            'Quantity': [1000, 500, 750, 1200, 300],
            'Owned': [50000, 45000, 42000, 40800, 41100],
            'Value': [150250, 74250, 114225, 186480, 46140]
        })
        mock_stock.insider_transactions = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['Insider']) == 5
        assert result['Trade'][0] == 'Sale'
        assert result['Quantity'][2] == 750
        assert result['Value'][3] == 186480

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_insider_transactions_only_purchases(self, mock_ticker):
        """Test get_insider_transactions with only purchase transactions"""
        # Setup mock with only purchases
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Start Date': [pd.Timestamp('2024-01-15'), pd.Timestamp('2024-02-20')],
            'Insider': ['Jane Smith', 'Bob Johnson'],
            'Trade': ['Purchase', 'Purchase'],
            'Price': [148.50, 152.30],
            'Quantity': [500, 750],
            'Owned': [45000, 45750],
            'Value': [74250, 114225]
        })
        mock_stock.insider_transactions = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_insider_transactions("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['Trade']) == 2
        assert all(trade == 'Purchase' for trade in result['Trade'])


class TestGetAnalystRecommendations:
    """Test suite for get_analyst_recommendations tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_valid_ticker(self, mock_ticker):
        """Test get_analyst_recommendations returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame with analyst recommendations data
        mock_df = pd.DataFrame({
            'Firm': ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Bernstein'],
            'To Grade': ['Buy', 'Overweight', 'Neutral', 'Outperform'],
            'From Grade': ['Neutral', 'Equal Weight', 'Underweight', 'Market Perform'],
            'Action': ['Initiated', 'Upgraded', 'Downgraded', 'Reiterated'],
            'Date': [pd.Timestamp('2024-03-15'), pd.Timestamp('2024-03-10'), pd.Timestamp('2024-03-08'), pd.Timestamp('2024-03-05')]
        })

        mock_stock.recommendations = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'Firm' in result
        assert 'To Grade' in result
        assert len(result['Firm']) == 4
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_empty_dataframe(self, mock_ticker):
        """Test get_analyst_recommendations handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.recommendations = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_none_result(self, mock_ticker):
        """Test get_analyst_recommendations handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.recommendations = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify - should raise AttributeError and return error message
        assert result == "Error: Failed to retrieve analyst recommendations. Please try again later."

    def test_get_analyst_recommendations_empty_string_ticker(self):
        """Test get_analyst_recommendations handles empty ticker string"""
        result = get_analyst_recommendations("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_analyst_recommendations_none_ticker(self):
        """Test get_analyst_recommendations handles None ticker"""
        result = get_analyst_recommendations(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_analyst_recommendations_non_string_ticker(self):
        """Test get_analyst_recommendations handles non-string ticker"""
        result = get_analyst_recommendations(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_exception_handling(self, mock_ticker):
        """Test get_analyst_recommendations handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve analyst recommendations. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_multiple_tickers(self, mock_ticker):
        """Test get_analyst_recommendations works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Firm': ['Goldman Sachs'],
            'To Grade': ['Buy'],
            'From Grade': ['Neutral'],
            'Action': ['Initiated'],
            'Date': [pd.Timestamp('2024-03-15')]
        })
        mock_stock.recommendations = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_analyst_recommendations(ticker)
            assert isinstance(result, dict)
            assert 'Firm' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_comprehensive_data(self, mock_ticker):
        """Test get_analyst_recommendations returns comprehensive recommendations"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Firm': [
                'Goldman Sachs',
                'Morgan Stanley',
                'JP Morgan',
                'Bernstein',
                'Deutsche Bank',
                'Credit Suisse'
            ],
            'To Grade': ['Buy', 'Overweight', 'Neutral', 'Outperform', 'Buy', 'Outperform'],
            'From Grade': ['Neutral', 'Equal Weight', 'Underweight', 'Market Perform', 'Hold', 'Neutral'],
            'Action': ['Initiated', 'Upgraded', 'Downgraded', 'Reiterated', 'Upgraded', 'Initiated'],
            'Date': [
                pd.Timestamp('2024-03-15'),
                pd.Timestamp('2024-03-10'),
                pd.Timestamp('2024-03-08'),
                pd.Timestamp('2024-03-05'),
                pd.Timestamp('2024-03-01'),
                pd.Timestamp('2024-02-28')
            ]
        })
        mock_stock.recommendations = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['Firm']) == 6
        assert result['To Grade'][0] == 'Buy'
        assert result['Action'][1] == 'Upgraded'
        assert result['Firm'][2] == 'JP Morgan'

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_various_grades(self, mock_ticker):
        """Test get_analyst_recommendations with various recommendation grades"""
        # Setup mock with various grades
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'Firm': ['Firm A', 'Firm B', 'Firm C', 'Firm D', 'Firm E'],
            'To Grade': ['Strong Buy', 'Buy', 'Hold', 'Underweight', 'Sell'],
            'From Grade': ['Buy', 'Hold', 'Sell', 'Neutral', 'Underweight'],
            'Action': ['Upgraded', 'Initiated', 'Downgraded', 'Downgraded', 'Initiated'],
            'Date': [pd.Timestamp('2024-03-15')] * 5
        })
        mock_stock.recommendations = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result['To Grade']) == 5
        assert result['To Grade'][0] == 'Strong Buy'
        assert result['To Grade'][4] == 'Sell'


class TestGetAnalystRecommendationsSummary:
    """Test suite for get_analyst_recommendations_summary tool"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_valid_ticker(self, mock_ticker):
        """Test get_analyst_recommendations_summary returns data for valid ticker"""
        # Setup mock
        mock_stock = Mock()

        # Create a mock DataFrame with analyst recommendations summary data
        mock_df = pd.DataFrame({
            'current': [25, 18, 8, 3, 1],
            'previous': [24, 17, 9, 4, 1]
        }, index=['Buy', 'Overweight', 'Hold', 'Underweight', 'Sell'])

        mock_stock.recommendations_summary = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert 'current' in result
        assert 'previous' in result
        assert 'Buy' in result['current']
        mock_ticker.assert_called_once_with("AAPL")

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_empty_dataframe(self, mock_ticker):
        """Test get_analyst_recommendations_summary handles empty DataFrame"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame()
        mock_stock.recommendations_summary = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_none_result(self, mock_ticker):
        """Test get_analyst_recommendations_summary handles None result"""
        # Setup mock
        mock_stock = Mock()
        mock_stock.recommendations_summary = None
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify - should raise AttributeError and return error message
        assert result == "Error: Failed to retrieve analyst recommendations summary. Please try again later."

    def test_get_analyst_recommendations_summary_empty_string_ticker(self):
        """Test get_analyst_recommendations_summary handles empty ticker string"""
        result = get_analyst_recommendations_summary("")

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_analyst_recommendations_summary_none_ticker(self):
        """Test get_analyst_recommendations_summary handles None ticker"""
        result = get_analyst_recommendations_summary(None)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    def test_get_analyst_recommendations_summary_non_string_ticker(self):
        """Test get_analyst_recommendations_summary handles non-string ticker"""
        result = get_analyst_recommendations_summary(123)

        assert result == "Error: Invalid ticker provided. Please provide a valid ticker symbol."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_exception_handling(self, mock_ticker):
        """Test get_analyst_recommendations_summary handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_ticker.side_effect = Exception("Network error")

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify
        assert result == "Error: Failed to retrieve analyst recommendations summary. Please try again later."

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_multiple_tickers(self, mock_ticker):
        """Test get_analyst_recommendations_summary works with different tickers"""
        # Setup mock
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'current': [25, 18],
            'previous': [24, 17]
        }, index=['Buy', 'Overweight'])
        mock_stock.recommendations_summary = mock_df
        mock_ticker.return_value = mock_stock

        # Test multiple tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        for ticker in tickers:
            result = get_analyst_recommendations_summary(ticker)
            assert isinstance(result, dict)
            assert 'current' in result

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_comprehensive_data(self, mock_ticker):
        """Test get_analyst_recommendations_summary returns comprehensive summary"""
        # Setup mock with comprehensive data
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'current': [25, 18, 8, 3, 1],
            '1 month ago': [24, 17, 9, 4, 1],
            '2 months ago': [23, 18, 10, 3, 2],
            '3 months ago': [22, 19, 11, 2, 2]
        }, index=['Buy', 'Overweight', 'Hold', 'Underweight', 'Sell'])
        mock_stock.recommendations_summary = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert result['current']['Buy'] == 25
        assert result['current']['Overweight'] == 18
        assert result['current']['Hold'] == 8
        assert result['1 month ago']['Buy'] == 24

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_get_analyst_recommendations_summary_strong_buy_consensus(self, mock_ticker):
        """Test get_analyst_recommendations_summary with strong buy consensus"""
        # Setup mock with strong buy consensus
        mock_stock = Mock()
        mock_df = pd.DataFrame({
            'current': [30, 10, 2, 0, 0],
            'previous': [28, 12, 3, 0, 0]
        }, index=['Buy', 'Overweight', 'Hold', 'Underweight', 'Sell'])
        mock_stock.recommendations_summary = mock_df
        mock_ticker.return_value = mock_stock

        # Execute
        result = get_analyst_recommendations_summary("AAPL")

        # Verify
        assert isinstance(result, dict)
        assert result['current']['Buy'] == 30
        assert result['current']['Sell'] == 0
        assert result['current']['Underweight'] == 0


class TestGetTicker:
    """Test suite for get_ticker tool"""

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_valid_company_name(self, mock_get):
        """Test get_ticker returns ticker for valid company name"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {'symbol': 'AAPL', 'shortname': 'Apple Inc.', 'index': 'quotes'},
                {'symbol': 'AAPL.SW', 'shortname': 'Apple Inc.', 'index': 'quotes'}
            ]
        }
        mock_get.return_value = mock_response

        # Execute
        result = get_ticker("Apple")

        # Verify
        assert result == 'AAPL'
        mock_get.assert_called_once()

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_full_company_name(self, mock_get):
        """Test get_ticker with full company name"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {'symbol': 'MSFT', 'shortname': 'Microsoft Corporation', 'index': 'quotes'}
            ]
        }
        mock_get.return_value = mock_response

        # Execute
        result = get_ticker("Microsoft Corporation")

        # Verify
        assert result == 'MSFT'

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_multiple_company_names(self, mock_get):
        """Test get_ticker with various company names"""
        # Setup mock responses for different companies
        companies = [
            ("Apple", "AAPL"),
            ("Microsoft", "MSFT"),
            ("Google", "GOOGL"),
            ("Amazon", "AMZN")
        ]

        for company, expected_ticker in companies:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'quotes': [
                    {'symbol': expected_ticker, 'shortname': company, 'index': 'quotes'}
                ]
            }
            mock_get.return_value = mock_response

            # Execute
            result = get_ticker(company)

            # Verify
            assert result == expected_ticker

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_empty_quotes_list(self, mock_get):
        """Test get_ticker handles empty quotes list"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': []
        }
        mock_get.return_value = mock_response

        # Execute
        result = get_ticker("Unknown Company")

        # Verify - should raise IndexError and return error message
        assert result == "Error: Failed to retrieve ticker. Please try again later."

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_non_200_status(self, mock_get):
        """Test get_ticker handles non-200 status code"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Execute
        result = get_ticker("Unknown Company")

        # Verify
        assert result == "Error: Failed to retrieve ticker. Please try again later."

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_exception_handling(self, mock_get):
        """Test get_ticker handles exceptions gracefully"""
        # Setup mock to raise exception
        mock_get.side_effect = Exception("Network error")

        # Execute
        result = get_ticker("Apple")

        # Verify
        assert result == "Error: Failed to retrieve ticker. Please try again later."

    def test_get_ticker_empty_string_company_name(self):
        """Test get_ticker handles empty company name string"""
        result = get_ticker("")

        assert result == "Error: Invalid company name provided. Please provide a valid company name."

    def test_get_ticker_none_company_name(self):
        """Test get_ticker handles None company name"""
        result = get_ticker(None)

        assert result == "Error: Invalid company name provided. Please provide a valid company name."

    def test_get_ticker_non_string_company_name(self):
        """Test get_ticker handles non-string company name"""
        result = get_ticker(123)

        assert result == "Error: Invalid company name provided. Please provide a valid company name."

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_request_timeout(self, mock_get):
        """Test get_ticker handles request timeout"""
        # Setup mock to raise timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        # Execute
        result = get_ticker("Apple")

        # Verify
        assert result == "Error: Failed to retrieve ticker. Please try again later."

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_network_error(self, mock_get):
        """Test get_ticker handles network error"""
        # Setup mock to raise connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        # Execute
        result = get_ticker("Apple")

        # Verify
        assert result == "Error: Failed to retrieve ticker. Please try again later."

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_case_insensitive(self, mock_get):
        """Test get_ticker is case insensitive"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {'symbol': 'AAPL', 'shortname': 'Apple Inc.', 'index': 'quotes'}
            ]
        }
        mock_get.return_value = mock_response

        # Test various cases
        for name in ["apple", "APPLE", "Apple", "ApPlE"]:
            result = get_ticker(name)
            assert result == 'AAPL'

    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_with_spaces(self, mock_get):
        """Test get_ticker handles company names with spaces"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {'symbol': 'BRK-A', 'shortname': 'Berkshire Hathaway Inc.', 'index': 'quotes'}
            ]
        }
        mock_get.return_value = mock_response

        # Execute
        result = get_ticker("Berkshire Hathaway")

        # Verify
        assert result == 'BRK-A'


class TestToolsIntegration:
    """Integration tests for tools 13-16 working together"""

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_multiple_tools_13_15_same_ticker(self, mock_ticker):
        """Test calling multiple tools 13-15 with the same ticker"""
        # Setup mock
        mock_stock = Mock()

        # Mock all the data
        mock_stock.insider_transactions = pd.DataFrame({
            'Start Date': [pd.Timestamp('2024-01-15')],
            'Insider': ['John Doe'],
            'Trade': ['Sale'],
            'Price': [150.25],
            'Quantity': [1000],
            'Owned': [50000],
            'Value': [150250]
        })

        mock_stock.recommendations = pd.DataFrame({
            'Firm': ['Goldman Sachs'],
            'To Grade': ['Buy'],
            'From Grade': ['Neutral'],
            'Action': ['Initiated'],
            'Date': [pd.Timestamp('2024-03-15')]
        })

        mock_stock.recommendations_summary = pd.DataFrame({
            'current': [25, 18],
            'previous': [24, 17]
        }, index=['Buy', 'Overweight'])

        mock_ticker.return_value = mock_stock

        # Call all tools
        insider_transactions = get_insider_transactions("AAPL")
        analyst_recommendations = get_analyst_recommendations("AAPL")
        analyst_recommendations_summary = get_analyst_recommendations_summary("AAPL")

        # Verify all succeed
        assert isinstance(insider_transactions, dict)
        assert 'Insider' in insider_transactions
        assert isinstance(analyst_recommendations, dict)
        assert 'Firm' in analyst_recommendations
        assert isinstance(analyst_recommendations_summary, dict)
        assert 'current' in analyst_recommendations_summary

    @patch('MarketInsight.utils.tools.yf.Ticker')
    @patch('MarketInsight.utils.tools.requests.get')
    def test_get_ticker_and_use_with_other_tools(self, mock_get, mock_ticker):
        """Test using get_ticker result with other tools"""
        # Setup get_ticker mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {'symbol': 'AAPL', 'shortname': 'Apple Inc.', 'index': 'quotes'}
            ]
        }
        mock_get.return_value = mock_response

        # Setup other tools mock
        mock_stock = Mock()
        mock_stock.insider_transactions = pd.DataFrame({
            'Start Date': [pd.Timestamp('2024-01-15')],
            'Insider': ['John Doe'],
            'Trade': ['Sale'],
            'Price': [150.25],
            'Quantity': [1000],
            'Owned': [50000],
            'Value': [150250]
        })
        mock_ticker.return_value = mock_stock

        # Get ticker first
        ticker = get_ticker("Apple")
        assert ticker == 'AAPL'

        # Use ticker with other tools
        insider_transactions = get_insider_transactions(ticker)
        assert isinstance(insider_transactions, dict)
        assert 'Insider' in insider_transactions

    @patch('MarketInsight.utils.tools.yf.Ticker')
    def test_tools_13_15_with_invalid_tickers_dont_call_api(self, mock_ticker):
        """Test that invalid tickers don't make API calls for tools 13-15"""
        invalid_inputs = ["", None, 123, [], {}]

        for invalid_input in invalid_inputs:
            get_insider_transactions(invalid_input)
            get_analyst_recommendations(invalid_input)
            get_analyst_recommendations_summary(invalid_input)

        # Verify yf.Ticker was never called
        assert mock_ticker.call_count == 0
