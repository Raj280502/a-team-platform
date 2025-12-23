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
You are a Software Architect designing a MINIMAL MVP system.

Your task is to produce a SIMPLE and CONSISTENT architecture.

STRICT RULES (DO NOT VIOLATE):
- Use EXACTLY ONE backend service
- Backend MUST be Flask
- Backend service name MUST be "backend"
- Backend MUST run on port 5000
- NO authentication services
- NO databases (no SQLite, no Postgres)
- Use in-memory data only
- Frontend MUST be React
- DO NOT add extra services
- DO NOT add Docker unless explicitly required

Return ONLY valid JSON that follows the schema.

{format_instructions}
"""
        ),
        (
            "human",
            """
Project Scope:
{project_scope}

Generate the system architecture for the MVP.
"""
        ),
    ]
)
