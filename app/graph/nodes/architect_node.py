from app.agents.architect.node import build_architect_node
from app.core.state import ProjectState


def architect_node(state: ProjectState) -> ProjectState:
    architect = build_architect_node()

    result = architect.invoke(
        {"project_scope": state["project_scope"]}
    )

    return {
        "architecture": result.model_dump(),
        "file_plan": [
            "backend/app.py",
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx",
        ]
    }
