"""
Configuration module for the application.

This module contains Pydantic models for request/response objects and
constants for external API rate limits.
"""

from pydantic import BaseModel

# External API Rate Limits
# These values control the maximum request rate for external API calls
# to prevent exceeding provider limits and control costs.
# Rate limits are expressed in requests per second.
YFINANCE_RATE_LIMIT = 2.0  # 2 requests/second = 120/minute
OPENAI_RATE_LIMIT = 10.0  # 10 requests/second = 600/minute
DEFAULT_API_RATE_LIMIT = 1.0  # 1 request/second = 60/minute
API_THROTTLER_CAPACITY = 10  # Maximum number of tokens in the bucket


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