from pathlib import Path
import shutil

from app.core.state import ProjectState
from app.utils.file_ops import write_files


def write_files_node(state: ProjectState) -> ProjectState:
    """
    Writes generated files into a real project workspace and injects docker runtime.
    """

    project_dir = Path("app/workspace/generated_projects/todo_app")

    # Write AI generated files
    if state.get("files"):
        write_files(project_dir, state["files"])

    # Inject docker runtime into project workspace
    docker_src = Path("app/runtime/docker")
    docker_dst = project_dir / "docker"

    if docker_dst.exists():
        shutil.rmtree(docker_dst)
    if docker_src.exists():
        shutil.copytree(docker_src, docker_dst)

    return {}
