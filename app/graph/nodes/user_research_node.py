"""
user_research_node.py — Stage 3: User Research
Generates user roles, personas with demographics, goals, pain points, and empathy maps.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.core.state import ProjectState
from app.agents.sdlc.schemas import UserResearchOutput

import json

_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a UX Research expert. Based on the project context, generate comprehensive user research.

PROJECT OVERVIEW:
{project_overview}

REQUIREMENTS:
{requirements}

Generate:
1. **roles**: 4-7 user roles that interact with the system. Each has:
   - name: Role name (e.g., "Admin", "Customer", "Manager")
   - description: How this role interacts with the system

2. **personas**: 2-4 detailed user personas. For EACH persona:
   - name: A realistic full name
   - age: Realistic age (20-65)
   - occupation: Job title
   - location: City, Country
   - role: Which user role this persona represents
   - goals: 3-5 specific goals they want to achieve with this system
   - key_characteristics: 3-5 personality/behavioral traits
   - pain_points: 3-5 frustrations or challenges
   - empathy_map:
     - thinks: 3-4 thoughts about using such a system
     - feels: 3-4 emotional responses
     - says: 3-4 things they would say about the product
     - does: 3-4 actions they take

Make personas feel REAL with specific details. Each should represent a different user role.

{format_instructions}

OUTPUT: Valid JSON only, no markdown or explanations."""),
    ("human", "Generate user research for: {user_prompt}"),
])


def user_research_node(state: ProjectState) -> ProjectState:
    """Stage 3: Generate user research (roles + personas)."""
    print("\n👥 USER RESEARCH: Generating roles & personas...")

    llm = get_llm(role="user_research")
    parser = PydanticOutputParser(pydantic_object=UserResearchOutput)

    chain = _prompt.partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser

    result = chain.invoke({
        "user_prompt": state["user_prompt"],
        "project_overview": json.dumps(state.get("project_overview", {}), indent=2),
        "requirements": json.dumps(state.get("requirements", {}), indent=2),
    })
    research = result.model_dump()

    print(f"   👤 Roles: {len(research.get('roles', []))}")
    print(f"   🧑 Personas: {len(research.get('personas', []))}")
    for p in research.get("personas", []):
        print(f"      - {p['name']} ({p['role']})")

    return {
        "user_research": research,
        "current_step": "user_research_complete",
    }
