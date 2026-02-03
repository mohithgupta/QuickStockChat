#!/usr/bin/env python3
"""
Test Verification Script
Verifies test files are properly structured and can be imported
"""
import ast
import os
import sys
from pathlib import Path

def verify_test_file(filepath):
    """Verify a test file has proper structure"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)

        # Check for test classes and functions
        test_classes = []
        test_methods = []
        test_functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this is a test class (contains test methods)
                class_test_methods = []
                for item in node.body:
                    # Check both FunctionDef and AsyncFunctionDef
                    is_test = False
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith('test_'):
                            is_test = True
                            class_test_methods.append(f"{node.name}.{item.name}")

                if class_test_methods:
                    test_classes.append(node.name)
                    test_methods.extend(class_test_methods)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Module-level test functions
                if node.name.startswith('test_'):
                    test_functions.append(node.name)

        return {
            'valid': True,
            'classes': test_classes,
            'methods': test_methods,
            'functions': test_functions,
            'total_tests': len(test_methods) + len(test_functions)
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def main():
    """Main verification function"""
    test_files = [
        'tests/unit/test_config.py',
        'tests/unit/test_rate_limiter.py',
        'tests/unit/test_auth.py',
        'tests/unit/test_logger.py',
        'tests/integration/test_chat_endpoint.py',
        'tests/integration/test_health_endpoint.py',
        'tests/integration/test_rate_limiting.py',
        'tests/integration/test_auth.py',
        'tests/integration/test_cors.py',
    ]

    print("=" * 60)
    print("Test Structure Verification")
    print("=" * 60)
    print()

    total_tests = 0
    all_valid = True

    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"❌ {test_file}: File not found")
            all_valid = False
            continue

        result = verify_test_file(test_file)

        if result['valid']:
            class_count = len(result['classes'])
            method_count = len(result['methods'])
            func_count = len(result['functions'])
            test_count = result['total_tests']
            total_tests += test_count

            print(f"✓ {test_file}")
            if class_count > 0:
                print(f"  Classes: {class_count}, Methods: {method_count}, Functions: {func_count}, Total: {test_count}")
            else:
                print(f"  Functions: {func_count}, Total: {test_count}")
        else:
            print(f"❌ {test_file}: {result['error']}")
            all_valid = False

    print()
    print("=" * 60)
    print(f"Total Test Files: {len(test_files)}")
    print(f"Total Test Methods: {total_tests}")
    print("=" * 60)

    if all_valid:
        print("\n✓ All test files are properly structured!")
        return 0
    else:
        print("\n❌ Some test files have issues!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
