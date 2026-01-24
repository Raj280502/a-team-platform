import requests
from pathlib import Path
from app.core.state import ProjectState


def contract_verify_node(state: ProjectState) -> ProjectState:
    base = Path(state["project_dir"])
    violations = []

    backend = state["contract"]["backend"]

    for f in backend["must_exist"]:
        if not (base / f).exists():
            violations.append(f"Missing file {f}")

    for route in backend["must_expose_routes"]:
        parts = route.split(" ", 1)
        if len(parts) != 2:
            violations.append(f"Invalid route format: {route}")
            continue

        method, path = parts
        try:
            r = requests.request(method, f"http://localhost:5000{path}")
            if r.status_code >= 500:
                violations.append(f"Broken route {route}")
        except:
            violations.append(f"Route unreachable {route}")

    if violations:
        return {"error_message": "\n".join(violations), "tests_passed": False}
    return {"error_message": None, "tests_passed": True}
