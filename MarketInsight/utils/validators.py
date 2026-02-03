"""
Input validation utilities for MarketInsight application.

Provides functions to validate and sanitize user inputs including ticker symbols,
company names, and other user-provided data to prevent security issues and ensure
data quality.
"""

import re
from typing import Optional
from MarketInsight.utils.logger import get_logger
from MarketInsight.utils.exceptions import TickerValidationError, ValidationError

logger = get_logger("Validators")


# --------------------------------------------------------------------------------
# Validator 1: Validate Ticker Symbol
# --------------------------------------------------------------------------------
def validate_ticker(ticker: Optional[str]) -> str:
    """
    Validate and clean a ticker symbol.

    Ensures the ticker symbol is valid, properly formatted, and safe to use
    in API calls. Raises TickerValidationError if validation fails.

    Args:
        ticker: The ticker symbol to validate

    Returns:
        str: The cleaned and validated ticker symbol in uppercase

    Raises:
        TickerValidationError: If the ticker symbol is invalid or malformed
    """
    logger.debug(f"Validating ticker: {ticker}")

    # Check if ticker is provided
    if not ticker:
        logger.error("Ticker validation failed: No ticker provided")
        raise TickerValidationError(
            "Ticker symbol is required",
            ticker=ticker
        )

    # Check if ticker is a string
    if not isinstance(ticker, str):
        logger.error(f"Ticker validation failed: Invalid type {type(ticker)}")
        raise TickerValidationError(
            "Ticker symbol must be a string",
            ticker=str(ticker)
        )

    # Strip whitespace
    cleaned_ticker = ticker.strip()

    # Check if ticker is empty after stripping
    if not cleaned_ticker:
        logger.error("Ticker validation failed: Empty ticker after stripping whitespace")
        raise TickerValidationError(
            "Ticker symbol cannot be empty or whitespace only",
            ticker=ticker
        )

    # Check length (typical ticker symbols are 1-5 characters, but some can be longer)
    if len(cleaned_ticker) > 10:
        logger.error(f"Ticker validation failed: Too long ({len(cleaned_ticker)} characters)")
        raise TickerValidationError(
            f"Ticker symbol is too long (maximum 10 characters, got {len(cleaned_ticker)})",
            ticker=cleaned_ticker
        )

    # Check for valid characters (letters, numbers, dot, hyphen, underscore)
    # Some tickers have dots (e.g., BRK.B), hyphens (e.g., BF-B), or numbers (e.g., 005930.TW)
    if not re.match(r'^[A-Za-z0-9._-]+$', cleaned_ticker):
        logger.error(f"Ticker validation failed: Invalid characters in '{cleaned_ticker}'")
        raise TickerValidationError(
            "Ticker symbol contains invalid characters. Only letters, numbers, dots, hyphens, and underscores are allowed",
            ticker=cleaned_ticker
        )

    # Convert to uppercase for consistency
    cleaned_ticker = cleaned_ticker.upper()

    # Additional check: ensure ticker doesn't start/end with special characters
    if cleaned_ticker[0] in ['.', '-', '_'] or cleaned_ticker[-1] in ['.', '-', '_']:
        logger.error(f"Ticker validation failed: Starts/ends with special character '{cleaned_ticker}'")
        raise TickerValidationError(
            "Ticker symbol cannot start or end with a dot, hyphen, or underscore",
            ticker=cleaned_ticker
        )

    logger.info(f"Ticker validated successfully: {cleaned_ticker}")
    return cleaned_ticker


# --------------------------------------------------------------------------------
# Validator 2: Sanitize User Input
# --------------------------------------------------------------------------------
def sanitize_input(input_value: Optional[str], max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks and ensure data safety.

    Removes or escapes potentially dangerous characters while preserving
    legitimate user input. Raises ValidationError if sanitization fails.

    Args:
        input_value: The user input to sanitize
        max_length: Maximum allowed length for the input (default: 1000)

    Returns:
        str: The sanitized input string

    Raises:
        ValidationError: If the input is invalid or cannot be sanitized
    """
    logger.debug(f"Sanitizing input (length: {len(input_value) if input_value else 0})")

    # Check if input is provided
    if not input_value:
        logger.error("Input sanitization failed: No input provided")
        raise ValidationError(
            "Input value is required",
            field="user_input"
        )

    # Check if input is a string
    if not isinstance(input_value, str):
        logger.error(f"Input sanitization failed: Invalid type {type(input_value)}")
        raise ValidationError(
            "Input value must be a string",
            field="user_input"
        )

    # Strip leading/trailing whitespace
    cleaned_input = input_value.strip()

    # Check if input is empty after stripping
    if not cleaned_input:
        logger.error("Input sanitization failed: Empty input after stripping whitespace")
        raise ValidationError(
            "Input value cannot be empty or whitespace only",
            field="user_input"
        )

    # Check length
    if len(cleaned_input) > max_length:
        logger.error(f"Input sanitization failed: Too long ({len(cleaned_input)} characters)")
        raise ValidationError(
            f"Input value is too long (maximum {max_length} characters, got {len(cleaned_input)})",
            field="user_input"
        )

    # Remove null bytes
    cleaned_input = cleaned_input.replace('\x00', '')

    # Remove potentially dangerous Unicode characters
    # This includes control characters except newline, tab, and carriage return
    cleaned_input = ''.join(
        char for char in cleaned_input
        if char == '\n' or char == '\t' or char == '\r' or not (ord(char) < 32 and ord(char) != 10)
    )

    # Normalize whitespace (replace multiple spaces/tabs with single space)
    cleaned_input = re.sub(r'[ \t]+', ' ', cleaned_input)

    # Check for suspicious patterns that might indicate injection attempts
    dangerous_patterns = [
        r'<script[^>]*>',  # Script tags
        r'javascript:',     # JavaScript protocol
        r'onerror=',       # Event handler injection
        r'onload=',        # Event handler injection
        r'<iframe',        # iframe tags
        r'<embed',         # embed tags
        r'<object',        # object tags
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned_input, re.IGNORECASE):
            logger.warning(f"Input sanitization detected potentially dangerous pattern: {pattern}")
            # Remove the dangerous pattern
            cleaned_input = re.sub(pattern, '', cleaned_input, flags=re.IGNORECASE)

    # Check if input is still valid after sanitization
    if not cleaned_input:
        logger.error("Input sanitization failed: Input became empty after removing dangerous content")
        raise ValidationError(
            "Input value contains only invalid or dangerous content",
            field="user_input"
        )

    logger.info(f"Input sanitized successfully (final length: {len(cleaned_input)})")
    return cleaned_input


# --------------------------------------------------------------------------------
# Validator 3: Validate Date String
# --------------------------------------------------------------------------------
def validate_date_string(date_str: Optional[str], date_format: str = "%Y-%m-%d") -> str:
    """
    Validate a date string in the specified format.

    Ensures the date string is valid and properly formatted.
    Raises ValidationError if validation fails.

    Args:
        date_str: The date string to validate
        date_format: Expected date format (default: YYYY-MM-DD)

    Returns:
        str: The validated date string

    Raises:
        ValidationError: If the date string is invalid or malformed
    """
    from datetime import datetime

    logger.debug(f"Validating date string: {date_str}")

    # Check if date is provided
    if not date_str:
        logger.error("Date validation failed: No date provided")
        raise ValidationError(
            "Date string is required",
            field="date"
        )

    # Check if date is a string
    if not isinstance(date_str, str):
        logger.error(f"Date validation failed: Invalid type {type(date_str)}")
        raise ValidationError(
            "Date string must be a string",
            field="date"
        )

    # Strip whitespace
    cleaned_date = date_str.strip()

    # Check if date is empty after stripping
    if not cleaned_date:
        logger.error("Date validation failed: Empty date after stripping whitespace")
        raise ValidationError(
            "Date string cannot be empty or whitespace only",
            field="date"
        )

    # Try to parse the date
    try:
        datetime.strptime(cleaned_date, date_format)
    except ValueError as e:
        logger.error(f"Date validation failed: Invalid format - {str(e)}")
        raise ValidationError(
            f"Date string must be in {date_format} format (e.g., {datetime.now().strftime(date_format)})",
            field=cleaned_date
        )

    logger.info(f"Date validated successfully: {cleaned_date}")
    return cleaned_date


# --------------------------------------------------------------------------------
# Validator 4: Validate Positive Number
# --------------------------------------------------------------------------------
def validate_positive_number(value: any, field_name: str = "value") -> float:
    """
    Validate that a value is a positive number.

    Ensures the value is numeric and greater than zero.
    Raises ValidationError if validation fails.

    Args:
        value: The value to validate
        field_name: Name of the field being validated (for error messages)

    Returns:
        float: The validated value as a float

    Raises:
        ValidationError: If the value is not a positive number
    """
    logger.debug(f"Validating positive number for field '{field_name}': {value}")

    # Check if value is provided
    if value is None:
        logger.error(f"Positive number validation failed: No value provided for '{field_name}'")
        raise ValidationError(
            f"{field_name} is required",
            field=field_name
        )

    # Try to convert to float
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        logger.error(f"Positive number validation failed: Cannot convert '{value}' to number")
        raise ValidationError(
            f"{field_name} must be a valid number",
            field=field_name
        )

    # Check if positive
    if numeric_value <= 0:
        logger.error(f"Positive number validation failed: Value {numeric_value} is not positive")
        raise ValidationError(
            f"{field_name} must be greater than zero (got {numeric_value})",
            field=field_name
        )

    logger.info(f"Positive number validated successfully: {numeric_value}")
    return numeric_value
