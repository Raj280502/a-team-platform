"""
config.py
----------
This file is responsible for loading and managing
all environment-level configuration for the platform.
"""

from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()


def get_hf_api_key() -> str:
    """
    Returns the Hugging Face API key from environment variables.

    Why this function exists:
    - Centralizes config access
    - Avoids using os.getenv() everywhere
    - Easy to modify later (vault, secrets manager, etc.)
    """
    api_key = os.getenv("HF_API_KEY")

    if not api_key:
        raise ValueError(
            "HF_API_KEY not found. Please set it in the .env file."
        )

    return api_key
get_hf_api_key()
print("Configuration module loaded. HF_API_KEY is set.")