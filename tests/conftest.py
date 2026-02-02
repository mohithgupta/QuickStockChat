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
