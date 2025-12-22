from app.agents.architect.node import build_architect_node
from app.core.state import ProjectState


def architect_node(state: ProjectState) -> ProjectState:
    architect = build_architect_node()

    result = architect.invoke(
        {"project_scope": state["project_scope"]}
    )

    state["architecture"] = result.model_dump()
    return state
