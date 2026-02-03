# exceptions.py
"""
Custom exception classes for MarketInsight application.

Provides specific exception types for different error scenarios including
ticker validation failures, API errors, and external service failures.
"""

from typing import Optional, Dict, Any
from MarketInsight.utils.logger import get_logger

logger = get_logger(__name__)


class MarketInsightError(Exception):
    """
    Base exception class for all MarketInsight-specific errors.

    All custom exceptions inherit from this base class to allow
    catching all MarketInsight errors with a single except clause.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class TickerValidationError(MarketInsightError):
    """
    Raised when ticker symbol validation fails.

    This exception is used when a provided ticker symbol is invalid,
    malformed, or fails validation checks.
    """

    def __init__(
        self,
        message: str,
        ticker: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ticker validation error.

        Args:
            message: Human-readable error message
            ticker: The invalid ticker symbol that caused the error
            details: Optional dictionary with additional error context
        """
        self.ticker = ticker
        error_details = details or {}
        if ticker:
            error_details["ticker"] = ticker

        super().__init__(message, error_details)
        logger.debug(f"TickerValidationError: {self} (ticker={ticker})")


class APIError(MarketInsightError):
    """
    Raised when an internal API operation fails.

    This exception is used for errors that occur within the application's
    API layer, such as request processing failures or configuration errors.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code associated with the error
            details: Optional dictionary with additional error context
        """
        self.status_code = status_code
        error_details = details or {}
        if status_code:
            error_details["status_code"] = status_code

        super().__init__(message, error_details)
        logger.warning(f"APIError: {self} (status_code={status_code})")


class ExternalServiceError(MarketInsightError):
    """
    Raised when an external service API call fails.

    This exception is used when calling external APIs (such as financial data providers)
    and the call fails due to network issues, rate limits, or service unavailability.
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize external service error.

        Args:
            message: Human-readable error message
            service_name: Name of the external service that failed
            status_code: HTTP status code from the external service
            details: Optional dictionary with additional error context
        """
        self.service_name = service_name
        self.status_code = status_code
        error_details = details or {}
        if service_name:
            error_details["service"] = service_name
        if status_code:
            error_details["status_code"] = status_code

        super().__init__(message, error_details)
        logger.warning(
            f"ExternalServiceError: {self} "
            f"(service={service_name}, status_code={status_code})"
        )


class ValidationError(MarketInsightError):
    """
    Raised when input validation fails.

    This exception is used for general validation errors that are not
    specifically related to ticker symbols.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation error.

        Args:
            message: Human-readable error message
            field: Name of the field that failed validation
            details: Optional dictionary with additional error context
        """
        self.field = field
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(message, error_details)
        logger.debug(f"ValidationError: {self} (field={field})")


class ConfigurationError(MarketInsightError):
    """
    Raised when there is a configuration error.

    This exception is used when the application is misconfigured
    or required environment variables are missing.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize configuration error.

        Args:
            message: Human-readable error message
            config_key: Name of the configuration key that is problematic
            details: Optional dictionary with additional error context
        """
        self.config_key = config_key
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key

        super().__init__(message, error_details)
        logger.error(f"ConfigurationError: {self} (config_key={config_key})")
