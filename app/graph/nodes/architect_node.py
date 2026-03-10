"""
architect_node.py - Designs system architecture and builds file plan.
Enhanced with component-based architecture and dynamic file planning.
"""

from app.agents.architect.node import build_architect_node
from app.core.state import ProjectState


def architect_node(state: ProjectState) -> ProjectState:
    """
    Architect agent: designs the system architecture.
    Produces API routes, component hierarchy, and dynamic file plan.
    """
    print("\n📐 ARCHITECT: Designing system architecture...")

    architect = build_architect_node()

    result = architect.invoke(
        {"project_scope": state["project_scope"]}
    )

    architecture = result.model_dump()

    # Dynamically determine file plan based on architecture output
    file_plan = generate_file_plan(architecture)

    print(f"   Backend: {architecture.get('backend', 'Flask')}")
    print(f"   Frontend: {architecture.get('frontend', 'React')}")
    print(f"   API Routes: {len(architecture.get('api_routes', []))}")
    print(f"   Components: {len(architecture.get('components', []))}")
    print(f"   📁 File plan ({len(file_plan)} files): {file_plan}")

    return {
        "architecture": architecture,
        "file_plan": file_plan,
        "current_step": "architect_complete",
    }


def generate_file_plan(architecture: dict) -> list:
    """
    Dynamically generate file plan based on architecture.
    Includes component files from the architecture output.
    """
    files = []

    # ---------- Backend ----------
    backend = architecture.get("backend", "").lower()
    if "flask" in backend or "python" in backend or not backend:
        files.append("backend/app.py")
        files.append("backend/requirements.txt")
    elif "express" in backend or "node" in backend:
        files.append("backend/server.js")
        files.append("backend/package.json")

    # ---------- Frontend core ----------
    frontend = architecture.get("frontend", "").lower()
    if "react" in frontend or not frontend:
        files.extend([
            "frontend/package.json",
            "frontend/index.html",
            "frontend/vite.config.js",
            "frontend/src/main.jsx",
            "frontend/src/App.jsx",
            "frontend/src/App.css",
            "frontend/src/index.css",
        ])

        # Add component files from architecture
        components = architecture.get("components", [])
        for comp in components:
            comp_path = comp.get("file_path", "")
            if comp_path and comp_path not in files:
                files.append(comp_path)

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
