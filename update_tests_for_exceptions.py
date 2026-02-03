#!/usr/bin/env python3
"""
Script to update old unit tests to work with new exception-based error handling
"""
import re
import os

# Patterns to replace
replacements = [
    # Pattern 1: Error string returns for invalid ticker
    (
        r'result = ([a-z_]+)\(""\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1("")\n    assert "Ticker symbol is required" in str(exc_info.value)'
    ),
    # Pattern 2: Error string returns for None ticker
    (
        r'result = ([a-z_]+)\(None\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1(None)\n    assert "Ticker symbol is required" in str(exc_info.value)'
    ),
    # Pattern 3: Error string returns for non-string ticker
    (
        r'result = ([a-z_]+)\(123\)\s+assert result == "Error: Invalid ticker provided\. Please provide a valid ticker symbol\."',
        r'with pytest.raises(TickerValidationError) as exc_info:\n        \1(123)\n    assert "must be a string" in str(exc_info.value)'
    ),
]

def update_test_file(filepath):
    """Update a single test file"""
    print(f"Processing {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # If content changed, write it back
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes needed for {filepath}")
        return False

def main():
    """Main function"""
    test_files = [
        'tests/unit/test_tools_5_8.py',
        'tests/unit/test_tools_9_12.py',
        'tests/unit/test_tools_13_16.py',
    ]

    print("=" * 60)
    print("Updating Unit Tests for Exception-Based Error Handling")
    print("=" * 60)
    print()

    updated_count = 0
    for test_file in test_files:
        if os.path.exists(test_file):
            if update_test_file(test_file):
                updated_count += 1
        else:
            print(f"  ⚠ File not found: {test_file}")

    print()
    print(f"Updated {updated_count} test files")

if __name__ == '__main__':
    main()
