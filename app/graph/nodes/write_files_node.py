"""
write_files_node.py
-------------------
Writes generated files to disk and creates API contract for testing.
"""

from pathlib import Path
import json
import re
import ast

from app.core.state import ProjectState
from app.utils.file_ops import write_files


# ------------------ SAFETY ------------------

def is_valid_python(code: str) -> bool:
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True
    except:
        return False


def fix_common_python_bugs(code: str) -> str:
    """
    Fix obvious crashes without changing logic.
    """
    # Safe None handling for request.get_json()
    code = code.replace(
        "request.get_json().get(",
        "(request.get_json() or {}).get("
    )
    return code


# ------------------ EXTRACTION ------------------

def extract_routes_from_backend(code: str) -> list:
    """
    Extract Flask routes with their HTTP methods.
    Returns list of (method, path) tuples.
    """
    routes = []

    # Pattern: @app.route('/path', methods=['GET', 'POST'])
    pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?"

    for match in re.finditer(pattern, code):
        raw_path = match.group(1)
        methods_str = match.group(2)

        # Normalize dynamic params: /delete/<int:id> -> /delete/1
        path = re.sub(r"<[^>]+>", "1", raw_path)

        if methods_str:
            methods = re.findall(r"['\"](\w+)['\"]", methods_str)
        else:
            methods = ["GET"]  # Default method

        for m in methods:
            routes.append((m.upper(), path))

    return routes


def extract_expected_json_keys(code: str, route_path: str) -> list:
    """
    Extract ALL required JSON keys from a route handler.
    
    Handles multiple patterns:
    1) 'key' not in data
    2) key = data.get('key')
    3) data['key']
    4) data.get('key', default)
    """
    # Find the route handler function
    # Match from @app.route to next @app.route or end
    escaped_path = re.escape(route_path.replace('/1', '/<[^>]+>'))
    pattern = rf"@app\.route\(['\"]({escaped_path}|{re.escape(route_path)})['\"].*?\ndef\s+\w+\([^)]*\):\s*(.*?)(?=\n@app\.route|\nif __name__|$)"
    
    match = re.search(pattern, code, re.DOTALL)
    if not match:
        # Try simpler pattern
        simple_pattern = rf"@app\.route\(['\"][^'\"]*{re.escape(route_path.split('/')[-1])}[^'\"]*['\"].*?\ndef\s+\w+\([^)]*\):\s*(.*?)(?=\n@app\.route|\nif __name__|$)"
        match = re.search(simple_pattern, code, re.DOTALL)
        if not match:
            return []

    block = match.group(2) if match.lastindex >= 2 else match.group(1)
    
    keys = set()

    # Pattern 1: 'key' not in data
    keys.update(re.findall(r"['\"](\w+)['\"]\s+not\s+in\s+data", block))
    
    # Pattern 2: data.get('key') or data.get("key")
    keys.update(re.findall(r"data\.get\(['\"](\w+)['\"]", block))
    
    # Pattern 3: data['key'] or data["key"]
    keys.update(re.findall(r"data\[['\"](\w+)['\"]\]", block))
    
    # Pattern 4: request.get_json().get('key')
    keys.update(re.findall(r"request\.get_json\(\)[^.]*\.get\(['\"](\w+)['\"]", block))

    return list(keys)


def generate_test_value(key: str) -> any:
    """Generate appropriate test value based on key name."""
    key_lower = key.lower()
    
    if 'id' in key_lower:
        return 1
    elif 'email' in key_lower:
        return "test@example.com"
    elif 'password' in key_lower:
        return "testpass123"
    elif 'name' in key_lower or 'title' in key_lower:
        return "Test Item"
    elif 'content' in key_lower or 'text' in key_lower or 'description' in key_lower:
        return "Test content here"
    elif 'price' in key_lower or 'amount' in key_lower:
        return 100
    elif 'quantity' in key_lower or 'count' in key_lower:
        return 5
    elif 'date' in key_lower:
        return "2024-01-01"
    elif 'url' in key_lower or 'link' in key_lower:
        return "https://example.com"
    elif 'done' in key_lower or 'completed' in key_lower or 'active' in key_lower:
        return True
    else:
        return "test"


# ------------------ MAIN NODE ------------------

def write_files_node(state: ProjectState) -> ProjectState:
    """
    Write all generated files to disk and create API contract.
    """
    project_dir = Path(state.get("project_dir", "app/workspace/generated_projects/todo_app"))
    project_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = state.get("files", {})
    
    print(f"\n📁 Writing {len(files_to_write)} files to {project_dir}")

    # ---------- Validate and fix backend ----------
    backend_code = files_to_write.get("backend/app.py", "")

    if backend_code:
        if not is_valid_python(backend_code):
            print("⚠️ Backend has syntax errors - attempting to proceed anyway")
        
        backend_code = fix_common_python_bugs(backend_code)
        files_to_write["backend/app.py"] = backend_code

    # ---------- Write all files ----------
    write_files(project_dir, files_to_write)
    print("✅ All files written to disk")

    # ---------- Build contract from backend ----------
    routes = extract_routes_from_backend(backend_code)
    
    endpoints = []
    request_fields = {}

    for method, path in routes:
        keys = extract_expected_json_keys(backend_code, path)
        
        # Build request body with appropriate test values
        body = {k: generate_test_value(k) for k in keys}

        endpoints.append({
            "method": method,
            "path": path,
            "expect": 200,
            "body": body
        })

        request_fields[path] = keys

    contract_json = {
        "base_url": "http://localhost:5000",
        "endpoints": endpoints
    }

    # Write contract.json
    contract_path = project_dir / "backend" / "contract.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(json.dumps(contract_json, indent=2))

    print(f"📋 Contract created with {len(endpoints)} endpoints")
    for ep in endpoints:
        print(f"   {ep['method']} {ep['path']} - body: {list(ep['body'].keys())}")

    route_strings = [f"{m} {p}" for m, p in routes]

    return {
        "extracted_routes": route_strings,
        "request_fields": request_fields
    }
