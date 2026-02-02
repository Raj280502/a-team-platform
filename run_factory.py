#!/usr/bin/env python3
"""
run_factory.py
--------------
Simple runner script for the AI Code Factory.

Usage:
    python run_factory.py "your app description"
    python run_factory.py  # Interactive mode
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line argument
        prompt = " ".join(sys.argv[1:])
        main(prompt)
    else:
        # Interactive mode
        main()
