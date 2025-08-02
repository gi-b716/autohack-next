#!/usr/bin/env python3
"""
Test script for internationalization.
"""
import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from i18n import setup_i18n, _


def test_i18n():
    print("Testing internationalization...")

    # Test English (default)
    setup_i18n("en_US")
    print(f"English: {_('Data folder path: \"{0}\"').format('/path/to/data')}")
    print(f"English: {_('Compile finished.')}")
    print(f"English: {_('No differences found.')}")

    # Test Chinese
    setup_i18n("zh_CN")
    print(f"Chinese: {_('Data folder path: \"{0}\"').format('/path/to/data')}")
    print(f"Chinese: {_('Compile finished.')}")
    print(f"Chinese: {_('No differences found.')}")

    # Test auto-detection (should default to system locale)
    setup_i18n()
    print(f"Auto: {_('Data folder path: \"{0}\"').format('/path/to/data')}")


if __name__ == "__main__":
    test_i18n()
