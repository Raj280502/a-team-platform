from pathlib import Path
from app.runtime.runner import run_project
from app.core.state import ProjectState

def docker_node(state: ProjectState) -> ProjectState:
    project_dir = Path("app/workspace/generated_projects/todo_app").resolve()
    run_project(project_dir)
    return {}
