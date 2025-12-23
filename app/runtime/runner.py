"""
runner.py
---------
Builds and runs generated projects using Docker Compose.
"""

import subprocess
import os
from pathlib import Path


def run_project(project_dir: Path):
    """
    Build and run the generated project using docker compose.
    """

    compose_dir = Path("app/runtime/docker").resolve()

    env = os.environ.copy()
    env["PROJECT_WORKSPACE"] = str(project_dir.resolve())
    env["DOCKER_TEMPLATES"] = str(compose_dir.resolve())

    try:
        subprocess.run(
            ["docker", "compose", "up", "--build"],
            cwd=compose_dir,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Docker runtime failed") from e
