from app.agents.architect.node import build_architect_node
from app.core.state import ProjectState


def architect_node(state: ProjectState) -> ProjectState:
    """
    Architect agent that designs the system architecture.
    
    Now GENERALIZED - doesn't hardcode file plan.
    File plan is determined dynamically based on architecture.
    """
    architect = build_architect_node()

    result = architect.invoke(
        {"project_scope": state["project_scope"]}
    )

    architecture = result.model_dump()
    
    # Dynamically determine file plan based on architecture
    file_plan = generate_file_plan(architecture)
    
    print(f"📐 Architecture designed: {architecture.get('backend', 'Flask')} + {architecture.get('frontend', 'React')}")
    print(f"📁 File plan: {file_plan}")

    return {
        "architecture": architecture,
        "file_plan": file_plan
    }


def generate_file_plan(architecture: dict) -> list:
    """
    Dynamically generate file plan based on architecture.
    
    Supports any type of application, not just specific templates.
    """
    files = []
    
    # Backend files
    backend = architecture.get("backend", "").lower()
    if "flask" in backend or "python" in backend or backend == "":
        files.append("backend/app.py")
        files.append("backend/requirements.txt")
    elif "fastapi" in backend:
        files.append("backend/main.py")
        files.append("backend/requirements.txt")
    elif "express" in backend or "node" in backend:
        files.append("backend/server.js")
        files.append("backend/package.json")
    
    # Frontend files
    frontend = architecture.get("frontend", "").lower()
    if "react" in frontend or frontend == "":
        files.extend([
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx",
            "frontend/src/App.css",
        ])
    elif "vue" in frontend:
        files.extend([
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.js",
            "frontend/src/App.vue",
        ])
    elif "html" in frontend or "vanilla" in frontend:
        files.extend([
            "frontend/index.html",
            "frontend/style.css",
            "frontend/script.js",
        ])
    
    return files
