import os
import uvicorn
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from langfuse import Langfuse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import SystemMessage, HumanMessage
from config.config import RequestObject, ValidationErrorResponse, ChartResponse, ChartDataPoint
from MarketInsight.components.agent import agent
from MarketInsight.utils.logger import get_logger
from MarketInsight.utils.validators import sanitize_input, validate_ticker
from MarketInsight.utils.exceptions import ValidationError, MarketInsightError, TickerValidationError, ExternalServiceError
from middleware.rate_limiter import limiter
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.auth import get_api_key
from middleware.error_handlers import register_exception_handlers
import yfinance as yf
from utils.api_throttler import get_throttler

logger = get_logger(__name__)
app = FastAPI()
app.state.limiter = limiter
throttler = get_throttler()

# Register global exception handlers
register_exception_handlers(app)

# Configure CORS with environment-based whitelist
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring and keep-alive pings"""
    return {"status": "ok", "message": "Service is running"}


@app.get("/api/charts/stock-price")
@limiter.limit("60/minute")
async def get_stock_price_chart(
    request: Request,
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)"),
    period: str = Query(default="1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    api_key: str = Depends(get_api_key)
):
    """
    Stock price chart endpoint returning historical price data for visualization.

    Provides OHLCV (Open, High, Low, Close, Volume) data for the specified ticker and time period.
    Returns data in a format suitable for chart libraries with support for line and candlestick charts.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
        period: Time period for historical data (default: "1mo")
            Valid options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    Returns:
        ChartResponse: Structured chart data with metadata and data points

    Raises:
        HTTPException 400: If ticker or period validation fails
        HTTPException 503: If external service (yfinance) is unavailable
    """
    # Validate ticker symbol
    validated_ticker = validate_ticker(ticker)

    # Validate period parameter
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    if period not in valid_periods:
        raise ValidationError(
            message=f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}",
            field="period",
            details={"valid_periods": valid_periods, "provided": period}
        )

    try:
        # Fetch historical data from yfinance
        with throttler.throttle("yfinance"):
            stock = yf.Ticker(validated_ticker)
            hist = stock.history(period=period)

        # Check if data is available
        if hist is None or hist.empty:
            logger.warning(f"No historical data available for {validated_ticker} with period {period}")
            raise ExternalServiceError(
                message=f"No historical data available for {validated_ticker} with the specified period",
                service_name="yfinance",
                details={"ticker": validated_ticker, "period": period}
            )

        # Convert DataFrame to list of ChartDataPoint
        data_points = []
        for index, row in hist.iterrows():
            # Format date as ISO string
            date_str = index.strftime("%Y-%m-%d")

            # Create data point with all available fields
            data_point = ChartDataPoint(
                date=date_str,
                value=float(row['Close']) if 'Close' in row and pd.notna(row['Close']) else None,
                open=float(row['Open']) if 'Open' in row and pd.notna(row['Open']) else None,
                high=float(row['High']) if 'High' in row and pd.notna(row['High']) else None,
                low=float(row['Low']) if 'Low' in row and pd.notna(row['Low']) else None,
                close=float(row['Close']) if 'Close' in row and pd.notna(row['Close']) else None,
                volume=float(row['Volume']) if 'Volume' in row and pd.notna(row['Volume']) else None
            )
            data_points.append(data_point)

        # Determine chart type based on data (candlestick if OHLC data exists, otherwise line)
        chart_type = "candlestick" if all(dp.open and dp.high and dp.low for dp in data_points) else "line"

        # Create response with metadata
        response = ChartResponse(
            ticker=validated_ticker,
            chart_type=chart_type,
            period=period,
            data=data_points,
            metadata={
                "data_points": len(data_points),
                "date_range": {
                    "start": data_points[0].date if data_points else None,
                    "end": data_points[-1].date if data_points else None
                },
                "currency": "USD"  # Default to USD, could be enhanced to detect currency
            }
        )

        logger.info(f"Successfully retrieved chart data for {validated_ticker} ({period}): {len(data_points)} data points")
        return response

    except Exception as e:
        logger.error(f"Failed to retrieve chart data for {validated_ticker}: {str(e)}")
        raise ExternalServiceError(
            message="Failed to retrieve stock price data. Please try again later.",
            service_name="yfinance",
            details={"ticker": validated_ticker, "period": period, "original_error": str(e)}
        )


@app.get("/api/charts/financial-statement")
@limiter.limit("60/minute")
async def get_financial_statement_chart(
    request: Request,
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)"),
    statement_type: str = Query(..., description="Statement type: income, balance, or cash_flow"),
    api_key: str = Depends(get_api_key)
):
    """
    Financial statement chart endpoint returning structured data for visualization.

    Provides financial statement data (income statement, balance sheet, or cash flow) for the specified ticker.
    Returns data in a format suitable for chart libraries with support for bar charts and time-series analysis.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
        statement_type: Type of financial statement (income, balance, or cash_flow)
            - income: Income statement (revenue, expenses, net income)
            - balance: Balance sheet (assets, liabilities, equity)
            - cash_flow: Cash flow statement (operating, investing, financing activities)

    Returns:
        ChartResponse: Structured chart data with metadata and data points

    Raises:
        HTTPException 400: If ticker or statement_type validation fails
        HTTPException 503: If external service (yfinance) is unavailable
    """
    # Validate ticker symbol
    validated_ticker = validate_ticker(ticker)

    # Validate statement_type parameter
    valid_statement_types = ["income", "balance", "cash_flow"]
    if statement_type not in valid_statement_types:
        raise ValidationError(
            message=f"Invalid statement_type '{statement_type}'. Must be one of: {', '.join(valid_statement_types)}",
            field="statement_type",
            details={"valid_statement_types": valid_statement_types, "provided": statement_type}
        )

    try:
        # Fetch financial statement data from yfinance
        with throttler.throttle("yfinance"):
            stock = yf.Ticker(validated_ticker)

            # Get the appropriate financial statement based on statement_type
            if statement_type == "income":
                financial_data = stock.income_stmt
                chart_type = "bar"
            elif statement_type == "balance":
                financial_data = stock.balance_sheet
                chart_type = "bar"
            else:  # cash_flow
                financial_data = stock.cash_flow
                chart_type = "bar"

        # Check if data is available
        if financial_data is None or financial_data.empty:
            logger.warning(f"No financial statement data available for {validated_ticker} with type {statement_type}")
            raise ExternalServiceError(
                message=f"No financial statement data available for {validated_ticker} with the specified type",
                service_name="yfinance",
                details={"ticker": validated_ticker, "statement_type": statement_type}
            )

        # Convert DataFrame columns to list of ChartDataPoint
        # Financial statements have dates as columns and metrics as rows
        data_points = []
        for col in financial_data.columns:
            # Format date as ISO string (yfinance returns Timestamp objects)
            if hasattr(col, 'strftime'):
                date_str = col.strftime("%Y-%m-%d")
            else:
                date_str = str(col)

            # Extract all metric values for this date
            metric_values = {}
            for idx, row in financial_data.iterrows():
                metric_name = str(idx)
                value = row[col]
                # Skip NaN values
                if value == value:  # NaN check
                    try:
                        metric_values[metric_name] = float(value)
                    except (TypeError, ValueError):
                        pass

            # Create data point with the date and primary metrics
            # For bar charts, we'll use the first few key metrics as the main values
            data_point = ChartDataPoint(
                date=date_str,
                value=list(metric_values.values())[0] if metric_values else None,
                metadata=metric_values if metric_values else {}
            )
            data_points.append(data_point)

        # Create response with metadata
        response = ChartResponse(
            ticker=validated_ticker,
            chart_type=chart_type,
            period=statement_type,
            data=data_points,
            metadata={
                "data_points": len(data_points),
                "date_range": {
                    "start": data_points[0].date if data_points else None,
                    "end": data_points[-1].date if data_points else None
                },
                "statement_type": statement_type,
                "available_metrics": list(financial_data.index.tolist()) if not financial_data.empty else []
            }
        )

        logger.info(f"Successfully retrieved {statement_type} statement data for {validated_ticker}: {len(data_points)} data points")
        return response

    except Exception as e:
        logger.error(f"Failed to retrieve financial statement data for {validated_ticker}: {str(e)}")
        raise ExternalServiceError(
            message="Failed to retrieve financial statement data. Please try again later.",
            service_name="yfinance",
            details={"ticker": validated_ticker, "statement_type": statement_type, "original_error": str(e)}
        )


@app.post("/api/chat")
@limiter.limit("100/minute")
async def chat(request: Request, body: RequestObject, api_key: str = Depends(get_api_key)):
    """
    Chat endpoint for processing user queries with agent-based responses.

    Validates the input prompt and returns streaming responses from the agent.
    Raises ValidationError if the prompt content is empty or invalid.
    """
    # Validate prompt content
    try:
        sanitized_content = sanitize_input(body.prompt.content, max_length=5000)
    except ValidationError as e:
        logger.warning(f"Validation failed for chat request: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Prompt content is required and cannot be empty",
                "error_type": "ValidationError",
                "field": "prompt.content"
            }
        )

    config = {'configurable': {'thread_id': body.threadId}}
    async def generate():
        try:
            # Create a span for the entire request
            with langfuse.start_as_current_observation(
                as_type="span",
                name="chat-request",
                input=sanitized_content
            ) as span:
                # Set user_id as metadata
                span.update(metadata={"user_id": body.threadId})

                # Create a nested generation for the LLM/agent call
                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="agent-stream",
                    model="agentic-workflow",
                    input=sanitized_content
                ) as generation:

                    full_response = ""
                    for token, _ in agent.stream(
                        {
                            'messages': [
                                SystemMessage(content="You are a professional stock market analyst. For every user query, first determine whether a relevant tool can provide accurate or real-time data. If an appropriate tool exists, you must use it before answering. If the user does not provide an exact stock ticker, use the available tool to identify or resolve the correct ticker when required. Only when no suitable tool applies should you respond using your own reasoning and general market knowledge. Never guess, assume, or fabricate any financial data."),
                                HumanMessage(content=sanitized_content)
                            ]
                        },
                        stream_mode='messages',
                        config=config
                    ):
                        full_response += token.content
                        yield token.content

                    # Update generation with the complete output
                    generation.update(output=full_response)

                # Update span with completion status
                span.update(output="Request completed successfully")

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    return StreamingResponse(generate(), media_type='text/event-stream',
        headers={
            'cache-control': 'no-cache, no-transform', 
            'connection': 'keep-alive'
        })

if __name__ == '__main__':
    logger.info("App Initiated Successfully")
    uvicorn.run(app, host='0.0.0.0', port=8000)