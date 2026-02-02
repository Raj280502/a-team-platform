"""
test_runner.py
--------------
Runs basic validation checks on generated code.

This is NOT AI logic.
"""

import subprocess
import time
import sys
from pathlib import Path

# Global process handle for Flask server
_flask_process = None

def start_backend_server(project_dir: Path) -> tuple[bool, str | None]:
    global _flask_process

    # 🔥 ALWAYS stop old server first
    stop_backend_server()

    backend_dir = project_dir / "backend"

    try:
        _flask_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        time.sleep(2)

        if _flask_process.poll() is not None:
            stdout, stderr = _flask_process.communicate()
            error = stderr.decode() if stderr else stdout.decode()
            return False, f"Backend failed to start: {error}"

        return True, None

    except Exception as e:
        return False, str(e)


def stop_backend_server():
    """
    Stops the Flask backend server.
    """
    global _flask_process
    
    if _flask_process:
        try:
            _flask_process.terminate()
            _flask_process.wait(timeout=3)
        except:
            _flask_process.kill()
        _flask_process = None

def run_basic_backend_test(project_dir: Path) -> tuple[bool, str | None]:
    """
    Starts the backend server for testing.
    Server will remain running for contract tests.
    
    Returns:
        (tests_passed, error_message)
    """
    return start_backend_server(project_dir)
