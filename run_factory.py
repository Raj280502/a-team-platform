#!/usr/bin/env python3
"""
run_factory.py
--------------
Entry point for the AI Code Factory.

Usage:
    python run_factory.py "build a todo app with categories"
    python run_factory.py  # Interactive mode
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import run_pipeline, main


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        run_pipeline(prompt)
    else:
        main()
