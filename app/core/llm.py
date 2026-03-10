"""
llm.py
------
Centralized LLM initialization with Groq as the primary provider.
Supports streaming and role-based token limits.
"""

from langchain_groq import ChatGroq
from langchain_core.callbacks import BaseCallbackHandler
from .config import get_groq_api_key, GROQ_MODEL, TOKEN_LIMITS

# Cache per role
_LLM_POOL = {}

# Global streaming callback (set by web_ui for real-time streaming)
_streaming_callback = None


def set_streaming_callback(callback: BaseCallbackHandler):
    """Set a global streaming callback for all LLM calls."""
    global _streaming_callback
    _streaming_callback = callback


def _build_groq_llm(max_tokens: int, streaming: bool = False):
    """Build Groq LLM instance."""
    groq_key = get_groq_api_key()
    if not groq_key:
        raise ValueError(
            "GROQ_API_KEY not set in .env file. "
            "Get one at https://console.groq.com/keys"
        )

    callbacks = []
    if streaming and _streaming_callback:
        callbacks.append(_streaming_callback)

    return ChatGroq(
        api_key=groq_key,
        model=GROQ_MODEL,
        temperature=0,
        max_tokens=max_tokens,
        streaming=streaming,
        callbacks=callbacks if callbacks else None,
    )


def get_llm(role: str = "default", streaming: bool = False):
    """
    Returns an LLM instance for the given role.

    Args:
        role: One of 'strategist', 'architect', 'coder', 'repair', 'chat', 'default'
        streaming: Whether to enable streaming mode

    Returns:
        ChatGroq instance with role-appropriate token limits
    """
    cache_key = f"{role}_{'stream' if streaming else 'sync'}"

    if cache_key not in _LLM_POOL:
        max_tokens = TOKEN_LIMITS.get(role, TOKEN_LIMITS["default"])
        _LLM_POOL[cache_key] = _build_groq_llm(max_tokens, streaming=streaming)

    return _LLM_POOL[cache_key]


def clear_llm_pool():
    """Clear cached LLM instances (useful for config changes)."""
    global _LLM_POOL
    _LLM_POOL = {}


print("⚡ LLM module ready (Groq provider).")
