"""
web_ui.py - Flask web interface for AI Code Factory.
Enhanced with SSE streaming, chat API, and project management.
"""

import os
import sys
import json
import time
import zipfile
import threading
import io
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import WORKSPACE_DIR
from app.core.database import (
    init_db, save_project, update_project, load_project,
    list_projects as db_list_projects, delete_project,
    save_message,
)

# Serve React build from client/dist
CLIENT_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client', 'dist')
app = Flask(__name__, static_folder=CLIENT_DIST, static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Global state for current generation
_current_state = {}
_generation_lock = threading.Lock()
_generation_active = False
_current_project_id = None  # Active DB project ID

# Initialize database on import
init_db()


# ============================================
# ROUTES — Pages
# ============================================

@app.route("/")
def index():
    """Serve React app."""
    return app.send_static_file("index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


# SPA catch-all: serve React index.html for client-side routes
@app.errorhandler(404)
def spa_fallback(e):
    """Serve React app for any unmatched route (SPA routing)."""
    return app.send_static_file("index.html")


# Pipeline log buffer for terminal tab
_log_buffer = []
MAX_LOG_LINES = 500


def add_log(message: str):
    """Add a message to the log buffer."""
    _log_buffer.append(message)
    if len(_log_buffer) > MAX_LOG_LINES:
        _log_buffer.pop(0)


@app.route("/api/logs")
def api_logs():
    """Get pipeline logs for the terminal tab."""
    return jsonify({"logs": _log_buffer})


# ============================================
# ROUTES — API
# ============================================

@app.route("/api/status")
def api_status():
    """Current generation status."""
    return jsonify({
        "active": _generation_active,
        "step": _current_state.get("current_step", "idle"),
        "project_name": _current_state.get("project_name", ""),
        "files_count": len(_current_state.get("files", {})),
        "tests_passed": _current_state.get("tests_passed", False),
        "preview_url": _current_state.get("preview_url", ""),
    })


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Start project generation."""
    global _generation_active
    
    if _generation_active:
        return jsonify({"error": "Generation already in progress"}), 409

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    project_name = data.get("project_name", "")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Start generation in background thread
    thread = threading.Thread(
        target=_run_generation,
        args=(prompt, project_name),
        daemon=True,
    )
    thread.start()

    return jsonify({"status": "started", "prompt": prompt})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Send a chat message to modify existing project."""
    global _generation_active

    if _generation_active:
        return jsonify({"error": "Generation in progress"}), 409

    if not _current_state.get("files"):
        return jsonify({"error": "No project loaded. Generate one first."}), 400

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Start chat refinement in background
    thread = threading.Thread(
        target=_run_chat,
        args=(prompt,),
        daemon=True,
    )
    thread.start()

    return jsonify({"status": "started", "prompt": prompt})


@app.route("/api/files")
def api_files():
    """Get generated file tree and contents."""
    files = _current_state.get("files", {})
    project_dir = _current_state.get("project_dir", "")

    file_tree = {}
    for file_path, content in files.items():
        file_tree[file_path] = {
            "content": content,
            "lines": len(content.split("\n")),
            "size": len(content),
        }

    return jsonify({
        "project_dir": project_dir,
        "files": file_tree,
    })


@app.route("/api/file/<path:filepath>")
def api_file(filepath):
    """Get a single file content."""
    files = _current_state.get("files", {})
    content = files.get(filepath)

    if content is None:
        return jsonify({"error": "File not found"}), 404

    return jsonify({
        "path": filepath,
        "content": content,
    })


@app.route("/api/file/<path:filepath>", methods=["PUT"])
def api_update_file(filepath):
    """Update a file's content (user edits in Monaco)."""
    data = request.get_json() or {}
    content = data.get("content")

    if content is None:
        return jsonify({"error": "Content required"}), 400

    # Update in state
    if "files" in _current_state:
        _current_state["files"][filepath] = content

    # Write to disk
    project_dir = _current_state.get("project_dir")
    if project_dir:
        file_path = Path(project_dir) / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return jsonify({"status": "updated", "path": filepath})


@app.route("/api/download")
def api_download():
    """Download generated project as ZIP."""
    project_dir = _current_state.get("project_dir")
    if not project_dir or not Path(project_dir).exists():
        return jsonify({"error": "No project to download"}), 404

    project_name = _current_state.get("project_name", "project")

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        project_path = Path(project_dir)
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # Skip node_modules, __pycache__, etc.
                rel = file_path.relative_to(project_path)
                if any(p in str(rel) for p in ["node_modules", "__pycache__", ".git"]):
                    continue
                zipf.write(file_path, f"{project_name}/{rel}")

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{project_name}.zip",
    )


@app.route("/api/projects")
def api_projects():
    """List all projects from database."""
    projects = db_list_projects()
    return jsonify({"projects": projects})


@app.route("/api/projects/<project_id>")
def api_project_detail(project_id):
    """Load a specific project and restore it into current state."""
    global _current_state, _current_project_id

    data = load_project(project_id)
    if not data:
        return jsonify({"error": "Project not found"}), 404

    project = data['project']
    files = data['files']
    messages = data['messages']

    # Restore into working state so user can continue iterating
    with _generation_lock:
        _current_state = {
            "project_name": project['name'],
            "project_dir": project.get('project_dir', ''),
            "files": files,
            "current_step": "complete",
            "tests_passed": False,
            "preview_url": "",
        }
        _current_project_id = project_id

    return jsonify({
        "project": project,
        "files": {path: {"content": content, "lines": len(content.split('\n')), "size": len(content)} for path, content in files.items()},
        "messages": messages,
    })


@app.route("/api/projects/<project_id>", methods=["DELETE"])
def api_project_delete(project_id):
    """Delete a project from the database."""
    deleted = delete_project(project_id)
    if not deleted:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"status": "deleted", "id": project_id})


@app.route("/api/preview/start", methods=["POST"])
def api_preview_start():
    """Start the preview servers."""
    from app.graph.nodes.preview_node import preview_node, get_preview_error

    if not _current_state.get("project_dir"):
        return jsonify({"error": "No project loaded"}), 400

    result = preview_node(_current_state)
    _current_state.update(result)

    error_msg = ""
    if not result.get("preview_started", False):
        error_msg = get_preview_error() or "Preview failed to start"

    return jsonify({
        "started": result.get("preview_started", False),
        "url": result.get("preview_url", ""),
        "error": error_msg,
    })


@app.route("/api/preview/stop", methods=["POST"])
def api_preview_stop():
    """Stop preview servers."""
    from app.graph.nodes.preview_node import stop_preview
    stop_preview()
    _current_state["preview_url"] = ""
    _current_state["preview_started"] = False
    return jsonify({"status": "stopped"})


@app.route("/api/preview/status")
def api_preview_status():
    """Check preview status."""
    from app.graph.nodes.preview_node import is_preview_running, get_preview_error
    status = is_preview_running()
    status["preview_url"] = _current_state.get("preview_url", "")
    status["error"] = get_preview_error()
    return jsonify(status)


# ============================================
# SSE STREAMING
# ============================================

@app.route("/api/stream")
def api_stream():
    """Server-Sent Events endpoint for real-time updates."""
    def event_stream():
        last_step = ""
        last_files_count = 0
        known_files = set()

        while True:
            step = _current_state.get("current_step", "idle")
            current_files = _current_state.get("files", {})
            files_count = len(current_files)

            # Detect newly added files
            new_files = {}
            current_keys = set(current_files.keys())
            added = current_keys - known_files
            if added:
                for fp in added:
                    new_files[fp] = {
                        "content": current_files[fp],
                        "lines": len(current_files[fp].split("\n")),
                        "size": len(current_files[fp]),
                    }
                known_files = current_keys

            if step != last_step or files_count != last_files_count or new_files:
                event_data = json.dumps({
                    "step": step,
                    "files_count": files_count,
                    "active": _generation_active,
                    "project_name": _current_state.get("project_name", ""),
                    "preview_url": _current_state.get("preview_url", ""),
                    "tests_passed": _current_state.get("tests_passed", False),
                    "new_files": new_files,  # contains path, content, lines, size
                })
                yield f"data: {event_data}\n\n"
                last_step = step
                last_files_count = files_count

            if step == "complete" or step == "error":
                # Send final event and close
                yield f"data: {json.dumps({'step': step, 'final': True})}\n\n"
                break

            time.sleep(0.3)  # Faster polling for real-time feel

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ============================================
# SDLC STAGE API (stage-gated execution)
# ============================================

@app.route("/api/stages", methods=["GET"])
def api_stages():
    """Return data for all completed SDLC stages."""
    from app.graph.graph import SDLC_STAGES, STAGE_LABELS

    stages = []
    for name in SDLC_STAGES:
        data = _current_state.get(name if name != "user_research" else "user_research",
                                   _current_state.get(name, None))
        # Map stage names to their state keys
        state_key = {
            "overview": "project_overview",
            "requirements": "requirements",
            "user_research": "user_research",
            "task_flows": "task_flows",
            "user_stories": "user_stories",
        }.get(name, name)

        stage_data = _current_state.get(state_key)

        stages.append({
            "name": name,
            "label": STAGE_LABELS.get(name, name),
            "completed": stage_data is not None,
            "data": stage_data,
        })

    return jsonify({
        "stages": stages,
        "current_step": _current_state.get("current_step", "idle"),
        "active": _generation_active,
    })


@app.route("/api/stages/<stage_name>", methods=["GET"])
def api_stage_detail(stage_name):
    """Return data for a specific SDLC stage."""
    state_key = {
        "overview": "project_overview",
        "requirements": "requirements",
        "user_research": "user_research",
        "task_flows": "task_flows",
        "user_stories": "user_stories",
    }.get(stage_name)

    if not state_key:
        return jsonify({"error": f"Unknown stage: {stage_name}"}), 404

    data = _current_state.get(state_key)
    return jsonify({
        "name": stage_name,
        "completed": data is not None,
        "data": data,
    })


@app.route("/api/stages/run/<stage_name>", methods=["POST"])
def api_run_stage(stage_name):
    """Run a single SDLC stage (stage-gated execution)."""
    global _generation_active

    from app.graph.graph import SDLC_STAGES

    if stage_name not in SDLC_STAGES:
        return jsonify({"error": f"Unknown stage: {stage_name}"}), 404

    if _generation_active:
        return jsonify({"error": "A stage is already running"}), 409

    # Get the user prompt — either from current state or from request body
    body = request.get_json() or {}
    prompt = body.get("prompt", "") or _current_state.get("user_prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt available. Send prompt in request body."}), 400

    # Store the prompt in state
    _current_state["user_prompt"] = prompt

    thread = threading.Thread(
        target=_run_stage,
        args=(stage_name,),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "status": "started",
        "stage": stage_name,
    })


@app.route("/api/stages/generate", methods=["POST"])
def api_start_code_generation():
    """Start code generation AFTER all SDLC stages have been approved."""
    global _generation_active

    if _generation_active:
        return jsonify({"error": "Generation already in progress"}), 409

    prompt = _current_state.get("user_prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt set"}), 400

    project_name = _current_state.get("project_name", "")

    thread = threading.Thread(
        target=_run_generation,
        args=(prompt, project_name),
        daemon=True,
    )
    thread.start()

    return jsonify({"status": "started"})


# ============================================
# SOCKETIO EVENTS
# ============================================

@socketio.on("connect")
def handle_connect():
    print("🔌 Client connected")
    emit("status", {"step": _current_state.get("current_step", "idle")})


@socketio.on("generate")
def handle_generate(data):
    """Start generation via WebSocket."""
    prompt = data.get("prompt", "").strip()
    if not prompt:
        emit("error", {"message": "Prompt required"})
        return

    if _generation_active:
        emit("error", {"message": "Generation already in progress"})
        return

    thread = threading.Thread(
        target=_run_generation,
        args=(prompt, ""),
        daemon=True,
    )
    thread.start()

    emit("status", {"step": "starting", "message": "Generation started..."})


@socketio.on("chat")
def handle_chat(data):
    """Handle chat refinement via WebSocket."""
    prompt = data.get("prompt", "").strip()
    if not prompt:
        emit("error", {"message": "Prompt required"})
        return

    thread = threading.Thread(
        target=_run_chat,
        args=(prompt,),
        daemon=True,
    )
    thread.start()


# ============================================
# BACKGROUND GENERATION
# ============================================

def _update_state(node_name: str, node_output: dict):
    """Callback to receive intermediate node outputs for real-time UI updates."""
    global _current_state
    with _generation_lock:
        # Merge files incrementally (coder_file_node outputs files)
        if "files" in node_output:
            if "files" not in _current_state:
                _current_state["files"] = {}
            _current_state["files"].update(node_output["files"])

        # Update step indicator
        if "current_step" in node_output:
            _current_state["current_step"] = node_output["current_step"]

        # Update project name/dir if present
        for key in ("project_name", "project_dir", "tech_stack",
                     "tests_passed", "preview_url", "preview_started"):
            if key in node_output:
                _current_state[key] = node_output[key]

        # Update SDLC stage data
        for key in ("project_overview", "requirements", "user_research",
                     "task_flows", "user_stories"):
            if key in node_output:
                _current_state[key] = node_output[key]

    add_log(f"[{node_name}] completed — files: {len(_current_state.get('files', {}))}")


def _run_stage(stage_name: str):
    """Run a single SDLC stage in background (stage-gated execution)."""
    global _generation_active, _current_state

    with _generation_lock:
        _generation_active = True
        _current_state["current_step"] = f"{stage_name}_running"

    try:
        from app.graph.graph import build_stage_graph

        graph = build_stage_graph(stage_name)

        # Build input state from current accumulated state
        input_state = {
            "user_prompt": _current_state.get("user_prompt", ""),
            "project_name": _current_state.get("project_name", ""),
            "project_dir": _current_state.get("project_dir", ""),
            "tech_stack": _current_state.get("tech_stack", "react-flask"),
            "chat_history": _current_state.get("chat_history", []),
            "is_followup": False,
            "files": _current_state.get("files", {}),
            "file_plan": _current_state.get("file_plan", []),
            "extracted_routes": _current_state.get("extracted_routes", []),
            "request_fields": _current_state.get("request_fields", {}),
            "generation_issues": [],
            "files_to_regenerate": [],
            "failed_file_history": [],
            "tests_passed": False,
            "error_message": None,
            "contract_report": {},
            "repair_attempts": 0,
            "preview_started": False,
            "preview_url": "",
            "current_step": f"{stage_name}_running",
        }

        # Include previously completed SDLC stage data
        for key in ("project_overview", "requirements", "user_research",
                     "task_flows", "user_stories", "project_scope", "architecture"):
            if key in _current_state and _current_state[key]:
                input_state[key] = _current_state[key]

        print(f"\n🎯 Running SDLC stage: {stage_name}")
        result = graph.invoke(input_state)

        # Merge result into current state
        with _generation_lock:
            for key, value in result.items():
                if value is not None:
                    _current_state[key] = value
            _current_state["current_step"] = f"{stage_name}_complete"

        print(f"   ✅ Stage '{stage_name}' completed successfully")

    except Exception as e:
        print(f"   ❌ Stage '{stage_name}' failed: {e}")
        import traceback
        traceback.print_exc()
        with _generation_lock:
            _current_state["current_step"] = "error"
            _current_state["error_message"] = str(e)

    finally:
        _generation_active = False


def _run_generation(prompt: str, project_name: str):
    """Run the full generation pipeline in background with real-time streaming."""
    global _generation_active, _current_state, _current_project_id

    with _generation_lock:
        _generation_active = True
        if "files" not in _current_state:
            _current_state["files"] = {}
        _current_state["current_step"] = "starting"

    try:
        from app.main import run_pipeline_streaming

        # Use streaming to get intermediate state after each node
        result = run_pipeline_streaming(prompt, project_name or None, _update_state)

        with _generation_lock:
            _current_state.update(result)
            _current_state["current_step"] = "complete"

        # Auto-start preview after generation
        try:
            from app.graph.nodes.preview_node import preview_node as pn
            print("\n🚀 Auto-starting preview...")
            with _generation_lock:
                _current_state["current_step"] = "preview_starting"
            preview_result = pn(_current_state)
            with _generation_lock:
                _current_state.update(preview_result)
            if preview_result.get("preview_started"):
                print(f"   ✅ Preview auto-started: {preview_result.get('preview_url')}")
            else:
                print("   ⚠️ Auto-preview failed (user can retry manually)")
        except Exception as prev_err:
            print(f"   ⚠️ Auto-preview error: {prev_err}")

        # Save to database
        try:
            p_name = result.get("project_name", project_name or "Untitled")
            tech = result.get("tech_stack", "react-flask")
            files = result.get("files", {})
            p_dir = result.get("project_dir", "")
            messages = [{"role": "user", "text": prompt, "type": "message"}]

            pid = save_project(
                name=p_name, prompt=prompt, tech_stack=tech,
                files=files, messages=messages,
                project_dir=p_dir, status="complete"
            )
            with _generation_lock:
                _current_project_id = pid
            print(f"💾 Project saved to DB: {pid}")
        except Exception as db_err:
            print(f"⚠️ DB save failed: {db_err}")

        # Notify via SocketIO
        socketio.emit("generation_complete", {
            "files_count": len(result.get("files", {})),
            "tests_passed": result.get("tests_passed", False),
            "preview_url": result.get("preview_url", ""),
        })

    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()

        with _generation_lock:
            _current_state["current_step"] = "error"
            _current_state["error_message"] = str(e)

        socketio.emit("generation_error", {"error": str(e)})

    finally:
        with _generation_lock:
            _generation_active = False


def _run_chat(prompt: str):
    """Run chat refinement in background."""
    global _generation_active, _current_state

    with _generation_lock:
        _generation_active = True
        _current_state["current_step"] = "chat_processing"

    try:
        from app.main import run_chat_pipeline
        result = run_chat_pipeline(prompt, _current_state.copy())

        with _generation_lock:
            _current_state.update(result)
            _current_state["current_step"] = "complete"

        # Save chat message and updated files to DB
        try:
            if _current_project_id:
                save_message(_current_project_id, 'user', prompt, 'message')
                updated_files = _current_state.get('files', {})
                if updated_files:
                    update_project(_current_project_id, files=updated_files)
                print(f"💾 Chat saved to DB for project: {_current_project_id}")
        except Exception as db_err:
            print(f"⚠️ DB chat save failed: {db_err}")

        socketio.emit("chat_complete", {
            "files_count": len(result.get("files", {})),
        })

    except Exception as e:
        print(f"❌ Chat error: {e}")
        with _generation_lock:
            _current_state["current_step"] = "error"

        socketio.emit("chat_error", {"error": str(e)})

    finally:
        with _generation_lock:
            _generation_active = False


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏭 AI CODE FACTORY — Web Interface")
    print("=" * 60)
    print(f"🌐 http://localhost:8080")
    print("=" * 60 + "\n")

    socketio.run(app, host="0.0.0.0", port=8080, debug=False)
