"""
config.py
----------
Centralized configuration management for the platform.
Loads environment variables and provides typed access.
"""

from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()


def get_hf_api_key() -> str:
    """Returns the Hugging Face API key from environment variables."""
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY not found. Please set it in the .env file.")
    return api_key


def get_groq_api_key() -> str:
    """Returns the Groq API key from environment variables."""
    return os.getenv("GROQ_API_KEY")


# ---------- Platform Configuration ----------

# LLM settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq | huggingface
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Token limits per role
TOKEN_LIMITS = {
    "strategist": 4000,
    "architect": 4000,
    "coder": 16000,   # High limit for complete file generation
    "repair": 16000,
    "chat": 8000,     # For iterative refinement
    "default": 4000,
}

# Supported tech stacks
SUPPORTED_STACKS = ["react-flask", "nextjs", "vue-flask", "html-css-js", "react-express"]
DEFAULT_STACK = "react-flask"

# Preview configuration
PREVIEW_BACKEND_PORT = int(os.getenv("PREVIEW_BACKEND_PORT", "5000"))
PREVIEW_FRONTEND_PORT = int(os.getenv("PREVIEW_FRONTEND_PORT", "5173"))

# Project workspace
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "app/workspace/generated_projects")


# ---------- Validation ----------
print("✅ Configuration module loaded.")
if get_groq_api_key():
    print(f"   LLM Provider: {LLM_PROVIDER} ({GROQ_MODEL})")
else:
    print("   ⚠️ GROQ_API_KEY not set — LLM calls will fail")