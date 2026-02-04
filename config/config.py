"""
Configuration module for the application.

This module contains Pydantic models for request/response objects,
security configuration loaded from environment variables, and
constants for external API rate limits.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# =============================================================================
# Security Configuration
# =============================================================================

# API Authentication
# API key for protecting endpoints (loaded from environment)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY: str = os.getenv("API_KEY", "")

# Require API key for protected endpoints (default: False for development)
# Set to 'true' to enable authentication on protected endpoints
REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"

# CORS Configuration
# Comma-separated list of allowed origins for Cross-Origin Resource Sharing
# In production, restrict to your actual frontend domain(s)
_CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
CORS_ORIGINS: List[str] = [origin.strip() for origin in _CORS_ORIGINS_STR.split(",") if origin.strip()]


# =============================================================================
# External API Rate Limits
# =============================================================================

# These values control the maximum request rate for external API calls
# to prevent exceeding provider limits and control costs.
# Rate limits are expressed in requests per second.
# Can be overridden via environment variables.

YFINANCE_RATE_LIMIT: float = float(os.getenv("YFINANCE_RATE_LIMIT", "2.0"))  # 2 requests/second = 120/minute
OPENAI_RATE_LIMIT: float = float(os.getenv("OPENAI_RATE_LIMIT", "10.0"))  # 10 requests/second = 600/minute
DEFAULT_API_RATE_LIMIT: float = float(os.getenv("DEFAULT_API_RATE_LIMIT", "1.0"))  # 1 request/second = 60/minute
API_THROTTLER_CAPACITY: int = int(os.getenv("API_THROTTLER_CAPACITY", "10"))  # Maximum number of tokens in the bucket


# =============================================================================
# Pydantic Models
# =============================================================================

class PromptObject(BaseModel):
    """Model for a prompt in a chat conversation."""
    content: str
    id: str
    role: str


class RequestObject(BaseModel):
    """Model for a chat request with prompt and thread metadata."""
    prompt: PromptObject
    threadId: str
    responseId: str


class ErrorResponse(BaseModel):
    """Model for a standard error response with user-friendly message."""
    error: str  # User-friendly error message
    error_type: str  # Type of error (e.g., "TickerValidationError", "APIError")
    details: Optional[Dict[str, Any]] = None  # Additional error context


class ValidationErrorResponse(BaseModel):
    """Model for a validation error response with field-level details."""
    error: str  # User-friendly error message
    error_type: str = "ValidationError"  # Default error type for validation errors
    field: Optional[str] = None  # The field that failed validation
    details: Optional[Dict[str, Any]] = None  # Additional validation context


class ChartDataPoint(BaseModel):
    """Model for a single data point in a chart."""
    date: str  # ISO format date string (e.g., "2024-01-15")
    value: Optional[float] = None  # The primary value (e.g., stock price, revenue)
    volume: Optional[float] = None  # Trading volume (for stock charts)
    open: Optional[float] = None  # Opening price (for candlestick charts)
    high: Optional[float] = None  # High price (for candlestick charts)
    low: Optional[float] = None  # Low price (for candlestick charts)
    close: Optional[float] = None  # Closing price (for candlestick charts)
    metadata: Optional[Dict[str, Any]] = None  # Additional metrics (for financial statements)


class ChartResponse(BaseModel):
    """Model for a complete chart response with metadata and data points."""
    ticker: str  # Stock ticker symbol
    chart_type: str  # Type of chart (e.g., "line", "candlestick", "bar", "pie")
    period: str  # Time period (e.g., "1mo", "3mo", "1y", "max")
    data: List[ChartDataPoint]  # List of data points
    metadata: Optional[Dict[str, Any]] = None  # Additional chart metadata