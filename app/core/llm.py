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
from .config import get_hf_api_key

# Cache per role
_LLM_POOL = {}

def _build_llm(repo_id: str, max_tokens: int):
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

def get_llm(role: str = "default"):
    if role not in _LLM_POOL:

        # Heavy reasoning model
        if role in ("strategist", "architect"):
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-72B-Instruct", max_tokens=204
            )

        # Fast, deterministic code model
        elif role in ("coder", "repair"):
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-7B-Instruct", max_tokens=600
            )

        # Fallback
        else:
            _LLM_POOL[role] = _build_llm(
                "Qwen/Qwen2.5-7B-Instruct", max_tokens=204
            )

    return _LLM_POOL[role]

print("Multi-role LLM loader ready.")
