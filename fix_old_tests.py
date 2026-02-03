#!/usr/bin/env python3
"""
Comprehensive script to update old unit tests for new exception-based error handling
"""
import re
from pathlib import Path

def fix_test_file(filepath):
    """Fix all error string assertions in a test file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Add imports if not present
    if 'from MarketInsight.utils.exceptions import' not in content:
        # Find the first import block and add our imports
        import_marker = 'import pytest'
        if import_marker in content:
            content = content.replace(
                import_marker,
                f'''import pytest
from MarketInsight.utils.exceptions import TickerValidationError, ExternalServiceError, ValidationError
'''
            )

    # Pattern 1: Empty string ticker tests
    content = re.sub(
        r'result = ([a-z_]+)\(""\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1("")\n    assert "Ticker symbol is required" in str(exc_info.value)',
        content,
        flags=re.MULTILINE
    )

    # Pattern 2: None ticker tests
    content = re.sub(
        r'result = ([a-z_]+)\(None\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1(None)\n    assert "Ticker symbol is required" in str(exc_info.value)',
        content,
        flags=re.MULTILINE
    )

    # Pattern 3: Non-string ticker (123) tests
    content = re.sub(
        r'result = ([a-z_]+)\(123\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1(123)\n    assert "must be a string" in str(exc_info.value)',
        content,
        flags=re.MULTILINE
    )

    # Pattern 4: General "Error:" prefix returns
    content = re.sub(
        r'assert result == "Error: Failed to retrieve ([^.]+)\. Please try again later\."',
        r'with pytest.raises(ExternalServiceError) as exc_info:\n        raise AssertionError("Fix this test manually")',
        content,
        flags=re.MULTILINE
    )

    # Pattern 5: "No {data} available" returns
    content = re.sub(
        r'assert result == "No ([^.]+) available for \{ticker\}"',
        r'with pytest.raises(ExternalServiceError) as exc_info:\n        raise AssertionError("Fix this test manually")',
        content,
        flags=re.MULTILINE
    )

    # Pattern 6: Exception handling tests that return error strings
    content = re.sub(
        r'# Execute\s+result = ([a-z_]+)\([^)]+\)\s+# Verify\s+assert result == "Error: ([^.]+)\.',
        r'# Execute & Verify\n        from MarketInsight.utils.exceptions import ExternalServiceError\n        with pytest.raises(ExternalServiceError):\n            \1',
        content,
        flags=re.MULTILINE
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    test_files = [
        'tests/unit/test_tools_5_8.py',
        'tests/unit/test_tools_9_12.py',
        'tests/unit/test_tools_13_16.py',
    ]

    print("Fixing old unit tests...")
    for filepath in test_files:
        if Path(filepath).exists():
            if fix_test_file(filepath):
                print(f"✓ Fixed {filepath}")
            else:
                print(f"- No changes to {filepath}")
        else:
            print(f"✗ File not found: {filepath}")

if __name__ == '__main__':
    main()
