# rate_limiter.py
"""
Rate limiting middleware using slowapi

Provides IP-based rate limiting to prevent API abuse and ensure
fair usage of resources.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Callable


def get_identifier(request) -> str:
    """
    Get the client identifier for rate limiting.

    Args:
        request: The incoming request object

    Returns:
        str: The client's IP address
    """
    return get_remote_address(request)


# Create limiter instance
# Configuration will be applied during integration in main.py
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute"],  # Default: 100 requests per minute
    storage_uri="memory://",  # In-memory storage for single-instance deployments
)
