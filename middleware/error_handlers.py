"""
Global exception handlers for FastAPI application.

This module contains all custom exception handlers that provide
consistent error responses across the application.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from MarketInsight.utils.exceptions import ValidationError, MarketInsightError, TickerValidationError, ExternalServiceError
from MarketInsight.utils.logger import get_logger

logger = get_logger(__name__)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with a clear message"""
    logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error": "rate_limit_exceeded"
        },
        headers={"Retry-After": "60"}
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors with user-friendly messages"""
    logger.warning(f"Validation error: {exc.message} for field {exc.field}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.message,
            "error_type": "ValidationError",
            "field": exc.field,
            "details": exc.details
        }
    )


async def market_insight_error_handler(request: Request, exc: MarketInsightError):
    """Handle all MarketInsight-specific errors"""
    # Determine appropriate status code based on error type
    if hasattr(exc, 'status_code') and exc.status_code:
        status_code = exc.status_code
    elif exc.__class__.__name__ in ['TickerValidationError', 'ValidationError']:
        status_code = status.HTTP_400_BAD_REQUEST
    elif exc.__class__.__name__ == 'ExternalServiceError':
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    logger.error(f"MarketInsight error: {exc.__class__.__name__} - {exc.message}")
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.message,
            "error_type": exc.__class__.__name__,
            "details": exc.details
        }
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all custom exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(MarketInsightError, market_insight_error_handler)
