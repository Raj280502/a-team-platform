from app.agents.coder.node import coder_node
from app.core.state import ProjectState


def generate_node(state: ProjectState) -> ProjectState:
    state["planned_files"] = state["file_plan"]
    result = coder_node(state)

    state["files"] = result.new_files
    return state
