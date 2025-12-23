from pathlib import Path

from app.core.state import ProjectState
from app.runtime.runner import run_project


def docker_node(state: ProjectState) -> ProjectState:
    project_dir = Path("workspace/generated_projects/todo_app")

    run_project(project_dir)

    return state
