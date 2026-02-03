#!/usr/bin/env python3
"""
Run test suite and show results
"""
import subprocess
import sys

def run_tests():
    """Run the test suite"""
    cmd = [
        sys.executable,
        '-m', 'pytest',
        'tests/',
        '-v',
        '--cov=MarketInsight',
        '--cov=config',
        '--cov=main',
        '--tb=short',
        '-x'  # Stop on first failure
    ]

    print("Running test suite...")
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=False, text=True)

    print("=" * 60)
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ Tests failed with exit code {result.returncode}")

    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())
