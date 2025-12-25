from app.core.state import ProjectState

def coder_plan_node(state: ProjectState) -> ProjectState:
    # MVP fixed file plan (later becomes LLM-generated)
    return {
        "file_plan": [
            "backend/app.py",
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx"
        ]
    }
