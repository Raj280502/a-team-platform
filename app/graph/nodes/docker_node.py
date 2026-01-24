import subprocess
from pathlib import Path
import webbrowser
import time


def docker_node(state):
    project_dir = Path("app/workspace/generated_projects/todo_app")

    print("\n🐳 Building and starting containers...\n")

    subprocess.run(
        ["docker", "compose", "up", "--build", "-d"],
        cwd=project_dir
    )

    time.sleep(5)
    webbrowser.open("http://localhost:3000")

    return {}
