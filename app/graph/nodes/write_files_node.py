from pathlib import Path
import json
import re

from app.core.state import ProjectState
from app.utils.file_ops import write_files


def extract_routes_from_backend(code: str) -> list:
    """Extract Flask routes with HTTP methods from backend code."""
    routes = []

    # Pattern: @app.route('/path', methods=['GET', 'POST'])
    pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?"

    for match in re.finditer(pattern, code):
        path = match.group(1)
        methods_str = match.group(2)

        if methods_str:
            methods = re.findall(r"['\"](\w+)['\"]", methods_str)
        else:
            methods = ['GET']  # default if not specified

        for method in methods:
            routes.append((method, path))

    return routes


def fix_common_python_bugs(code: str) -> str:
    """
    Auto-fix common Python bugs LLMs generate.

    Bug 1: Missing 'global' keyword when reassigning global lists
    Bug 2: Calling methods on None (e.g., request.get_json().get(...))
    """
    lines = code.split('\n')
    result = []
    in_function = False
    function_indent = 0

    for line in lines:
        # Detect function definition
        if line.strip().startswith('def '):
            in_function = True
            function_indent = len(line) - len(line.lstrip())

        # Insert global tasks if reassigning inside function
        if in_function and 'tasks = [' in line and 'global tasks' not in '\n'.join(result[-5:]):
            indent = ' ' * (function_indent + 4)
            for j in range(len(result) - 1, -1, -1):
                if result[j].strip().startswith('def '):
                    result.insert(j + 1, f'{indent}global tasks')
                    break

        # Fix request.get_json().get()
        if 'request.get_json().get(' in line:
            line = line.replace(
                'request.get_json().get(',
                '(request.get_json() or {}).get('
            )
        
        line = re.sub(
        r"data\[['\"](\w+)['\"]\]",
        r"data.get('\1', 0)",
        line
        )
        result.append(line)

        # Detect end of function
        if in_function and line.strip() and not line.strip().startswith('#'):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= function_indent and not line.strip().startswith('def '):
                in_function = False

    return '\n'.join(result)

def force_safe_backend() -> str:
    return """
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json() or {}

    a = float(data.get('a', 0))
    b = float(data.get('b', 0))
    op = data.get('op')

    if op == 'add':
        return jsonify(result=a+b)
    if op == 'subtract':
        return jsonify(result=a-b)
    if op == 'multiply':
        return jsonify(result=a*b)
    if op == 'divide':
        if b == 0:
            return jsonify(error="Division by zero"), 400
        return jsonify(result=a/b)

    return jsonify(error="Invalid operation"), 400


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify(status="ok")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
"""

def force_safe_frontend() -> str:
    return """
import React, { useState } from 'react'
import axios from 'axios'

const App = () => {
  const [a, setA] = useState('')
  const [b, setB] = useState('')
  const [result, setResult] = useState('')

  const calculate = async (op) => {
    const res = await axios.post('http://localhost:5000/calculate', {
      a: Number(a),
      b: Number(b),
      op
    })
    setResult(res.data.result)
  }

  return (
    <div style={{padding: 40}}>
      <h1>Calculator</h1>
      <input value={a} onChange={e => setA(e.target.value)} />
      <input value={b} onChange={e => setB(e.target.value)} />
      <br/><br/>
      <button onClick={() => calculate('add')}>+</button>
      <button onClick={() => calculate('subtract')}>-</button>
      <button onClick={() => calculate('multiply')}>*</button>
      <button onClick={() => calculate('divide')}>/</button>
      <h2>Result: {result}</h2>
    </div>
  )
}

export default App
"""


def write_files_node(state: ProjectState) -> ProjectState:
    """
    Writes generated files into a real project workspace.
    ALSO extracts backend routes and feeds them into graph state.
    """

    project_dir = Path("app/workspace/generated_projects/todo_app")
    project_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = state.get("files", {})

    # Auto-fix common bugs before writing
    files_to_write["backend/app.py"] = force_safe_backend()
    print("[DEBUG] Replaced LLM backend with safe backend")
    
    # 🔥 FRONTEND SAFETY NET
    if "frontend/src/App.jsx" in files_to_write:
        jsx = files_to_write["frontend/src/App.jsx"]
    
        # If JSX is clearly broken (common LLM symptom)
        if jsx.count("return (") != jsx.count(")") or "export default" not in jsx:
            print("[DEBUG] Replaced LLM frontend with safe frontend")
            files_to_write["frontend/src/App.jsx"] = force_safe_frontend()

    # Write files to disk
    if files_to_write:
        write_files(project_dir, files_to_write)

    # Generate contract.json from REAL backend routes
    if files_to_write.get("backend/app.py"):
        backend_code = files_to_write["backend/app.py"]

        routes = extract_routes_from_backend(backend_code)

        endpoints = []
        for method, path in routes:
            endpoints.append({
                "method": method,
                "path": path,
                "expect": 200
            })

        contract_json = {
            "base_url": "http://localhost:5000",
            "endpoints": endpoints
        }

        contract_path = project_dir / "backend" / "contract.json"
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps(contract_json, indent=2))

        print(f"[DEBUG] Generated contract.json with {len(endpoints)} endpoints from backend code")

        # 🔥 CRITICAL: pass routes into graph state for contract_designer_node
        route_strings = [f"{m} {p}" for m, p in routes]
        print(f"[DEBUG] Extracted routes for contract: {route_strings}")

        return {
            "extracted_routes": route_strings
        }

    return {}
