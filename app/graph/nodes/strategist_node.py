"""
strategist_node.py
------------------
First node in the pipeline - analyzes user requirements.
"""

from app.agents.strategist.node import build_strategist_node
from app.core.state import ProjectState


def strategist_node(state: ProjectState) -> ProjectState:
    """
    Strategist agent that analyzes the user prompt.
    
    Extracts:
    - Project goal
    - Target users
    - Core features
    - Technical constraints
    """
    print("\n🧠 STRATEGIST: Analyzing requirements...")
    
    strategist = build_strategist_node()

    result = strategist.invoke(
        {"user_prompt": state["user_prompt"]}
    )
    
    scope = result.model_dump()
    
    print(f"   📋 Goal: {scope.get('project_goal', 'N/A')}")
    print(f"   👥 Users: {scope.get('target_users', 'N/A')}")
    print(f"   ⭐ Features: {scope.get('core_features', [])}")

    return {"project_scope": scope}
