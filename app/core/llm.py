"""
llm.py
------
This file defines a SINGLE place where the LLM is initialized.

Why this file is critical:
- Prevents reloading the model multiple times
- Keeps configuration consistent
- Makes the system scalable and maintainable
"""

# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
# from .config import get_hf_api_key

# # Internal singleton instance
# _llm_instance = None


# def get_llm():
#     """
#     Returns a shared LLM instance.

#     Design pattern used:
#     - Singleton (one LLM for the entire application)

#     Why:
#     - Efficient
#     - Easy to swap models
#     - Avoids repeated authentication
#     """
#     global _llm_instance

#     if _llm_instance is None:
#         api_key = get_hf_api_key()

#         # Hugging Face inference client
#         endpoint = HuggingFaceEndpoint(
#             repo_id="Qwen/Qwen2.5-72B-Instruct",
#             task="text-generation",
#             huggingfacehub_api_token=api_key,
#         )

#         _llm_instance = ChatHuggingFace(llm=endpoint, temperature=0, max_new_tokens=5000, do_sample=False, top_p=0.95)
       
#     return _llm_instance
# print("LLM module loaded. Use get_llm() to access the model.")
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq
from .config import get_hf_api_key, get_groq_api_key

# Cache per role
_LLM_POOL = {}
_USE_GROQ = False  # Switch to True if HuggingFace fails

def _build_hf_llm(repo_id: str, max_tokens: int):
    """Build HuggingFace LLM."""
    return ChatHuggingFace(
        llm=HuggingFaceEndpoint(
            repo_id=repo_id,
            task="text-generation",
            huggingfacehub_api_token=get_hf_api_key(),
        ),
        temperature=0,
        do_sample=False,
        max_new_tokens=max_tokens,
    )

def _build_groq_llm(max_tokens: int):
    """Build Groq LLM as fallback."""
    groq_key = get_groq_api_key()
    if not groq_key:
        raise ValueError("GROQ_API_KEY not set in .env file")
    
    return ChatGroq(
        api_key=groq_key,
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=max_tokens,
    )

def _build_llm(repo_id: str, max_tokens: int):
    """Build LLM with automatic fallback to Groq."""
    global _USE_GROQ
    
    # If already switched to Groq, use it
    if _USE_GROQ:
        print("⚡ Using Groq API (HuggingFace fallback)")
        return _build_groq_llm(max_tokens)
    
    # Try HuggingFace first
    try:
        return _build_hf_llm(repo_id, max_tokens)
    except Exception as e:
        error_str = str(e).lower()
        # Check if it's a rate limit or token error
        if "rate" in error_str or "limit" in error_str or "quota" in error_str or "token" in error_str:
            print(f"⚠️ HuggingFace token limit reached: {e}")
            print("🔄 Switching to Groq API...")
            _USE_GROQ = True
            return _build_groq_llm(max_tokens)
        else:
            # Re-raise if it's not a token issue
            raise

def get_llm(role: str = "default"):
    if role not in _LLM_POOL:

        # Heavy reasoning model - needs high tokens for complex planning
        if role in ("strategist", "architect"):
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-72B-Instruct", max_tokens=4000
            )

        # Fast, deterministic code model - needs very high tokens for full files
        elif role in ("coder", "repair"):
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-72B-Instruct", max_tokens=8000
            )

        # Fallback
        else:
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-7B-Instruct", max_tokens=4000
            )

    return _LLM_POOL[role]

print("Multi-role LLM loader ready.")
