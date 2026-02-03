# security_headers.py
"""
Security headers middleware

Adds security-related HTTP headers to all responses to enhance
application security and protect against common vulnerabilities.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from MarketInsight.utils.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    Adds the following headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Content-Security-Policy: restrictive policy
    - Strict-Transport-Security: enforce HTTPS (production only)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response with security headers added
        """
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        # Allows scripts from same origin, inline scripts, and specific external sources
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https: http:",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self' https://api.openai.com https://query1.finance.yahoo.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # HTTP Strict Transport Security (only for HTTPS)
        # Skip in development to allow HTTP
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        logger.debug("Security headers applied to response")
        return response
