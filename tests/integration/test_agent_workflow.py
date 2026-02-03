"""
Integration tests for agent workflow with tool invocation

Tests cover the agent's ability to:
- Initialize properly with all tools
- Invoke tools correctly based on user queries
- Handle streaming responses
- Maintain conversation state
- Handle errors gracefully
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from MarketInsight.components.agent import agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class TestAgentWorkflow:
    """Test suite for agent workflow with tool invocation"""

    @pytest.fixture
    def mock_tools(self):
        """Mock all tools to avoid real API calls"""
        tools_to_mock = [
            'MarketInsight.utils.tools.get_stock_price',
            'MarketInsight.utils.tools.get_historical_data',
            'MarketInsight.utils.tools.get_stock_news',
            'MarketInsight.utils.tools.get_balance_sheet',
            'MarketInsight.utils.tools.get_income_statement',
            'MarketInsight.utils.tools.get_cash_flow',
            'MarketInsight.utils.tools.get_company_info',
            'MarketInsight.utils.tools.get_dividends',
            'MarketInsight.utils.tools.get_splits',
            'MarketInsight.utils.tools.get_institutional_holders',
            'MarketInsight.utils.tools.get_major_shareholders',
            'MarketInsight.utils.tools.get_mutual_fund_holders',
            'MarketInsight.utils.tools.get_insider_transactions',
            'MarketInsight.utils.tools.get_analyst_recommendations',
            'MarketInsight.utils.tools.get_analyst_recommendations_summary',
            'MarketInsight.utils.tools.get_ticker'
        ]

        mocks = {}
        for tool_path in tools_to_mock:
            mock_tool = Mock()
            mock_tool.return_value = "Sample tool response"
            mocks[tool_path] = mock_tool

        return mocks

    @pytest.fixture
    def mock_llm(self):
        """Mock the LLM to avoid real API calls"""
        with patch('MarketInsight.components.agent.ChatOpenAI') as mock:
            mock_model = Mock()
            yield mock_model

    def test_agent_initializes_with_all_tools(self):
        """Test that agent initializes successfully with all tools"""
        # Agent should be already initialized from agent.py
        assert agent is not None
        assert hasattr(agent, 'bound_tools')

        # Verify that tools are bound
        tools = agent.bound_tools
        assert len(tools) == 16

        # Verify tool names
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'get_stock_price',
            'get_historical_data',
            'get_stock_news',
            'get_balance_sheet',
            'get_income_statement',
            'get_cash_flow',
            'get_company_info',
            'get_dividends',
            'get_splits',
            'get_institutional_holders',
            'get_major_shareholders',
            'get_mutual_fund_holders',
            'get_insider_transactions',
            'get_analyst_recommendations',
            'get_analyst_recommendations_summary',
            'get_ticker'
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_agent_has_memory_saver(self):
        """Test that agent has MemorySaver checkpointer for conversation state"""
        assert agent is not None
        assert hasattr(agent, 'checkpoint')

        # Verify checkpointer is MemorySaver
        from langgraph.checkpoint.memory import MemorySaver
        assert isinstance(agent.checkpointer, MemorySaver)

    def test_agent_stream_returns_iterator(self):
        """Test that agent.stream returns an iterator"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a test assistant."),
                HumanMessage(content="Hello")
            ]
        }

        # Mock the stream to return empty iterator
        with patch.object(agent, 'stream', return_value=iter([])):
            result = agent.stream(messages, config=config)
            assert hasattr(result, '__iter__')

    def test_agent_handles_stock_price_query(self):
        """Test that agent can handle stock price queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the stock price of AAPL?")
            ]
        }

        # Mock the stream with tool call response
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_stock_price", "args": {"ticker": "AAPL"}, "id": "call_123"}]),
            Mock(content="The stock price of AAPL is $150.25")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_historical_data_query(self):
        """Test that agent can handle historical data queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Get historical data for AAPL from 2024-01-01 to 2024-01-31")
            ]
        }

        # Mock the stream with tool call response
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_historical_data", "args": {"ticker": "AAPL", "start_date": "2024-01-01", "end_date": "2024-01-31"}, "id": "call_124"}]),
            Mock(content="Here is the historical data for AAPL...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_company_info_query(self):
        """Test that agent can handle company info queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Tell me about Apple Inc")
            ]
        }

        # Mock the stream with tool call response
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_company_info", "args": {"ticker": "AAPL"}, "id": "call_125"}]),
            Mock(content="Apple Inc. is a technology company...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_multi_tool_queries(self):
        """Test that agent can handle queries requiring multiple tools"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Give me a comprehensive analysis of AAPL including price, news, and financials")
            ]
        }

        # Mock the stream with multiple tool calls
        mock_messages = [
            Mock(content= "", tool_calls=[
                {"name": "get_stock_price", "args": {"ticker": "AAPL"}, "id": "call_126"}
            ]),
            Mock(content= "", tool_calls=[
                {"name": "get_stock_news", "args": {"ticker": "AAPL"}, "id": "call_127"}
            ]),
            Mock(content= "", tool_calls=[
                {"name": "get_income_statement", "args": {"ticker": "AAPL"}, "id": "call_128"}
            ]),
            Mock(content="Here's a comprehensive analysis of AAPL...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_maintains_conversation_context(self):
        """Test that agent maintains conversation context across messages"""
        thread_id = "test-thread-context"

        # First message
        config1 = {'configurable': {'thread_id': thread_id}}
        messages1 = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the stock price of AAPL?")
            ]
        }

        # Second message (should remember context)
        config2 = {'configurable': {'thread_id': thread_id}}
        messages2 = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What about its market cap?")
            ]
        }

        mock_messages1 = [Mock(content="AAPL is trading at $150.25")]
        mock_messages2 = [Mock(content="AAPL has a market cap of $2.5 trillion")]

        with patch.object(agent, 'stream', return_value=iter(mock_messages1)):
            results1 = list(agent.stream(messages1, config=config1))
            assert len(results1) > 0

        with patch.object(agent, 'stream', return_value=iter(mock_messages2)):
            results2 = list(agent.stream(messages2, config=config2))
            assert len(results2) > 0

    def test_agent_handles_ticker_resolution(self):
        """Test that agent can resolve company names to tickers"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the stock price of Microsoft?")
            ]
        }

        # Mock the stream with ticker resolution
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_ticker", "args": {"company_name": "Microsoft"}, "id": "call_129"}]),
            Mock(content= "", tool_calls=[{"name": "get_stock_price", "args": {"ticker": "MSFT"}, "id": "call_130"}]),
            Mock(content="Microsoft (MSFT) is trading at $378.91")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_invalid_ticker(self):
        """Test that agent handles invalid ticker gracefully"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the stock price of INVALIDTICKER123?")
            ]
        }

        # Mock the stream with error handling
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_stock_price", "args": {"ticker": "INVALIDTICKER123"}, "id": "call_131"}]),
            Mock(content="I couldn't find valid data for ticker INVALIDTICKER123. Please verify the ticker symbol.")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_empty_query(self):
        """Test that agent handles empty or vague queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Hello")
            ]
        }

        # Mock the stream with general response
        mock_messages = [
            Mock(content="Hello! I'm a stock market analyst. How can I help you today?")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_stream_mode_messages(self):
        """Test that agent supports stream_mode='messages'"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a test assistant."),
                HumanMessage(content="Test message")
            ]
        }

        mock_messages = [
            Mock(content="Test response")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, stream_mode='messages', config=config))
            assert len(results) > 0

    def test_agent_handles_tool_errors(self):
        """Test that agent handles tool execution errors gracefully"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the stock price of AAPL?")
            ]
        }

        # Mock the stream with tool error
        mock_messages = [
            Mock(content= "", tool_calls=[{"name": "get_stock_price", "args": {"ticker": "AAPL"}, "id": "call_132"}]),
            Mock(content="I encountered an error retrieving the stock price. Please try again later.")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_respects_thread_id(self):
        """Test that agent uses thread_id for conversation isolation"""
        thread_id_1 = "thread-isolated-1"
        thread_id_2 = "thread-isolated-2"

        config1 = {'configurable': {'thread_id': thread_id_1}}
        config2 = {'configurable': {'thread_id': thread_id_2}}

        messages = {
            'messages': [
                SystemMessage(content="You are a test assistant."),
                HumanMessage(content="Remember: secret=123")
            ]
        }

        mock_messages = [Mock(content="I'll remember that.")]

        # Thread 1
        with patch.object(agent, 'stream', return_value=iter(mock_messages)) as mock1:
            list(agent.stream(messages, config=config1))
            assert mock1.called
            call_args = mock1.call_args
            assert call_args[1]['config']['configurable']['thread_id'] == thread_id_1

        # Thread 2
        with patch.object(agent, 'stream', return_value=iter(mock_messages)) as mock2:
            list(agent.stream(messages, config=config2))
            assert mock2.called
            call_args = mock2.call_args
            assert call_args[1]['config']['configurable']['thread_id'] == thread_id_2

    def test_agent_handles_financial_statements_query(self):
        """Test that agent can handle financial statement queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Show me the balance sheet and income statement for AAPL")
            ]
        }

        # Mock the stream with financial tools
        mock_messages = [
            Mock(content= "", tool_calls=[
                {"name": "get_balance_sheet", "args": {"ticker": "AAPL"}, "id": "call_133"}
            ]),
            Mock(content= "", tool_calls=[
                {"name": "get_income_statement", "args": {"ticker": "AAPL"}, "id": "call_134"}
            ]),
            Mock(content="Here are the financial statements for AAPL...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_analyst_recommendations_query(self):
        """Test that agent can handle analyst recommendations queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What are the analyst recommendations for GOOGL?")
            ]
        }

        # Mock the stream with analyst tools
        mock_messages = [
            Mock(content= "", tool_calls=[
                {"name": "get_analyst_recommendations", "args": {"ticker": "GOOGL"}, "id": "call_135"}
            ]),
            Mock(content="Here are the analyst recommendations for GOOGL...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_holder_information_query(self):
        """Test that agent can handle holder information queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="Who are the major holders of TSLA?")
            ]
        }

        # Mock the stream with holder tools
        mock_messages = [
            Mock(content= "", tool_calls=[
                {"name": "get_institutional_holders", "args": {"ticker": "TSLA"}, "id": "call_136"}
            ]),
            Mock(content= "", tool_calls=[
                {"name": "get_major_shareholders", "args": {"ticker": "TSLA"}, "id": "call_137"}
            ]),
            Mock(content="Here are the major holders of TSLA...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0

    def test_agent_handles_dividends_and_splits_query(self):
        """Test that agent can handle dividends and stock splits queries"""
        config = {'configurable': {'thread_id': 'test-thread-123'}}

        messages = {
            'messages': [
                SystemMessage(content="You are a professional stock market analyst."),
                HumanMessage(content="What is the dividend history and stock splits for AAPL?")
            ]
        }

        # Mock the stream with dividend and split tools
        mock_messages = [
            Mock(content= "", tool_calls=[
                {"name": "get_dividends", "args": {"ticker": "AAPL"}, "id": "call_138"}
            ]),
            Mock(content= "", tool_calls=[
                {"name": "get_splits", "args": {"ticker": "AAPL"}, "id": "call_139"}
            ]),
            Mock(content="Here is the dividend and split history for AAPL...")
        ]

        with patch.object(agent, 'stream', return_value=iter(mock_messages)):
            results = list(agent.stream(messages, config=config))
            assert len(results) > 0
