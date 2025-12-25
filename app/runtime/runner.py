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

    project_dir.mkdir(parents=True, exist_ok=True)   # 🔥 WINDOWS FIX
    env = os.environ.copy()
    env["PROJECT_WORKSPACE"] = str(project_dir.resolve())

    try:
        subprocess.run(
            ["docker", "compose", "-f", "docker/docker-compose.yml", "build", "--no-cache"],
            cwd=project_dir,
            env=env,
            check=True,
        )
        subprocess.run(
            ["docker", "compose", "-f", "docker/docker-compose.yml", "up"],
            cwd=project_dir,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Docker runtime failed") from e
