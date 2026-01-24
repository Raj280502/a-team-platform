from pathlib import Path
from app.agents.coder.node import build_repair_node
from app.runtime.failure_compiler import compile_failure
from app.utils.file_ops import normalize_code


def repair_node(state):
    project_dir = Path(state["project_dir"])
    backend_file = project_dir / "backend" / "app.py"

    if not backend_file.exists():
        return {"repair_attempts": state.get("repair_attempts", 0) + 1}

    broken_code = backend_file.read_text(encoding="utf-8")
    failure_report = compile_failure(project_dir, state["error_message"])

    repairer = build_repair_node()

    fixed_code = repairer.invoke(
        {
            "broken_file": broken_code,
            "failure_report": failure_report,
        }
    ).content

    backend_file.write_text(normalize_code(fixed_code), encoding="utf-8")

    return {
        "repair_attempts": state.get("repair_attempts", 0) + 1
    }
