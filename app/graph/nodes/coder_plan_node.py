from app.core.state import ProjectState

def coder_plan_node(state: ProjectState) -> ProjectState:
    # MVP fixed file plan (later becomes LLM-generated)
    state["file_plan"] = [
        "backend/app.py",
        "frontend/src/App.js"
    ]
    return state
