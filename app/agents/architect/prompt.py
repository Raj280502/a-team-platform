"""
prompt.py
---------
Prompt template for the Architect agent.

This agent converts project scope into
a concrete technical architecture.
"""

from langchain_core.prompts import ChatPromptTemplate


architect_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Senior Software Architect.

Your task is to design a technical architecture
for the given project scope.

Decide:
1. Backend framework
2. Frontend framework
3. Services involved
4. Port configuration
5. Runtime environment

{format_instructions}

IMPORTANT RULES:
- Respond with VALID JSON only
- Do NOT include explanations
- Do NOT include assumptions outside MVP scope
"""
        ),
        (
            "human",
            """
Project Scope:
{project_scope}
"""
        ),
    ]
)
