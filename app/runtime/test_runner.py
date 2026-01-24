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
    """
    Starts the Flask backend server in background.
    
    Returns:
        (success, error_message)
    """
    global _flask_process
    
    backend_dir = project_dir / "backend"
    
    if not backend_dir.exists():
        return False, "Backend directory not found"
    
    try:
        # Start Flask server in background
        _flask_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if process is still running
        if _flask_process.poll() is not None:
            # Process died
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
