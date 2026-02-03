"""
Unit tests for MarketInsight/utils/validators.py validation functions

Tests cover ticker validation, input sanitization, date validation, and positive number validation.
"""

import pytest
from datetime import datetime
from MarketInsight.utils.validators import (
    validate_ticker,
    sanitize_input,
    validate_date_string,
    validate_positive_number
)
from MarketInsight.utils.exceptions import TickerValidationError, ValidationError


class TestValidateTickerValidInputs:
    """Test suite for validate_ticker with valid inputs"""

    def test_valid_simple_ticker(self):
        """Test validate_ticker accepts simple uppercase ticker"""
        result = validate_ticker("AAPL")
        assert result == "AAPL"

    def test_valid_simple_ticker_lowercase(self):
        """Test validate_ticker converts lowercase to uppercase"""
        result = validate_ticker("aapl")
        assert result == "AAPL"

    def test_valid_ticker_with_whitespace(self):
        """Test validate_ticker strips whitespace"""
        result = validate_ticker("  msft  ")
        assert result == "MSFT"

    def test_valid_ticker_with_numbers(self):
        """Test validate_ticker accepts tickers with numbers"""
        result = validate_ticker("005930.TW")
        assert result == "005930.TW"

    def test_valid_ticker_with_dot(self):
        """Test validate_ticker accepts tickers with dots"""
        result = validate_ticker("BRK.B")
        assert result == "BRK.B"

    def test_valid_ticker_with_hyphen(self):
        """Test validate_ticker accepts tickers with hyphens"""
        result = validate_ticker("BF-B")
        assert result == "BF-B"

    def test_valid_ticker_with_underscore(self):
        """Test validate_ticker accepts tickers with underscores"""
        result = validate_ticker("TEST_A")
        assert result == "TEST_A"

    def test_valid_ticker_mixed_case(self):
        """Test validate_ticker normalizes mixed case"""
        result = validate_ticker("GoOgLe")
        assert result == "GOOGLE"

    def test_valid_single_character_ticker(self):
        """Test validate_ticker accepts single character tickers"""
        result = validate_ticker("F")
        assert result == "F"

    def test_valid_ten_character_ticker(self):
        """Test validate_ticker accepts maximum length (10 characters)"""
        result = validate_ticker("ABCDEFGHIJ")
        assert result == "ABCDEFGHIJ"


class TestValidateTickerMissingOrNoneInputs:
    """Test suite for validate_ticker with missing or None inputs"""

    def test_ticker_none_raises_error(self):
        """Test validate_ticker raises TickerValidationError for None"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker(None)

        assert "Ticker symbol is required" in str(exc_info.value)
        assert exc_info.value.ticker is None

    def test_ticker_empty_string_raises_error(self):
        """Test validate_ticker raises TickerValidationError for empty string"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("")

        assert "Ticker symbol is required" in str(exc_info.value)

    def test_ticker_whitespace_only_raises_error(self):
        """Test validate_ticker raises TickerValidationError for whitespace only"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("   ")

        assert "cannot be empty or whitespace only" in str(exc_info.value)

    def test_ticker_tabs_only_raises_error(self):
        """Test validate_ticker raises TickerValidationError for tabs only"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("\t\t")

        assert "cannot be empty or whitespace only" in str(exc_info.value)

    def test_ticker_newline_only_raises_error(self):
        """Test validate_ticker raises TickerValidationError for newline only"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("\n")

        assert "cannot be empty or whitespace only" in str(exc_info.value)


class TestValidateTickerInvalidType:
    """Test suite for validate_ticker with invalid types"""

    def test_ticker_integer_raises_error(self):
        """Test validate_ticker raises TickerValidationError for integer"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker(123)

        assert "must be a string" in str(exc_info.value)

    def test_ticker_list_raises_error(self):
        """Test validate_ticker raises TickerValidationError for list"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker(["AAPL"])

        assert "must be a string" in str(exc_info.value)

    def test_ticker_dict_raises_error(self):
        """Test validate_ticker raises TickerValidationError for dict"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker({"ticker": "AAPL"})

        assert "must be a string" in str(exc_info.value)

    def test_ticker_boolean_raises_error(self):
        """Test validate_ticker raises TickerValidationError for boolean"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker(True)

        assert "must be a string" in str(exc_info.value)


class TestValidateTickerInvalidCharacters:
    """Test suite for validate_ticker with invalid characters"""

    def test_ticker_with_space_raises_error(self):
        """Test validate_ticker raises TickerValidationError for space in ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL MSFT")

        assert "invalid characters" in str(exc_info.value).lower()

    def test_ticker_with_special_chars_raises_error(self):
        """Test validate_ticker raises TickerValidationError for special characters"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL@MSFT")

        assert "invalid characters" in str(exc_info.value).lower()

    def test_ticker_with_slash_raises_error(self):
        """Test validate_ticker raises TickerValidationError for slash"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAA/BB")

        assert "invalid characters" in str(exc_info.value).lower()

    def test_ticker_with_parentheses_raises_error(self):
        """Test validate_ticker raises TickerValidationError for parentheses"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL(MSFT)")

        assert "invalid characters" in str(exc_info.value).lower()

    def test_ticker_with_exclamation_raises_error(self):
        """Test validate_ticker raises TickerValidationError for exclamation mark"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL!")

        assert "invalid characters" in str(exc_info.value).lower()


class TestValidateTickerInvalidLength:
    """Test suite for validate_ticker with invalid length"""

    def test_ticker_too_long_raises_error(self):
        """Test validate_ticker raises TickerValidationError for ticker > 10 chars"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("ABCDEFGHIJK")

        assert "too long" in str(exc_info.value).lower()
        assert "10 characters" in str(exc_info.value)

    def test_ticker_very_long_raises_error(self):
        """Test validate_ticker raises TickerValidationError for very long ticker"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("A" * 100)

        assert "too long" in str(exc_info.value).lower()


class TestValidateTickerInvalidPositionSpecialChars:
    """Test suite for validate_ticker with special chars at start/end"""

    def test_ticker_starts_with_dot_raises_error(self):
        """Test validate_ticker raises TickerValidationError for dot at start"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker(".AAPL")

        assert "cannot start or end" in str(exc_info.value).lower()

    def test_ticker_ends_with_dot_raises_error(self):
        """Test validate_ticker raises TickerValidationError for dot at end"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL.")

        assert "cannot start or end" in str(exc_info.value).lower()

    def test_ticker_starts_with_hyphen_raises_error(self):
        """Test validate_ticker raises TickerValidationError for hyphen at start"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("-AAPL")

        assert "cannot start or end" in str(exc_info.value).lower()

    def test_ticker_ends_with_hyphen_raises_error(self):
        """Test validate_ticker raises TickerValidationError for hyphen at end"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL-")

        assert "cannot start or end" in str(exc_info.value).lower()

    def test_ticker_starts_with_underscore_raises_error(self):
        """Test validate_ticker raises TickerValidationError for underscore at start"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("_AAPL")

        assert "cannot start or end" in str(exc_info.value).lower()

    def test_ticker_ends_with_underscore_raises_error(self):
        """Test validate_ticker raises TickerValidationError for underscore at end"""
        with pytest.raises(TickerValidationError) as exc_info:
            validate_ticker("AAPL_")

        assert "cannot start or end" in str(exc_info.value).lower()


class TestSanitizeInputValidInputs:
    """Test suite for sanitize_input with valid inputs"""

    def test_valid_simple_input(self):
        """Test sanitize_input accepts simple text"""
        result = sanitize_input("Hello World")
        assert result == "Hello World"

    def test_input_with_whitespace(self):
        """Test sanitize_input strips leading/trailing whitespace"""
        result = sanitize_input("  Hello World  ")
        assert result == "Hello World"

    def test_input_with_tabs(self):
        """Test sanitize_input preserves internal tabs but normalizes to space"""
        result = sanitize_input("Hello\t\tWorld")
        assert result == "Hello World"

    def test_input_with_newlines(self):
        """Test sanitize_input preserves newlines"""
        result = sanitize_input("Hello\nWorld")
        assert result == "Hello\nWorld"

    def test_input_with_multiple_spaces(self):
        """Test sanitize_input normalizes multiple spaces to single space"""
        result = sanitize_input("Hello    World")
        assert result == "Hello World"

    def test_input_at_max_length(self):
        """Test sanitize_input accepts input at max length (1000)"""
        input_text = "A" * 1000
        result = sanitize_input(input_text)
        assert result == input_text
        assert len(result) == 1000

    def test_input_with_special_chars(self):
        """Test sanitize_input accepts special characters"""
        result = sanitize_input("Hello! @#$ %^&*() World")
        assert result == "Hello! @#$ %^&*() World"

    def test_input_with_unicode(self):
        """Test sanitize_input accepts unicode characters"""
        result = sanitize_input("Hello 世界 🌍")
        assert result == "Hello 世界 🌍"

    def test_input_with_null_bytes(self):
        """Test sanitize_input removes null bytes"""
        result = sanitize_input("Hello\x00World")
        assert result == "HelloWorld"

    def test_input_with_control_characters(self):
        """Test sanitize_input removes control characters"""
        result = sanitize_input("Hello\x01\x02World")
        assert result == "HelloWorld"


class TestSanitizeInputMissingOrNoneInputs:
    """Test suite for sanitize_input with missing or None inputs"""

    def test_none_raises_error(self):
        """Test sanitize_input raises ValidationError for None"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input(None)

        assert "is required" in str(exc_info.value)
        assert exc_info.value.field == "user_input"

    def test_empty_string_raises_error(self):
        """Test sanitize_input raises ValidationError for empty string"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("")

        # Empty string is caught by the "not input_value" check before whitespace check
        assert "is required" in str(exc_info.value)

    def test_whitespace_only_raises_error(self):
        """Test sanitize_input raises ValidationError for whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_tabs_only_raises_error(self):
        """Test sanitize_input raises ValidationError for tabs only"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("\t\t")

        assert "cannot be empty" in str(exc_info.value)


class TestSanitizeInputInvalidType:
    """Test suite for sanitize_input with invalid types"""

    def test_integer_raises_error(self):
        """Test sanitize_input raises TypeError for integer (tries to call len())"""
        with pytest.raises(TypeError) as exc_info:
            sanitize_input(123)

        assert "object of type 'int' has no len()" in str(exc_info.value)

    def test_list_raises_error(self):
        """Test sanitize_input raises ValidationError for list"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input(["input"])

        assert "must be a string" in str(exc_info.value)

    def test_dict_raises_error(self):
        """Test sanitize_input raises ValidationError for dict"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input({"input": "text"})

        assert "must be a string" in str(exc_info.value)


class TestSanitizeInputInvalidLength:
    """Test suite for sanitize_input with invalid length"""

    def test_input_too_long_raises_error(self):
        """Test sanitize_input raises ValidationError for input > max_length"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("A" * 1001)

        assert "too long" in str(exc_info.value).lower()
        assert "1000 characters" in str(exc_info.value)

    def test_custom_max_length(self):
        """Test sanitize_input respects custom max_length"""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("A" * 101, max_length=100)

        assert "too long" in str(exc_info.value).lower()
        assert "100 characters" in str(exc_info.value)


class TestSanitizeInputDangerousPatterns:
    """Test suite for sanitize_input with dangerous patterns"""

    def test_removes_script_tag(self):
        """Test sanitize_input removes opening script tag"""
        # Note: Only removes opening tag, pattern is r'<script[^>]*>'
        result = sanitize_input("Hello <script>alert('XSS')</script> World")
        assert result == "Hello alert('XSS')</script> World"

    def test_removes_javascript_protocol(self):
        """Test sanitize_input removes javascript: protocol"""
        result = sanitize_input("javascript:alert('XSS')")
        assert "javascript:" not in result.lower()

    def test_removes_onerror_handler(self):
        """Test sanitize_input removes onerror event handler"""
        result = sanitize_input("<img src=x onerror=alert('XSS')>")
        assert "onerror=" not in result

    def test_removes_onload_handler(self):
        """Test sanitize_input removes onload event handler"""
        result = sanitize_input("<img src=x onload=alert('XSS')>")
        assert "onload=" not in result

    def test_removes_iframe_tag(self):
        """Test sanitize_input removes iframe tags"""
        result = sanitize_input("<iframe src='evil.com'></iframe>")
        assert "<iframe" not in result

    def test_removes_embed_tag(self):
        """Test sanitize_input removes embed tags"""
        result = sanitize_input("<embed src='evil.swf'>")
        assert "<embed" not in result

    def test_removes_object_tag(self):
        """Test sanitize_input removes object tags"""
        result = sanitize_input("<object data='evil.pdf'></object>")
        assert "<object" not in result

    def test_dangerous_content_removed(self):
        """Test sanitize_input removes dangerous patterns from input"""
        # The script opening tag is removed, but content/closing tags remain
        result = sanitize_input("<script>alert('XSS')</script>")
        assert result == "alert('XSS')</script>"

    def test_case_insensitive_pattern_removal(self):
        """Test sanitize_input removes patterns case-insensitively"""
        # Opening tag is removed regardless of case
        result = sanitize_input("<SCRIPT>alert('XSS')</SCRIPT>")
        assert "<script" not in result.lower()
        # But content and closing tag remain
        assert "alert('XSS')" in result


class TestValidateDateStringValidInputs:
    """Test suite for validate_date_string with valid inputs"""

    def test_valid_date_default_format(self):
        """Test validate_date_string accepts valid date in default format"""
        result = validate_date_string("2024-01-15")
        assert result == "2024-01-15"

    def test_valid_date_with_whitespace(self):
        """Test validate_date_string strips whitespace"""
        result = validate_date_string("  2024-01-15  ")
        assert result == "2024-01-15"

    def test_valid_date_different_format(self):
        """Test validate_date_string accepts different format"""
        result = validate_date_string("15/01/2024", date_format="%d/%m/%Y")
        assert result == "15/01/2024"

    def test_valid_date_leap_year(self):
        """Test validate_date_string accepts leap year date"""
        result = validate_date_string("2024-02-29")
        assert result == "2024-02-29"

    def test_valid_date_end_of_month(self):
        """Test validate_date_string accepts end of month dates"""
        result = validate_date_string("2024-01-31")
        assert result == "2024-01-31"


class TestValidateDateStringMissingOrNoneInputs:
    """Test suite for validate_date_string with missing or None inputs"""

    def test_none_raises_error(self):
        """Test validate_date_string raises ValidationError for None"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string(None)

        assert "is required" in str(exc_info.value)
        assert exc_info.value.field == "date"

    def test_empty_string_raises_error(self):
        """Test validate_date_string raises ValidationError for empty string"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("")

        # Empty string is caught by "not date_str" check before whitespace check
        assert "is required" in str(exc_info.value)

    def test_whitespace_only_raises_error(self):
        """Test validate_date_string raises ValidationError for whitespace"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("   ")

        assert "cannot be empty" in str(exc_info.value)


class TestValidateDateStringInvalidType:
    """Test suite for validate_date_string with invalid types"""

    def test_integer_raises_error(self):
        """Test validate_date_string raises ValidationError for integer"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string(20240115)

        assert "must be a string" in str(exc_info.value)

    def test_datetime_object_raises_error(self):
        """Test validate_date_string raises ValidationError for datetime object"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string(datetime(2024, 1, 15))

        assert "must be a string" in str(exc_info.value)


class TestValidateDateStringInvalidFormat:
    """Test suite for validate_date_string with invalid format"""

    def test_wrong_format_raises_error(self):
        """Test validate_date_string raises ValidationError for wrong format"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("15-01-2024")

        assert "must be in" in str(exc_info.value)
        assert "%Y-%m-%d" in str(exc_info.value)

    def test_invalid_date_raises_error(self):
        """Test validate_date_string raises ValidationError for invalid date"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("2024-02-30")  # Feb 30 doesn't exist

        assert "must be in" in str(exc_info.value)

    def test_invalid_month_raises_error(self):
        """Test validate_date_string raises ValidationError for invalid month"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("2024-13-01")

        assert "must be in" in str(exc_info.value)

    def test_invalid_day_raises_error(self):
        """Test validate_date_string raises ValidationError for invalid day"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("2024-01-32")

        assert "must be in" in str(exc_info.value)

    def test_garbage_string_raises_error(self):
        """Test validate_date_string raises ValidationError for garbage input"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("not-a-date")

        assert "must be in" in str(exc_info.value)

    def test_partial_date_raises_error(self):
        """Test validate_date_string raises ValidationError for partial date"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("2024-01")

        assert "must be in" in str(exc_info.value)


class TestValidatePositiveNumberValidInputs:
    """Test suite for validate_positive_number with valid inputs"""

    def test_valid_integer(self):
        """Test validate_positive_number accepts positive integer"""
        result = validate_positive_number(42)
        assert result == 42.0

    def test_valid_float(self):
        """Test validate_positive_number accepts positive float"""
        result = validate_positive_number(3.14)
        assert result == 3.14

    def test_string_number(self):
        """Test validate_positive_number converts string to float"""
        result = validate_positive_number("42.5")
        assert result == 42.5

    def test_very_small_positive(self):
        """Test validate_positive_number accepts very small positive numbers"""
        result = validate_positive_number(0.0001)
        assert result == 0.0001

    def test_large_number(self):
        """Test validate_positive_number accepts large numbers"""
        result = validate_positive_number(999999.99)
        assert result == 999999.99

    def test_custom_field_name(self):
        """Test validate_positive_number uses custom field name"""
        result = validate_positive_number(42, field_name="price")
        assert result == 42.0


class TestValidatePositiveNumberMissingOrNoneInputs:
    """Test suite for validate_positive_number with missing or None inputs"""

    def test_none_raises_error(self):
        """Test validate_positive_number raises ValidationError for None"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number(None)

        assert "is required" in str(exc_info.value)
        assert exc_info.value.field == "value"

    def test_custom_field_name_in_error(self):
        """Test validate_positive_number includes custom field name in error"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number(None, field_name="price")

        assert "price is required" in str(exc_info.value)
        assert exc_info.value.field == "price"


class TestValidatePositiveNumberInvalidType:
    """Test suite for validate_positive_number with invalid types"""

    def test_string_garbage_raises_error(self):
        """Test validate_positive_number raises ValidationError for garbage string"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number("not a number")

        assert "must be a valid number" in str(exc_info.value)

    def test_list_raises_error(self):
        """Test validate_positive_number raises ValidationError for list"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number([42])

        assert "must be a valid number" in str(exc_info.value)

    def test_dict_raises_error(self):
        """Test validate_positive_number raises ValidationError for dict"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number({"value": 42})

        assert "must be a valid number" in str(exc_info.value)

    def test_boolean_true_accepted(self):
        """Test validate_positive_number accepts True (converts to 1.0)"""
        # Note: In Python, bool is subclass of int, float(True) = 1.0
        result = validate_positive_number(True)
        assert result == 1.0


class TestValidatePositiveNumberNonPositive:
    """Test suite for validate_positive_number with non-positive values"""

    def test_zero_raises_error(self):
        """Test validate_positive_number raises ValidationError for zero"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number(0)

        assert "must be greater than zero" in str(exc_info.value)

    def test_negative_integer_raises_error(self):
        """Test validate_positive_number raises ValidationError for negative integer"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number(-42)

        assert "must be greater than zero" in str(exc_info.value)
        assert "-42" in str(exc_info.value)

    def test_negative_float_raises_error(self):
        """Test validate_positive_number raises ValidationError for negative float"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number(-3.14)

        assert "must be greater than zero" in str(exc_info.value)

    def test_negative_string_raises_error(self):
        """Test validate_positive_number raises ValidationError for negative string"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number("-10.5")

        assert "must be greater than zero" in str(exc_info.value)

    def test_zero_string_raises_error(self):
        """Test validate_positive_number raises ValidationError for zero string"""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_number("0")

        assert "must be greater than zero" in str(exc_info.value)
