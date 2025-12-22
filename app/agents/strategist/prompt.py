"""
prompt.py
---------
Contains the prompt template for the Strategist agent.

Why this file exists:
- Keeps prompts separate from logic
- Easy to tweak without touching code
- Improves readability and maintainability
"""

from langchain_core.prompts import ChatPromptTemplate


# Prompt template for the Strategist agent
strategist_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Senior Software Product Strategist.

Your task is to analyze a user's idea and clearly define:
1. The main goal of the project
2. Target users
3. Core features
4. Technical constraints

{format_instructions}

IMPORTANT RULES:
- Respond with VALID JSON only
- Do NOT include explanations
- Do NOT repeat the input
"""
        ),
        (
            "human",
            "{user_prompt}"
        ),
    ]
)
