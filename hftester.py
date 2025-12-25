#!/usr/bin/env python3
"""
hftester.py
-----------
Test script to check Hugging Face API key loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key
hf_api_key = os.getenv('HF_API_KEY')

if hf_api_key:
    print(f"HF_API_KEY is loaded: {hf_api_key[:10]}... (masked for security)")
    print(f"Full length: {len(hf_api_key)} characters")
else:
    print("HF_API_KEY is not set in environment.")

# Optional: Test a simple API call (commented out to avoid quota issues)
# from huggingface_hub import HfApi
# api = HfApi(token=hf_api_key)
# try:
#     user = api.whoami()
#     print(f"Authenticated as: {user['name']}")
# except Exception as e:
#     print(f"API test failed: {e}")