"""
strategist_node.py - First node in the pipeline.
Analyzes user requirements and produces rich project specification.
"""

from app.agents.strategist.node import build_strategist_node
from app.core.state import ProjectState


def strategist_node(state: ProjectState) -> ProjectState:
    """
    Strategist agent: analyzes the user prompt and extracts
    project goal, features, pages, data models, API endpoints.
    """
    print("\n🧠 STRATEGIST: Analyzing requirements...")

    strategist = build_strategist_node()

    result = strategist.invoke(
        {"user_prompt": state["user_prompt"]}
    )

    scope = result.model_dump()

    print(f"   📋 Goal: {scope.get('project_goal', 'N/A')}")
    print(f"   👥 Users: {scope.get('target_users', 'N/A')}")
    print(f"   ⭐ Features ({len(scope.get('core_features', []))}): {scope.get('core_features', [])[:3]}...")
    print(f"   📄 Pages: {[p.get('name') for p in scope.get('pages', [])]}")
    print(f"   📊 Data models: {scope.get('data_models', [])}")
    print(f"   🔗 API endpoints: {len(scope.get('api_endpoints', []))}")

    return {
        "project_scope": scope,
        "current_step": "strategist_complete",
    }
