"""
llm.py
------
Multi-provider LLM with auto-fallback and retry.
- Tries primary provider first (Groq)
- If rate-limited, tries fallback (Gemini)
- If both fail, waits and retries (up to 2 retries)
"""

import time
import re
from langchain_groq import ChatGroq
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from .config import (
    get_groq_api_key, get_google_api_key,
    GROQ_MODEL, SDLC_LLM_PROVIDER, SDLC_GROQ_MODEL, SDLC_GEMINI_MODEL,
    TOKEN_LIMITS,
)

# Cache per role
_LLM_POOL = {}

# Global streaming callback (set by web_ui for real-time streaming)
_streaming_callback = None

# Roles that should use the SDLC provider (cheaper/faster)
SDLC_ROLES = {"sdlc", "overview", "requirements", "user_research", "task_flows", "user_stories"}


def set_streaming_callback(callback: BaseCallbackHandler):
    """Set a global streaming callback for all LLM calls."""
    global _streaming_callback
    _streaming_callback = callback


def _build_groq_llm(max_tokens: int, model: str = None, streaming: bool = False):
    """Build Groq LLM instance."""
    groq_key = get_groq_api_key()
    if not groq_key:
        return None

    callbacks = []
    if streaming and _streaming_callback:
        callbacks.append(_streaming_callback)

    try:
        return ChatGroq(
            api_key=groq_key,
            model=model or GROQ_MODEL,
            temperature=0,
            max_tokens=max_tokens,
            streaming=streaming,
            callbacks=callbacks if callbacks else None,
        )
    except Exception as e:
        print(f"   ⚠️ Groq init failed: {e}")
        return None


def _build_gemini_llm(max_tokens: int, model: str = None, streaming: bool = False):
    """Build Google Gemini LLM instance."""
    google_key = get_google_api_key()
    if not google_key:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model or SDLC_GEMINI_MODEL,
            google_api_key=google_key,
            temperature=0,
            max_output_tokens=max_tokens,
        )
    except ImportError:
        print("   ⚠️ langchain-google-genai not installed")
        return None
    except Exception as e:
        print(f"   ⚠️ Gemini init failed: {e}")
        return None


def _is_rate_limit_error(e):
    """Check if an exception is a rate limit / quota error."""
    err_str = str(e).lower()
    return any(kw in err_str for kw in ["429", "rate_limit", "quota", "resource_exhausted", "resourceexhausted"])


def _extract_retry_delay(e):
    """Extract retry delay from error message, default 35s."""
    err_str = str(e)
    match = re.search(r'retry.?in\s+([\d.]+)', err_str, re.IGNORECASE)
    if match:
        return min(float(match.group(1)), 60)  # Cap at 60s
    return 35


class FallbackLLM(BaseChatModel):
    """
    Wrapper that tries primary → fallback → retry with delay.
    """
    primary: BaseChatModel
    fallback: BaseChatModel = None
    role_name: str = "default"
    max_retries: int = 2

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self):
        return "fallback-llm"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Try primary → fallback → wait & retry."""
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            # Try primary
            try:
                result = self.primary._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                if attempt > 1:
                    print(f"   ✅ {self.role_name}: Succeeded on retry {attempt}")
                return result
            except Exception as e:
                primary_name = type(self.primary).__name__
                if _is_rate_limit_error(e):
                    print(f"   ⚠️ {self.role_name}: {primary_name} rate limited")
                else:
                    print(f"   ⚠️ {self.role_name}: {primary_name} error: {str(e)[:100]}")
                last_error = e

            # Try fallback
            if self.fallback:
                try:
                    fallback_name = type(self.fallback).__name__
                    print(f"   🔄 {self.role_name}: Trying {fallback_name}...")
                    return self.fallback._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                except Exception as e2:
                    if _is_rate_limit_error(e2):
                        print(f"   ⚠️ {self.role_name}: {fallback_name} also rate limited")
                    else:
                        print(f"   ⚠️ {self.role_name}: {fallback_name} error: {str(e2)[:100]}")
                    last_error = e2

            # Both failed — wait and retry if we have attempts left
            if attempt < self.max_retries:
                delay = _extract_retry_delay(last_error)
                print(f"   ⏳ {self.role_name}: Both providers busy. Waiting {delay:.0f}s before retry {attempt + 1}...")
                time.sleep(delay)

        # All retries exhausted
        raise last_error


def get_llm(role: str = "default", streaming: bool = False):
    """
    Returns an LLM instance with auto-fallback + retry.
    """
    cache_key = f"{role}_{'stream' if streaming else 'sync'}"

    if cache_key not in _LLM_POOL:
        max_tokens = TOKEN_LIMITS.get(role, TOKEN_LIMITS.get("sdlc" if role in SDLC_ROLES else "default", 4000))

        is_sdlc = role in SDLC_ROLES

        # Build both providers
        groq_model = SDLC_GROQ_MODEL if is_sdlc else GROQ_MODEL
        groq_llm = _build_groq_llm(max_tokens, model=groq_model, streaming=streaming)
        gemini_llm = _build_gemini_llm(max_tokens, streaming=streaming)

        # Select primary and fallback
        if groq_llm and gemini_llm:
            primary_name = f"Groq ({groq_model})"
            fallback_name = f"Gemini ({SDLC_GEMINI_MODEL})"
            print(f"   🟢 {role} → {primary_name} (fallback: {fallback_name})")
            _LLM_POOL[cache_key] = FallbackLLM(
                primary=groq_llm,
                fallback=gemini_llm,
                role_name=role,
            )
        elif groq_llm:
            print(f"   🔵 {role} → Groq ({groq_model})")
            _LLM_POOL[cache_key] = groq_llm
        elif gemini_llm:
            print(f"   🟣 {role} → Gemini ({SDLC_GEMINI_MODEL})")
            _LLM_POOL[cache_key] = gemini_llm
        else:
            raise ValueError(f"No LLM provider available for role '{role}'.")

    return _LLM_POOL[cache_key]


def clear_llm_pool():
    """Clear cached LLM instances."""
    global _LLM_POOL
    _LLM_POOL = {}


print("⚡ LLM module ready (Groq ↔ Gemini with auto-retry).")
