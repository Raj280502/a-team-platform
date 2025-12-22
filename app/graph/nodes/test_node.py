from pathlib import Path

from app.runtime.test_runner import run_basic_backend_test
from app.core.state import ProjectState


def test_node(state: ProjectState) -> ProjectState:
    project_dir = Path("workspace/generated_projects/todo_app")

    passed, error = run_basic_backend_test(project_dir)

    state["tests_passed"] = passed
    state["error_message"] = error

    return state
