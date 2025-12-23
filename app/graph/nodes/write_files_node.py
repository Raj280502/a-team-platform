from pathlib import Path

from app.core.state import ProjectState
from app.utils.file_ops import write_files


def write_files_node(state: ProjectState) -> ProjectState:
    """
    Writes generated or repaired files to disk.
    """

    project_dir = Path("workspace/generated_projects/todo_app")

    if state["files"]:
        write_files(project_dir, state["files"])

    return state
