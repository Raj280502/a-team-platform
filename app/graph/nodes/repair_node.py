from pathlib import Path

from app.agents.coder.node import build_repair_node
from app.core.state import ProjectState


def repair_node(state: ProjectState) -> ProjectState:
    repairer = build_repair_node()
    project_dir = Path("app/workspace/generated_projects/todo_app")

    existing_files = {
        p.relative_to(project_dir).as_posix(): p.read_text(encoding="utf-8")
        for p in project_dir.rglob("*")
        if p.is_file()
    }

    result = repairer.invoke(
        {
            "existing_files": existing_files,
            "error_message": state["error_message"],
        }
    )

    return {"files": result.modified_files or {}, "repair_attempts": state.get("repair_attempts", 0) + 1}
