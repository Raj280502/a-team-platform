"""
task_flows_node.py — Stage 4: Task Flows
Generates user journey flowcharts with nodes and edges for ReactFlow rendering.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.core.state import ProjectState
from app.agents.sdlc.schemas import TaskFlowsOutput

import json

_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a UX Designer specializing in user flows and journeys. Generate detailed task flows for the project.

PROJECT OVERVIEW:
{project_overview}

USER ROLES:
{user_roles}

REQUIREMENTS:
{requirements}

Generate 4-7 task flows. For EACH flow:
1. **name**: Flow name (e.g., "User Registration", "Order Processing")
2. **description**: What this flow covers
3. **primary_roles**: Which user roles are primarily involved
4. **secondary_roles**: Supporting roles
5. **steps**: Ordered list of flow steps. Each step has:
   - id: Unique ID (e.g., "step_1", "step_2")
   - label: Display text (e.g., "Enter Email", "Validate Input")
   - type: One of "start", "action", "decision", "end", "system"
     - "start": Entry point (green)
     - "action": User or system action (blue)
     - "decision": Yes/No branch (yellow diamond)
     - "system": Background system action (gray)
     - "end": Terminal node (red)
   - next_steps: List of connections, each with:
     - target_id: ID of the next step
     - label: Edge label (use "Yes"/"No" for decisions, "" for regular flow)

FLOW DESIGN RULES:
- Each flow MUST start with a "start" type node and end with an "end" type node
- Decisions MUST have exactly 2 next_steps (Yes and No branches)
- Actions should have 1 next_step unless branching
- Keep flows between 5-12 steps
- Make flows realistic and comprehensive
- Cover key user journeys: onboarding, core actions, admin tasks

{format_instructions}

OUTPUT: Valid JSON only, no markdown or explanations."""),
    ("human", "Generate task flows for: {user_prompt}"),
])


def task_flows_node(state: ProjectState) -> ProjectState:
    """Stage 4: Generate task flows with diagram structure."""
    print("\n🔄 TASK FLOWS: Generating user journeys...")

    llm = get_llm(role="strategist")
    parser = PydanticOutputParser(pydantic_object=TaskFlowsOutput)

    # Extract roles from user_research
    research = state.get("user_research", {})
    roles = research.get("roles", [])
    roles_str = json.dumps(roles, indent=2)

    chain = _prompt.partial(
        format_instructions=parser.get_format_instructions()
    ) | llm | parser

    result = chain.invoke({
        "user_prompt": state["user_prompt"],
        "project_overview": json.dumps(state.get("project_overview", {}), indent=2),
        "requirements": json.dumps(state.get("requirements", {}), indent=2),
        "user_roles": roles_str,
    })
    flows = result.model_dump()

    print(f"   📊 Task Flows: {len(flows.get('flows', []))}")
    for f in flows.get("flows", []):
        print(f"      - {f['name']} ({len(f.get('steps', []))} steps)")

    return {
        "task_flows": flows,
        "current_step": "task_flows_complete",
    }
