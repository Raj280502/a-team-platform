"""
overview_node.py — Stage 1: Project Overview
Generates high-level project vision, goals, target audience, and timeline.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.core.state import ProjectState
from app.agents.sdlc.schemas import ProjectOverviewOutput


_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an elite Product Strategist. Analyze the user's project idea and produce a comprehensive project overview.

Generate:
1. **title**: A catchy, professional project title
2. **description**: 2-3 sentence description of the project
3. **goals**: 3-5 specific, measurable project goals
4. **target_audience**: Detailed description of who will use this
5. **key_metrics**: 3-5 success KPIs
6. **tech_recommendations**: Recommended tech stack with brief justification
7. **timeline_estimate**: Rough development timeline (e.g., "4-6 weeks")
8. **domain**: Project domain category

Be thorough and professional. Think like a senior product manager at a top tech company.

{format_instructions}

OUTPUT: Valid JSON only, no markdown or explanations."""),
    ("human", "{user_prompt}"),
])


def overview_node(state: ProjectState) -> ProjectState:
    """Stage 1: Generate project overview from user prompt."""
    print("\n📋 OVERVIEW: Generating project overview...")

    llm = get_llm(role="overview")
    parser = PydanticOutputParser(pydantic_object=ProjectOverviewOutput)

    chain = _prompt.partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser

    result = chain.invoke({"user_prompt": state["user_prompt"]})
    overview = result.model_dump()

    print(f"   📌 Title: {overview['title']}")
    print(f"   🎯 Goals: {len(overview['goals'])}")
    print(f"   👥 Audience: {overview['target_audience'][:60]}")

    return {
        "project_overview": overview,
        "current_step": "overview_complete",
    }
