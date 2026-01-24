"""
preview.py
----------
Starts the generated project locally for live preview (no Docker required).
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def start_preview(project_dir: Path):
    """
    Start Flask backend and open browser for live preview.
    """
    backend_dir = project_dir / "backend"
    frontend_dir = project_dir / "frontend"
    
    print("\n" + "=" * 60)
    print("🚀 STARTING LIVE PREVIEW")
    print("=" * 60)
    
    # Start Flask backend
    print("\n[1/2] Starting Flask backend on http://localhost:5000 ...")
    backend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait for backend to start
    time.sleep(2)
    
    if backend_process.poll() is not None:
        print("❌ Backend failed to start!")
        stdout, stderr = backend_process.communicate()
        print(stderr.decode())
        return None
    
    print("✅ Backend running!")
    
    # Check if frontend has package.json
    if (frontend_dir / "package.json").exists():
        print("\n[2/2] Starting React frontend on http://localhost:5173 ...")
        print("      Run these commands in a new terminal:")
        print(f"      cd {frontend_dir}")
        print("      npm install")
        print("      npm run dev")
        print("\n" + "=" * 60)
        print("🌐 Open http://localhost:5173 in your browser")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("🌐 Backend API available at http://localhost:5000")
        print("=" * 60)
    
    # Open browser
    webbrowser.open("http://localhost:5173")
    
    print("\nPress Ctrl+C to stop the server...")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping preview...")
        backend_process.terminate()
        print("✅ Preview stopped.")
    
    return backend_process


if __name__ == "__main__":
    # Allow running directly: python -m app.runtime.preview
    project_dir = Path("app/workspace/generated_projects/todo_app")
    start_preview(project_dir)
