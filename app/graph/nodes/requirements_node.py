"""
requirements_node.py — Stage 2: Project Requirements
Generates functional/non-functional requirements, constraints, and assumptions.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.core.state import ProjectState
from app.agents.sdlc.schemas import RequirementsOutput

import json

_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Requirements Engineer. Based on the project overview, generate detailed project requirements.

PROJECT OVERVIEW:
{project_overview}

Generate:
1. **functional_requirements**: 8-15 functional requirements. Each must have:
   - id: Unique ID (FR-001, FR-002, ...)
   - title: Short title
   - description: Detailed description of what the system must do
   - priority: "high", "medium", or "low"
   - category: Group name (e.g., "Authentication", "Data Management", "UI/UX")

2. **non_functional_requirements**: 4-8 non-functional requirements:
   - id: NFR-001, NFR-002, ...
   - Areas: Performance, Security, Usability, Scalability, Reliability

3. **constraints**: 3-5 technical or business constraints

4. **assumptions**: 3-5 assumptions being made

Be thorough and use industry-standard requirement writing practices.

{format_instructions}

OUTPUT: Valid JSON only, no markdown or explanations."""),
    ("human", "Generate requirements for: {user_prompt}"),
])


def requirements_node(state: ProjectState) -> ProjectState:
    """Stage 2: Generate requirements from project overview."""
    print("\n📝 REQUIREMENTS: Generating project requirements...")

    llm = get_llm(role="strategist")
    parser = PydanticOutputParser(pydantic_object=RequirementsOutput)

    overview_str = json.dumps(state.get("project_overview", {}), indent=2)

    chain = _prompt.partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser

    result = chain.invoke({
        "user_prompt": state["user_prompt"],
        "project_overview": overview_str,
    })
    reqs = result.model_dump()

    fr_count = len(reqs.get("functional_requirements", []))
    nfr_count = len(reqs.get("non_functional_requirements", []))
    print(f"   ✅ Functional: {fr_count}, Non-functional: {nfr_count}")
    print(f"   🔒 Constraints: {len(reqs.get('constraints', []))}")

    return {
        "requirements": reqs,
        "current_step": "requirements_complete",
    }
