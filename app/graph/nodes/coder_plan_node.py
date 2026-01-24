from app.core.state import ProjectState


def coder_plan_node(state: ProjectState) -> ProjectState:
    """
    Defines the MVP file plan AND initializes route container.
    """

    return {
        "file_plan": [
            "backend/app.py",
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx",
        ],

        # 🔥 VERY IMPORTANT — initialize this for later nodes
        "extracted_routes": []
    }
