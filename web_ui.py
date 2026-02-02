"""
web_ui.py
---------
Web-based UI for the AI Code Factory with integrated editor and terminal.
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
import sys
import subprocess
import threading
from pathlib import Path
from queue import Queue
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_project = None
generation_status = {"status": "idle", "message": ""}
terminal_output_queue = Queue()


@app.route('/')
def index():
    """Serve the main UI page."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "AI Code Factory Web UI is running",
        "current_project": current_project
    })


@app.route('/api/test')
def test_import():
    """Test if imports work."""
    try:
        from app.main import run_pipeline
        return jsonify({"status": "ok", "message": "Imports working"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_project():
    """Start project generation."""
    global current_project, generation_status
    
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    generation_status = {"status": "running", "message": "Starting generation..."}
    
    # Run generation in background
    thread = threading.Thread(target=run_generation, args=(prompt,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "message": "Generation started"})


@app.route('/api/status')
def get_status():
    """Get current generation status."""
    return jsonify(generation_status)


@app.route('/api/files/<path:filepath>')
def get_file(filepath):
    """Get file content."""
    if not current_project:
        return jsonify({"error": "No active project"}), 404
    
    try:
        full_path = Path(current_project) / filepath
        if not full_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        content = full_path.read_text(encoding='utf-8')
        return jsonify({"content": content, "path": filepath})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/files/<path:filepath>', methods=['PUT'])
def save_file(filepath):
    """Save file content."""
    if not current_project:
        return jsonify({"error": "No active project"}), 404
    
    try:
        data = request.json
        content = data.get('content', '')
        
        full_path = Path(current_project) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        
        return jsonify({"status": "saved", "path": filepath})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/docker/status')
def docker_status():
    """Check if Docker is running and containers status."""
    if not current_project:
        return jsonify({"error": "No active project"}), 404
    
    try:
        import subprocess
        
        # Check if Docker is running
        docker_check = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        
        if docker_check.returncode != 0:
            return jsonify({
                "docker_running": False,
                "message": "Docker is not running. Please start Docker Desktop."
            })
        
        # Check container status
        ps_result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=current_project,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return jsonify({
            "docker_running": True,
            "containers": ps_result.stdout,
            "project_dir": current_project
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Docker command timed out"}), 500
    except FileNotFoundError:
        return jsonify({"error": "Docker not found. Is Docker Desktop installed?"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/files')
def list_files():
    """List all files in current project."""
    if not current_project:
        return jsonify({"error": "No active project"}), 404
    
    try:
        project_path = Path(current_project)
        files = []
        
        for root, dirs, filenames in os.walk(project_path):
            # Skip node_modules, __pycache__, etc.
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'venv']]
            
            for filename in filenames:
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(project_path)
                files.append(str(rel_path).replace('\\', '/'))
        
        return jsonify({"files": sorted(files)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on('execute_command')
def handle_command(data):
    """Execute terminal command and stream output."""
    command = data.get('command', '')
    cwd = data.get('cwd', current_project or os.getcwd())
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                socketio.emit('terminal_output', {'output': line})
        
        process.wait()
        socketio.emit('terminal_output', {
            'output': f'\n[Process exited with code {process.returncode}]\n',
            'exit_code': process.returncode
        })
        
    except Exception as e:
        socketio.emit('terminal_output', {
            'output': f'Error: {str(e)}\n',
            'error': True
        })


def run_generation(prompt: str):
    """Run the generation pipeline in background."""
    global current_project, generation_status
    
    try:
        print(f"\n🚀 Starting generation for: {prompt}")
        
        # Import here to avoid circular imports
        try:
            from app.main import run_pipeline
        except ImportError as e:
            print(f"❌ Import error: {e}")
            raise Exception(f"Failed to import pipeline: {e}")
        
        generation_status = {"status": "running", "message": f"Generating: {prompt}"}
        socketio.emit('generation_status', generation_status)
        print("📡 Status emitted: running")
        
        # Run the pipeline
        print("🔄 Calling run_pipeline...")
        project_dir, final_state = run_pipeline(prompt)
        current_project = str(project_dir)
        
        print(f"✅ Generation completed: {project_dir}")
        
        # Get preview URL from final state
        preview_url = final_state.get('preview_url', 'http://localhost:3000')
        preview_started = final_state.get('preview_started', False)
        
        generation_status = {
            "status": "completed", 
            "message": "Generation completed!",
            "project_dir": str(project_dir),
            "preview_url": preview_url,
            "preview_started": preview_started
        }
        socketio.emit('generation_status', generation_status)
        
        # List generated files and send preview URL
        socketio.emit('project_ready', {
            "project_dir": str(project_dir),
            "preview_url": preview_url
        })
        
        print("📡 Status emitted: completed")
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        
        generation_status = {
            "status": "error",
            "message": f"Error: {str(e)}"
        }
        socketio.emit('generation_status', generation_status)


if __name__ == '__main__':
    print("🌐 Starting AI Code Factory Web UI...")
    print("📡 Open your browser at: http://localhost:8080")
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
