"""
user_stories_node.py — Stage 5: User Stories
Generates epics, sprints, and user stories in Agile format.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.core.state import ProjectState
from app.agents.sdlc.schemas import UserStoriesOutput

import json

_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Agile Product Owner. Generate comprehensive user stories organized by epics and sprints.

PROJECT OVERVIEW:
{project_overview}

REQUIREMENTS:
{requirements}

USER ROLES:
{user_roles}

TASK FLOWS:
{task_flows}

Generate:
1. **epics**: 3-5 epics, each with:
   - name: Epic name (e.g., "User Management", "Core Features")
   - description: What this epic covers
   - sprints: 1-2 sprints per epic, each with:
     - name: Sprint name (e.g., "Sprint 1")
     - goal: Sprint goal
     - stories: 3-6 user stories, each with:
       - id: Unique ID (US-001, US-002, ...)
       - title: Short story title
       - as_a: Role ("As a Customer")
       - i_want: Action ("I want to create an account")
       - so_that: Benefit ("So that I can save my preferences")
       - acceptance_criteria: 2-4 specific, testable criteria
       - priority: "must" / "should" / "could" / "wont"
       - story_points: Fibonacci (1, 2, 3, 5, 8, 13)

RULES:
- Stories must trace back to requirements and task flows
- Use actual role names from user research
- "must" priorities = MVP features
- "should" = important but not launch-blocking
- Story points reflect complexity (1=trivial, 13=very complex)
- Total: 15-30 stories across all sprints

{format_instructions}

OUTPUT: Valid JSON only, no markdown or explanations."""),
    ("human", "Generate user stories for: {user_prompt}"),
])


def user_stories_node(state: ProjectState) -> ProjectState:
    """Stage 5: Generate user stories organized by epics and sprints."""
    print("\n📖 USER STORIES: Generating epics & sprints...")

    llm = get_llm(role="user_stories")
    parser = PydanticOutputParser(pydantic_object=UserStoriesOutput)

    research = state.get("user_research", {})
    roles = research.get("roles", [])

    chain = _prompt.partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser

    result = chain.invoke({
        "user_prompt": state["user_prompt"],
        "project_overview": json.dumps(state.get("project_overview", {}), indent=2),
        "requirements": json.dumps(state.get("requirements", {}), indent=2),
        "user_roles": json.dumps(roles, indent=2),
        "task_flows": json.dumps(state.get("task_flows", {}), indent=2),
    })
    stories = result.model_dump()

    total_stories = sum(
        len(s.get("stories", []))
        for e in stories.get("epics", [])
        for s in e.get("sprints", [])
    )
    print(f"   📚 Epics: {len(stories.get('epics', []))}")
    print(f"   📝 Total Stories: {total_stories}")

    return {
        "user_stories": stories,
        "current_step": "user_stories_complete",
    }
