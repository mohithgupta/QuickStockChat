"""
Pytest configuration and shared fixtures for all tests

This file contains common test fixtures and configuration
used across unit, integration, and e2e tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set a dummy OPENAI_API_KEY for tests that import modules requiring it
# This is needed because some modules (like agent.py) initialize ChatOpenAI
# at import time. The tests themselves mock the API calls, so this key
# is never actually used to make real requests.
os.environ.setdefault('OPENAI_API_KEY', 'test-dummy-key-for-testing')

# Import all tools and create fixtures for their underlying functions
# The @tool decorator wraps functions as StructuredTool objects, so we need to
# access the .func attribute to get the raw function for unit testing
from MarketInsight.utils.tools import (
    get_stock_price, get_historical_data, get_stock_news, get_balance_sheet,
    get_income_statement, get_cash_flow, get_company_info, get_dividends,
    get_splits, get_institutional_holders, get_major_shareholders,
    get_mutual_fund_holders, get_insider_transactions,
    get_analyst_recommendations, get_analyst_recommendations_summary, get_ticker
)

# Store the raw functions for tests
get_stock_price_func = get_stock_price.func if hasattr(get_stock_price, 'func') else get_stock_price
get_historical_data_func = get_historical_data.func if hasattr(get_historical_data, 'func') else get_historical_data
get_stock_news_func = get_stock_news.func if hasattr(get_stock_news, 'func') else get_stock_news
get_balance_sheet_func = get_balance_sheet.func if hasattr(get_balance_sheet, 'func') else get_balance_sheet
get_income_statement_func = get_income_statement.func if hasattr(get_income_statement, 'func') else get_income_statement
get_cash_flow_func = get_cash_flow.func if hasattr(get_cash_flow, 'func') else get_cash_flow
get_company_info_func = get_company_info.func if hasattr(get_company_info, 'func') else get_company_info
get_dividends_func = get_dividends.func if hasattr(get_dividends, 'func') else get_dividends
get_splits_func = get_splits.func if hasattr(get_splits, 'func') else get_splits
get_institutional_holders_func = get_institutional_holders.func if hasattr(get_institutional_holders, 'func') else get_institutional_holders
get_major_shareholders_func = get_major_shareholders.func if hasattr(get_major_shareholders, 'func') else get_major_shareholders
get_mutual_fund_holders_func = get_mutual_fund_holders.func if hasattr(get_mutual_fund_holders, 'func') else get_mutual_fund_holders
get_insider_transactions_func = get_insider_transactions.func if hasattr(get_insider_transactions, 'func') else get_insider_transactions
get_analyst_recommendations_func = get_analyst_recommendations.func if hasattr(get_analyst_recommendations, 'func') else get_analyst_recommendations
get_analyst_recommendations_summary_func = get_analyst_recommendations_summary.func if hasattr(get_analyst_recommendations_summary, 'func') else get_analyst_recommendations_summary
get_ticker_func = get_ticker.func if hasattr(get_ticker, 'func') else get_ticker


@pytest.fixture
def sample_ticker():
    """Provide a sample stock ticker for testing"""
    return "AAPL"


@pytest.fixture
def sample_thread_id():
    """Provide a sample thread ID for testing"""
    return "test-thread-123"


@pytest.fixture
def sample_response_id():
    """Provide a sample response ID for testing"""
    return "test-response-456"


@pytest.fixture
def sample_prompt():
    """Provide a sample prompt object for testing"""
    from config.config import PromptObject
    return PromptObject(
        content="What is the stock price of AAPL?",
        id="msg-1",
        role="user"
    )


@pytest.fixture
def sample_request(sample_prompt, sample_thread_id, sample_response_id):
    """Provide a sample request object for testing"""
    from config.config import RequestObject
    return RequestObject(
        prompt=sample_prompt,
        threadId=sample_thread_id,
        responseId=sample_response_id
    )


@pytest.fixture
def mock_stock_data():
    """Provide mock stock data for testing"""
    return {
        "regularMarketPrice": 150.25,
        "previousClose": 148.50,
        "marketCap": 2500000000000,
        "volume": 50000000
    }


@pytest.fixture
def mock_historical_data():
    """Provide mock historical data for testing"""
    import pandas as pd
    from datetime import datetime, timedelta

    dates = pd.date_range(
        start=datetime.now() - timedelta(days=5),
        end=datetime.now(),
        freq='D'
    )

    return pd.DataFrame({
        'Open': [148.0, 149.0, 150.0, 151.0, 152.0],
        'High': [149.0, 150.0, 151.0, 152.0, 153.0],
        'Low': [147.0, 148.0, 149.0, 150.0, 151.0],
        'Close': [148.5, 149.5, 150.5, 151.5, 152.5],
        'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
    }, index=dates)
