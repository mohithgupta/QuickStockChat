# auth.py
"""
API key authentication middleware

Provides optional API key authentication for protected endpoints.
API keys can be provided via X-API-Key header or api_key query parameter.
"""

import os
from typing import Optional
from fastapi import Header, HTTPException, status
from MarketInsight.utils.logger import get_logger

logger = get_logger(__name__)


async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Validate API key from request headers or query parameters.

    Authentication is controlled by REQUIRE_API_KEY environment variable.
    If not enabled, this function returns None and authentication is skipped.

    Args:
        x_api_key: API key from X-API-Key header
        api_key: API key from query parameter

    Returns:
        Optional[str]: The validated API key, or None if auth is disabled

    Raises:
        HTTPException: If authentication is required and key is invalid/missing
    """
    require_auth = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"

    # If authentication is not required, skip validation
    if not require_auth:
        return None

    # Get the API key from header or query parameter
    provided_key = x_api_key or api_key

    # Get the expected API key from environment
    expected_key = os.getenv("API_KEY")

    if not expected_key:
        logger.warning("API_KEY environment variable not set but authentication is required")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API key not configured"
        )

    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide it via X-API-Key header or api_key query parameter."
        )

    if provided_key != expected_key:
        logger.warning(f"Invalid API key attempt from {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    logger.debug("API key authentication successful")
    return provided_key
