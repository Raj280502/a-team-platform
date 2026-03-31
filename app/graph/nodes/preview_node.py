"""
preview_node.py
-------------- 
Starts the generated application for live preview.
Robust: port cleanup, health checks with retries, detailed error reporting.
"""

import subprocess
import sys
import time
import shutil
import socket
import signal
import os
import re
import urllib.request
from pathlib import Path

from app.core.state import ProjectState
from app.core.config import PREVIEW_BACKEND_PORT, PREVIEW_FRONTEND_PORT

# Global process handles
_backend_process = None
_frontend_process = None

# Track last error for UI display
_last_preview_error = ""


def preview_node(state: ProjectState) -> ProjectState:
    """
    Starts the generated application for preview.
    1. Kills anything on preview ports
    2. Installs deps
    3. Starts Flask backend (port 5000)
    4. Starts Vite dev server (port 5173)
    5. Health-checks both with retries
    """
    global _last_preview_error
    _last_preview_error = ""
    print("\n🚀 PREVIEW: Starting application...")

    project_dir = Path(state.get("project_dir", ""))
    if not project_dir.exists():
        _last_preview_error = "Project directory not found"
        print(f"   ❌ {_last_preview_error}: {project_dir}")
        return {
            "preview_started": False,
            "preview_url": "",
            "current_step": "preview_failed",
        }

    backend_dir = project_dir / "backend"
    frontend_dir = project_dir / "frontend"

    # ============================================
    # Step 0: Clean up — kill old processes + free ports
    # ============================================
    stop_preview()
    _kill_port(PREVIEW_BACKEND_PORT)
    _kill_port(PREVIEW_FRONTEND_PORT)
    time.sleep(0.5)

    # ============================================
    # Step 1: Patch generated code for reliability
    # ============================================
    _patch_backend_for_preview(backend_dir)
    _patch_frontend_for_preview(frontend_dir)
    _patch_frontend_localhost_refs(frontend_dir)
    _patch_missing_jsx_imports(frontend_dir)
    _fix_broken_imports(frontend_dir)
    # ============================================
    # Step 2: Install backend dependencies
    # ============================================
    install_backend_deps(backend_dir)

    # ============================================
    # Step 3: Install frontend dependencies
    # ============================================
    npm_ok = install_frontend_deps(frontend_dir)

    # ============================================
    # Step 4: Start backend
    # ============================================
    backend_ok = start_backend(backend_dir)
    if not backend_ok:
        _last_preview_error = _last_preview_error or "Backend failed to start"
        print(f"   ❌ {_last_preview_error}")
        # Still try frontend even if backend fails
        # Some projects are frontend-only

    # ============================================
    # Step 5: Start frontend
    # ============================================
    frontend_ok = False
    if npm_ok and frontend_dir.exists():
        frontend_ok = start_frontend(frontend_dir)

    # Determine the preview URL — use 127.0.0.1 (not localhost) to avoid IPv6 resolution issues
    if frontend_ok:
        preview_url = f"http://127.0.0.1:{PREVIEW_FRONTEND_PORT}"
    elif backend_ok:
        preview_url = f"http://127.0.0.1:{PREVIEW_BACKEND_PORT}"
    else:
        _last_preview_error = _last_preview_error or "Both backend and frontend failed"
        print(f"   ❌ {_last_preview_error}")
        return {
            "preview_started": False,
            "preview_url": "",
            "current_step": "preview_failed",
        }

    if backend_ok:
        print(f"   ✅ Backend running on port {PREVIEW_BACKEND_PORT}")
    if frontend_ok:
        print(f"   ✅ Frontend running on port {PREVIEW_FRONTEND_PORT}")

    print(f"   🌐 Preview URL: {preview_url}")

    return {
        "preview_started": True,
        "preview_url": preview_url,
        "current_step": "preview_ready",
    }


def get_preview_error() -> str:
    """Return the last preview error message for the UI."""
    return _last_preview_error


def _is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _kill_port(port: int):
    """Kill any process listening on a given port (Windows + Unix)."""
    try:
        if sys.platform == "win32":
            # Find PID using netstat
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    pid = int(parts[-1])
                    if pid > 0:
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(pid)],
                                capture_output=True, timeout=5
                            )
                            print(f"   🔄 Killed process {pid} on port {port}")
                        except Exception:
                            pass
        else:
            # Unix: use lsof
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True, timeout=5
            )
            for pid in result.stdout.strip().split("\n"):
                if pid.strip():
                    try:
                        os.kill(int(pid.strip()), signal.SIGKILL)
                        print(f"   🔄 Killed process {pid} on port {port}")
                    except Exception:
                        pass
    except Exception as e:
        print(f"   ⚠️ Port cleanup warning for {port}: {e}")


def _health_check(port: int, path: str = "/", retries: int = 8, delay: float = 1.0) -> bool:
    """
    Check if a server is responding on the given port.
    Retries with increasing delay.
    """
    for attempt in range(retries):
        try:
            url = f"http://127.0.0.1:{port}{path}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status < 500:
                    return True
        except Exception:
            pass

        # Also check if process is still alive via port
        if _is_port_in_use(port):
            # Port is bound but maybe not serving HTTP yet — could be OK
            if attempt >= 2:
                return True  # Port is open, treat as started

        wait = delay * (1 + attempt * 0.5)
        time.sleep(wait)

    return False


def _patch_backend_for_preview(backend_dir: Path):
    """
    Patch the generated Flask app.py to ensure it runs correctly for preview.
    - Add host='0.0.0.0' to app.run()
    - Ensure correct port
    - Add CORS headers
    """
    app_file = backend_dir / "app.py"
    if not app_file.exists():
        return

    try:
        code = app_file.read_text(encoding="utf-8")
        modified = False

        # Ensure CORS is imported and initialized
        if "flask_cors" not in code and "CORS" not in code:
            # Add CORS import after Flask import
            if "from flask import" in code:
                code = code.replace(
                    "from flask import",
                    "from flask_cors import CORS\nfrom flask import",
                    1
                )
                # Add CORS(app) after app = Flask(...)
                if "app = Flask(" in code:
                    code = code.replace(
                        "app = Flask(__name__)",
                        "app = Flask(__name__)\nCORS(app)",
                        1
                    )
                modified = True

        # Ensure app.run uses correct port and host
        if "app.run(" in code:
            import re
            # Replace any app.run(...) to use 0.0.0.0 and correct port
            code = re.sub(
                r'app\.run\([^)]*\)',
                f'app.run(host="0.0.0.0", port={PREVIEW_BACKEND_PORT}, debug=False)',
                code
            )
            modified = True

        if modified:
            app_file.write_text(code, encoding="utf-8")
            print("   🔧 Patched backend app.py for preview")
    except Exception as e:
        print(f"   ⚠️ Backend patch warning: {e}")


def _patch_frontend_for_preview(frontend_dir: Path):
    """
    Patch the generated Vite config for reliable preview.
    - Ensure host is 0.0.0.0
    - Ensure correct port
    - Fix proxy target to use 127.0.0.1 (avoid IPv6)
    """
    vite_config = frontend_dir / "vite.config.js"
    if not vite_config.exists():
        return

    try:
        config = vite_config.read_text(encoding="utf-8")
        modified = False

        # Ensure server.host is set
        if "host:" not in config and "server:" in config:
            config = config.replace(
                "server: {",
                f"server: {{\n    host: '0.0.0.0',",
                1
            )
            modified = True

        # Fix proxy targets: localhost → 127.0.0.1 to avoid IPv6
        if "localhost:" + str(PREVIEW_BACKEND_PORT) in config:
            config = config.replace(
                f"http://localhost:{PREVIEW_BACKEND_PORT}",
                f"http://127.0.0.1:{PREVIEW_BACKEND_PORT}",
            )
            modified = True

        # Add CSP headers to allow Vite HMR (uses eval)
        if "Content-Security-Policy" not in config and "headers:" not in config:
            csp = (
                "\"script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' ws: wss: http://127.0.0.1:*;\""
            )
            if "host:" in config:
                config = config.replace(
                    "host:",
                    f"headers: {{\n      'Content-Security-Policy': {csp}\n    }},\n    host:",
                    1
                )
            elif "port:" in config:
                config = config.replace(
                    "port:",
                    f"headers: {{\n      'Content-Security-Policy': {csp}\n    }},\n    port:",
                    1
                )
            modified = True

        if modified:
            vite_config.write_text(config, encoding="utf-8")
            print("   🔧 Patched vite.config.js for preview")
    except Exception as e:
        print(f"   ⚠️ Frontend patch warning: {e}")


def _patch_frontend_localhost_refs(frontend_dir: Path):
    """
    Replace hardcoded http://localhost:5000 in generated .jsx/.js/.ts files
    with relative /api paths so the Vite proxy handles routing.
    Also replaces localhost with 127.0.0.1 for any remaining full URLs.
    """
    src_dir = frontend_dir / "src"
    if not src_dir.exists():
        return

    count = 0
    for ext in ("*.jsx", "*.js", "*.ts", "*.tsx"):
        for file in src_dir.rglob(ext):
            try:
                content = file.read_text(encoding="utf-8")
                original = content

                # Replace full URL axios/fetch calls with relative paths
                # e.g. http://localhost:5000/api/products → /api/products
                content = content.replace(
                    f"http://localhost:{PREVIEW_BACKEND_PORT}",
                    ""
                )
                content = content.replace(
                    f"http://127.0.0.1:{PREVIEW_BACKEND_PORT}",
                    ""
                )

                if content != original:
                    file.write_text(content, encoding="utf-8")
                    count += 1
            except Exception:
                pass

    if count > 0:
        print(f"   🔧 Patched {count} frontend files: removed hardcoded localhost URLs")

# PascalCase JSX elements that should NOT be auto-imported
_JSX_BUILTINS = {
    'React', 'Fragment', 'Suspense', 'StrictMode', 'Profiler', 'App',
}


def _patch_missing_jsx_imports(frontend_dir: Path):
    """
    Safety net at preview time: scan all .jsx files in src/ for PascalCase
    component references that are not imported, and inject import statements.
    Only adds imports for components that actually exist on disk.
    """
    src_dir = frontend_dir / "src"
    if not src_dir.exists():
        return

    # Collect known component files on disk
    comp_dir = src_dir / "components"
    known_components = set()
    if comp_dir.exists():
        for f in comp_dir.iterdir():
            if f.suffix == ".jsx":
                known_components.add(f.stem)

    if not known_components:
        return

    count = 0
    for jsx_file in src_dir.rglob("*.jsx"):
        try:
            content = jsx_file.read_text(encoding="utf-8")
            original = content

            # Find PascalCase tags used in JSX
            used = set(re.findall(r'<([A-Z][A-Za-z0-9]+)', content))
            used -= _JSX_BUILTINS

            # Find already-imported names
            imported = set(re.findall(r'import\s+(\w+)\s+from', content))
            for d in re.findall(r'import\s*\{([^}]+)\}\s*from', content):
                for name in d.split(','):
                    imported.add(name.strip())

            missing = used - imported
            # Only add imports for components that exist on disk
            missing = missing & known_components

            if not missing:
                continue

            # Build import lines
            new_imports = [f"import {c} from './components/{c}';" for c in sorted(missing)]

            # Insert after last import line
            lines = content.split('\n')
            last_imp = -1
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    last_imp = i

            if last_imp >= 0:
                for j, imp in enumerate(new_imports):
                    lines.insert(last_imp + 1 + j, imp)
            else:
                lines = new_imports + [''] + lines

            content = '\n'.join(lines)
            if content != original:
                jsx_file.write_text(content, encoding="utf-8")
                count += 1
                print(f"   \U0001f527 Patched imports in {jsx_file.name}: +{', '.join(sorted(missing))}")
        except Exception as e:
            print(f"   \u26a0\ufe0f Import patch warning for {jsx_file.name}: {e}")

    if count > 0:
        print(f"   \U0001f527 Patched missing component imports in {count} JSX file(s)")


def _fix_broken_imports(frontend_dir: Path):
    """
    Safety net: scan all .jsx/.js files and fix imports that reference
    non-existent files.
    - Missing .css imports → create an empty CSS stub file
    - Missing .jsx/.js component imports → remove the import line
      and replace JSX references with a placeholder <div>
    """
    src_dir = frontend_dir / "src"
    if not src_dir.exists():
        return

    css_created = 0
    imports_removed = 0

    for ext in ("*.jsx", "*.js", "*.tsx", "*.ts"):
        for source_file in src_dir.rglob(ext):
            try:
                content = source_file.read_text(encoding="utf-8")
                original = content
                lines = content.split("\n")
                new_lines = []
                removed_components = []

                for line in lines:
                    stripped = line.strip()

                    # Match: import Something from './path'
                    # Match: import './path.css'
                    m_default = re.match(
                        r"import\s+(\w+)\s+from\s+['\"](\.\./|\./)?([^'\"]+)['\"];",
                        stripped
                    )
                    m_css = re.match(
                        r"import\s+['\"](\.\./|\./)?([^'\"]+\.css)['\"];",
                        stripped
                    )

                    if m_css:
                        prefix = m_css.group(1) or "./"
                        css_path = m_css.group(2)
                        resolved = (source_file.parent / (prefix + css_path)).resolve()
                        if not resolved.exists():
                            # Create empty CSS stub
                            resolved.parent.mkdir(parents=True, exist_ok=True)
                            resolved.write_text(
                                f"/* Auto-generated stub for {css_path} */\n",
                                encoding="utf-8"
                            )
                            css_created += 1
                        new_lines.append(line)
                    elif m_default:
                        comp_name = m_default.group(1)
                        prefix = m_default.group(2) or "./"
                        import_path = m_default.group(3)
                        # Resolve the actual file path
                        base = source_file.parent / (prefix + import_path)
                        candidates = [
                            base,
                            base.with_suffix(".jsx"),
                            base.with_suffix(".js"),
                            base.with_suffix(".tsx"),
                            base.with_suffix(".ts"),
                        ]
                        exists = any(c.exists() for c in candidates)
                        if exists:
                            new_lines.append(line)
                        else:
                            # Remove the import and track the component name
                            removed_components.append(comp_name)
                            imports_removed += 1
                            new_lines.append(
                                f"// [auto-removed] {stripped}  -- file not found"
                            )
                    else:
                        new_lines.append(line)

                # Replace JSX usage of removed components with a placeholder
                content = "\n".join(new_lines)
                for comp in removed_components:
                    # Replace self-closing: <CompName ... />
                    content = re.sub(
                        rf"<{comp}\b[^>]*/>",
                        f'<div className="item-card" style={{{{padding:"12px"}}}}>⚠️ {comp} (component not generated)</div>',
                        content
                    )
                    # Replace paired tags: <CompName ...>...</CompName>
                    content = re.sub(
                        rf"<{comp}\b[^>]*>.*?</{comp}>",
                        f'<div className="item-card" style={{{{padding:"12px"}}}}>⚠️ {comp} (component not generated)</div>',
                        content,
                        flags=re.DOTALL
                    )

                if content != original:
                    source_file.write_text(content, encoding="utf-8")

            except Exception as e:
                print(f"   ⚠️ Broken import fix warning for {source_file.name}: {e}")

    if css_created > 0:
        print(f"   🔧 Created {css_created} empty CSS stub(s) for missing stylesheets")
    if imports_removed > 0:
        print(f"   🔧 Removed {imports_removed} import(s) referencing non-existent files")


def install_backend_deps(backend_dir: Path):
    """Install Python dependencies from requirements.txt."""
    req_file = backend_dir / "requirements.txt"
    if not req_file.exists():
        return

    # Ensure flask-cors is in requirements
    try:
        content = req_file.read_text(encoding="utf-8")
        if "flask-cors" not in content.lower():
            with open(req_file, "a", encoding="utf-8") as f:
                f.write("\nflask-cors\n")
    except Exception:
        pass

    print("   📦 Installing backend dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            cwd=backend_dir,
            timeout=90,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("   ✅ Backend deps installed")
    except subprocess.TimeoutExpired:
        print("   ⚠️ Backend deps install timed out")
    except Exception as e:
        print(f"   ⚠️ Backend deps install warning: {e}")


def _patch_package_json_deps(frontend_dir: Path) -> bool:
    """
    Scan src/ for imported npm packages and ensure they are in package.json.
    Adds any missing packages and deletes node_modules to force reinstall.
    Returns True if package.json was modified.
    """
    import json as _json

    package_json_path = frontend_dir / "package.json"
    src_dir = frontend_dir / "src"
    if not package_json_path.exists() or not src_dir.exists():
        return False

    # These are the standard packages the LLM commonly generates imports for
    REQUIRED_DEPS = {
        "react-router-dom": "^6.20.0",
        "axios": "^1.6.0",
        "lucide-react": "^0.344.0",
        "recharts": "^2.10.0",
        "date-fns": "^3.0.0",
    }

    # Scan all JSX/JS files for imported package names
    imported_packages = set()
    for ext in ("*.jsx", "*.js", "*.ts", "*.tsx"):
        for f in src_dir.rglob(ext):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Match: import X from 'package' or import { X } from 'package'
                for m in re.finditer(r"from ['\"]([^./][^'\"]*)['\"]", content):
                    # Get the base package name (e.g. 'react-router-dom/native' → 'react-router-dom')
                    parts = m.group(1).split("/")
                    pkg = parts[0] if not parts[0].startswith("@") else "/".join(parts[:2])
                    imported_packages.add(pkg)
            except Exception:
                pass

    try:
        pkg_data = _json.loads(package_json_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    current_deps = pkg_data.get("dependencies", {})
    added = {}

    for pkg, ver in REQUIRED_DEPS.items():
        if pkg in imported_packages and pkg not in current_deps:
            current_deps[pkg] = ver
            added[pkg] = ver

    if not added:
        return False

    pkg_data["dependencies"] = current_deps
    package_json_path.write_text(_json.dumps(pkg_data, indent=2), encoding="utf-8")
    print(f"   🔧 Added missing npm packages to package.json: {', '.join(added.keys())}")

    # Force reinstall by removing node_modules
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        import shutil as _shutil
        try:
            _shutil.rmtree(node_modules)
            print("   🔧 Removed node_modules to force clean reinstall")
        except Exception as e:
            print(f"   ⚠️ Could not remove node_modules: {e}")

    return True


def install_frontend_deps(frontend_dir: Path) -> bool:
    """Install npm dependencies, auto-fixing missing packages first."""
    global _last_preview_error
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("   ⚠️ No package.json found, skipping npm install")
        return False

    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        _last_preview_error = "npm not found — install Node.js to enable preview"
        print(f"   ⚠️ {_last_preview_error}")
        return False

    # Auto-patch missing npm packages before installing
    _patch_package_json_deps(frontend_dir)

    # Check if node_modules already exists (skip reinstall only if package.json was NOT just patched)
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists() and (node_modules / ".package-lock.json").exists():
        print("   ✅ Frontend deps already installed (skipping npm install)")
        return True

    print("   📦 Installing frontend dependencies...")
    try:
        result = subprocess.run(
            [npm_cmd, "install", "--prefer-offline", "--no-audit", "--no-fund"],
            cwd=frontend_dir,
            timeout=180,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            error_msg = result.stderr[:300] if result.stderr else "Unknown npm error"
            _last_preview_error = f"npm install failed: {error_msg}"
            print(f"   ⚠️ {_last_preview_error}")
            return False

        print("   ✅ Frontend deps installed")
        return True
    except subprocess.TimeoutExpired:
        _last_preview_error = "npm install timed out (>180s)"
        print(f"   ⚠️ {_last_preview_error}")
        return False
    except Exception as e:
        _last_preview_error = f"npm install error: {e}"
        print(f"   ⚠️ {_last_preview_error}")
        return False



def start_backend(backend_dir: Path) -> bool:
    """Start Flask backend server with health check."""
    global _backend_process, _last_preview_error

    app_file = backend_dir / "app.py"
    if not app_file.exists():
        print("   ⚠️ No backend/app.py found")
        return False

    try:
        env = os.environ.copy()
        env["FLASK_ENV"] = "production"
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        _backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        # Health check with retries
        print(f"   ⏳ Waiting for backend on port {PREVIEW_BACKEND_PORT}...")
        if _health_check(PREVIEW_BACKEND_PORT, "/", retries=6, delay=1.0):
            return True

        # Check if process crashed
        if _backend_process.poll() is not None:
            stdout = _backend_process.stdout.read().decode(errors="replace") if _backend_process.stdout else ""
            stderr = _backend_process.stderr.read().decode(errors="replace") if _backend_process.stderr else ""
            error = stderr or stdout
            _last_preview_error = f"Backend crashed: {error[:200]}"
            print(f"   ❌ {_last_preview_error}")
            return False

        # Process is running but not responding — might just be slow
        # Check port one more time
        if _is_port_in_use(PREVIEW_BACKEND_PORT):
            print("   ✅ Backend port is open (slow startup)")
            return True

        _last_preview_error = "Backend started but not responding"
        print(f"   ⚠️ {_last_preview_error}")
        return False

    except Exception as e:
        _last_preview_error = f"Backend start error: {e}"
        print(f"   ❌ {_last_preview_error}")
        return False


def start_frontend(frontend_dir: Path) -> bool:
    """Start Vite dev server with health check."""
    global _frontend_process, _last_preview_error

    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        return False

    # Check node_modules exists
    if not (frontend_dir / "node_modules").exists():
        _last_preview_error = "node_modules missing — npm install may have failed"
        print(f"   ⚠️ {_last_preview_error}")
        return False

    try:
        env = os.environ.copy()
        env["BROWSER"] = "none"  # Prevent Vite from opening a browser

        # Use npx vite directly for more reliable startup
        npx_cmd = shutil.which("npx")
        if npx_cmd:
            cmd = [npx_cmd, "vite", "--host", "0.0.0.0", "--port", str(PREVIEW_FRONTEND_PORT)]
        else:
            cmd = [npm_cmd, "run", "dev"]

        _frontend_process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        # Health check with retries (Vite takes a moment to start)
        print(f"   ⏳ Waiting for frontend on port {PREVIEW_FRONTEND_PORT}...")
        if _health_check(PREVIEW_FRONTEND_PORT, "/", retries=10, delay=1.0):
            return True

        # Check if process crashed
        if _frontend_process.poll() is not None:
            stdout = _frontend_process.stdout.read().decode(errors="replace") if _frontend_process.stdout else ""
            stderr = _frontend_process.stderr.read().decode(errors="replace") if _frontend_process.stderr else ""
            error = stderr or stdout
            _last_preview_error = f"Frontend crashed: {error[:200]}"
            print(f"   ❌ {_last_preview_error}")
            return False

        # Process running but no HTTP response — check port
        if _is_port_in_use(PREVIEW_FRONTEND_PORT):
            print("   ✅ Frontend port is open (slow startup)")
            return True

        _last_preview_error = "Vite dev server started but not responding"
        print(f"   ⚠️ {_last_preview_error}")
        return False

    except Exception as e:
        _last_preview_error = f"Frontend start error: {e}"
        print(f"   ⚠️ {_last_preview_error}")
        return False


def stop_preview():
    """Stop all preview processes and free ports."""
    global _backend_process, _frontend_process

    for proc, name in [(_backend_process, "backend"), (_frontend_process, "frontend")]:
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"   🛑 Stopped {name} process")
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                    print(f"   🛑 Force-killed {name} process")
                except Exception:
                    pass
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    _backend_process = None
    _frontend_process = None


def is_preview_running() -> dict:
    """Check current preview status."""
    backend_alive = _backend_process is not None and _backend_process.poll() is None
    frontend_alive = _frontend_process is not None and _frontend_process.poll() is None

    backend_port_open = _is_port_in_use(PREVIEW_BACKEND_PORT)
    frontend_port_open = _is_port_in_use(PREVIEW_FRONTEND_PORT)

    return {
        "backend_running": backend_alive or backend_port_open,
        "frontend_running": frontend_alive or frontend_port_open,
        "backend_port": PREVIEW_BACKEND_PORT,
        "frontend_port": PREVIEW_FRONTEND_PORT,
    }
