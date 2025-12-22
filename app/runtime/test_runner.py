"""
test_runner.py
--------------
Runs basic validation checks on generated code.

This is NOT AI logic.
"""

import subprocess
from pathlib import Path


def run_basic_backend_test(project_dir: Path) -> tuple[bool, str | None]:
    """
    Runs a very basic backend validation.

    For MVP:
    - Try importing backend app
    - No pytest yet (we'll add later)

    Returns:
        (tests_passed, error_message)
    """

    backend_dir = project_dir / "backend"

    if not backend_dir.exists():
        return False, "Backend directory not found"

    try:
        subprocess.run(
            ["python", "app.py"],
            cwd=backend_dir,
            capture_output=True,
            timeout=5,
            check=False,
        )
        return True, None

    except Exception as e:
        return False, str(e)
