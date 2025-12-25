from app.agents.strategist.node import build_strategist_node
from app.core.state import ProjectState


def strategist_node(state: ProjectState) -> ProjectState:
    strategist = build_strategist_node()

    result = strategist.invoke(
        {"user_prompt": state["user_prompt"]}
    )

    return {"project_scope": result.model_dump()}
