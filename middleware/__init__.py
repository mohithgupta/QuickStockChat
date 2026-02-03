"""
Security middleware package for MarketInsight application

This package contains middleware components for API security including:
- Rate limiting to prevent API abuse
- Authentication and authorization
- Security headers for enhanced protection
"""

from .rate_limiter import limiter
from .auth import get_api_key
from .security_headers import SecurityHeadersMiddleware

__all__ = [
    "limiter",
    "get_api_key",
    "SecurityHeadersMiddleware"
]
