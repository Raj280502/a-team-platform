from app.agents.coder.node import build_generate_node
from app.core.state import ProjectState


def generate_node(state: ProjectState) -> ProjectState:
    generator = build_generate_node()

    result = generator.invoke(
        {
            "project_scope": state["project_scope"],
            "architecture": state["architecture"],
        }
    )

    state["files"] = result.new_files
    return state
