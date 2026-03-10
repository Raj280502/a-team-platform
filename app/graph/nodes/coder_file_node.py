"""
coder_file_node.py
------------------
Generates code files based on project scope and architecture.
Enhanced with better prompts, streaming support, and multi-stack awareness.
"""

from app.core.state import ProjectState
from app.core.llm import get_llm
from app.utils.file_ops import normalize_code
from app.utils.code_validator import validate_file
import json
import re

# Maximum retries for generating a single file
MAX_FILE_RETRIES = 3


def coder_file_node(state: ProjectState) -> ProjectState:
    """
    Generates ALL code files based on project_scope and architecture.
    
    - Reads file_plan from state (set by architect)
    - Generates each file using LLM with appropriate context
    - Validates and retries if code is truncated
    - Post-processes code for common fixes
    """
    llm = get_llm(role="coder")

    project_scope = state.get("project_scope", {})
    architecture = state.get("architecture", {})
    file_plan = state.get("file_plan", [])

    project_goal = project_scope.get("project_goal", "A web application")
    features = project_scope.get("core_features", [])
    pages = project_scope.get("pages", [])
    data_models = project_scope.get("data_models", [])
    api_endpoints = project_scope.get("api_endpoints", [])
    ui_style = project_scope.get("ui_style", "modern clean")
    
    # Architecture details
    api_routes = architecture.get("api_routes", [])
    components = architecture.get("components", [])

    # Start with existing files so we don't overwrite good files
    generated = state.get("files", {}).copy()
    generation_issues = []
    failed_history = state.get("failed_file_history", [])

    # If specific files were flagged for regeneration, only generate those
    files_to_regenerate = state.get("files_to_regenerate") or []
    targets = files_to_regenerate if files_to_regenerate else file_plan

    print(f"\n🔨 Generating {len(targets)} files for: {project_goal}")

    # Build a context dict that all generators can use
    context = {
        "project_goal": project_goal,
        "features": features,
        "pages": pages,
        "data_models": data_models,
        "api_endpoints": api_endpoints,
        "api_routes": api_routes,
        "components": components,
        "ui_style": ui_style,
    }

    # ============================================
    # Generate each target file WITH RETRY
    # ============================================
    for file_path in targets:
        print(f"   📄 Generating: {file_path}")

        content = None
        last_issues = []

        for attempt in range(MAX_FILE_RETRIES):
            # Determine file type and generate accordingly
            if file_path.endswith(".py") and "app.py" in file_path:
                content = generate_backend_file(llm, context, attempt)
            elif file_path.endswith(".py"):
                content = generate_python_file(llm, file_path, context)
            elif "App.jsx" in file_path:
                backend_code = generated.get("backend/app.py", "")
                routes = extract_routes(backend_code)
                content = generate_app_jsx(llm, context, routes, attempt)
            elif "App.css" in file_path:
                content = generate_app_css(context)
                break
            elif "index.css" in file_path:
                content = generate_index_css()
                break
            elif "main.jsx" in file_path:
                content = generate_main_jsx()
                break
            elif "vite.config" in file_path:
                content = generate_vite_config()
                break
            elif file_path.endswith(".html") and "index" in file_path:
                content = generate_html_file(project_goal)
                break
            elif "package.json" in file_path and "frontend" in file_path:
                content = generate_package_json(project_goal)
                break
            elif "requirements.txt" in file_path:
                content = generate_requirements_txt()
                break
            elif "components/" in file_path and file_path.endswith(".jsx"):
                comp_info = find_component_info(file_path, components)
                backend_code = generated.get("backend/app.py", "")
                routes = extract_routes(backend_code)
                content = generate_component_file(llm, file_path, comp_info, context, routes)
            else:
                content = generate_generic_file(llm, file_path, context)
                break

            # Validate generated code
            is_valid, issues = validate_file(content, file_path)

            if is_valid:
                print(f"      ✅ Valid on attempt {attempt + 1}")
                break
            else:
                last_issues = issues
                print(f"      ⚠️ Issues on attempt {attempt + 1}: {issues[:2]}")
                if attempt < MAX_FILE_RETRIES - 1:
                    print(f"      🔄 Retrying...")
        else:
            print(f"      ❌ Failed after {MAX_FILE_RETRIES} attempts")
            if file_path in failed_history and "App.jsx" in file_path:
                print(f"      🛡️ Using template fallback")
                content = get_fallback_app_jsx(context)
                generated[file_path] = content
                continue

            generation_issues.append({"file": file_path, "issues": last_issues})
            failed_history.append(file_path)

        generated[file_path] = content

    # ============================================
    # Extract routes for contract testing
    # ============================================
    backend_code = generated.get("backend/app.py", "")
    routes = extract_routes(backend_code)
    print(f"   🔗 Extracted {len(routes)} API routes: {routes}")
    # Post-generation pass: fix missing component imports across all JSX files
    generated = fix_all_jsx_imports(generated)
    if generation_issues:
        print(f"\n   ⚠️ {len(generation_issues)} files had issues (will attempt repair)")

    return {
        "files": generated,
        "extracted_routes": routes,
        "generation_issues": generation_issues,
        "files_to_regenerate": [],
        "failed_file_history": failed_history,
        "current_step": "coder_complete",
    }


# ============================================
# FILE GENERATORS
# ============================================

def generate_backend_file(llm, ctx: dict, attempt: int = 0) -> str:
    """Generate Python Flask backend file with rich context."""
    retry_emphasis = ""
    if attempt > 0:
        retry_emphasis = f"""
CRITICAL: Previous attempt ({attempt}) was INCOMPLETE/TRUNCATED.
- The code MUST be 100% complete
- Do NOT stop mid-function
- Include ALL imports, routes, and the app.run() block
- VERIFY the code ends with app.run(...) before finishing
"""

    routes_info = json.dumps(ctx["api_routes"], indent=2) if ctx["api_routes"] else json.dumps(ctx["api_endpoints"], indent=2)

    prompt = f"""You are an expert Python Flask developer. Generate a COMPLETE, WORKING backend API.
{retry_emphasis}
PROJECT: {ctx['project_goal']}
DATA MODELS: {json.dumps(ctx['data_models'])}
FEATURES TO IMPLEMENT: {json.dumps(ctx['features'], indent=2)}
API ROUTES TO IMPLEMENT: {routes_info}

STRICT REQUIREMENTS:
1. Start with these imports:
   from flask import Flask, request, jsonify
   from flask_cors import CORS
   import uuid

2. Initialize app:
   app = Flask(__name__)
   CORS(app)

3. Use IN-MEMORY storage at module level:
   items = []  # or appropriate data structure for each model

4. Create REST API routes for EACH feature:
   - Use /api/ prefix for all routes (e.g., /api/tasks)
   - GET routes for retrieving/listing data
   - POST routes for creating data  
   - PUT routes for updating data
   - DELETE routes for removing data
   - Generate unique IDs with uuid.uuid4().hex[:8]

5. Add convenience routes:
   @app.route('/')
   def root():
       return jsonify({{"message": "API is running", "endpoints": [...]}})
   
   @app.route('/api/health')
   def health():
       return jsonify({{"status": "ok"}})

6. Each route must:
   - Handle request.get_json() safely: data = request.get_json() or {{}}
   - Return jsonify() responses
   - Return appropriate status codes (200, 201, 400, 404)

7. End with:
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=False)

OUTPUT RULES:
- Output ONLY Python code
- NO markdown code fences (```)
- NO explanations or comments about what you're doing
- Start directly with 'from flask import'
- Make sure the code is COMPLETE and can run
- CRITICAL: Code MUST end with app.run()

Generate the complete Flask backend:"""

    response = llm.invoke(prompt)
    code = normalize_code(response.content)
    code = fix_backend_code(code)
    return code


def generate_app_jsx(llm, ctx: dict, routes: list, attempt: int = 0) -> str:
    """Generate React App.jsx with full UI using architecture context."""
    routes_info = json.dumps(routes, indent=2) if routes else "[]"
    components_info = json.dumps(ctx["components"], indent=2) if ctx["components"] else "[]"

    retry_emphasis = ""
    if attempt > 0:
        retry_emphasis = f"""
CRITICAL: Previous attempt ({attempt}) was INCOMPLETE/TRUNCATED.
- The component MUST be 100% complete
- Do NOT stop mid-function or mid-JSX
- Include ALL state, functions, and UI elements
- VERIFY the code ends with 'export default App;' before finishing
"""

    prompt = f"""You are an expert React developer. Generate a COMPLETE, BEAUTIFUL App.jsx component.
{retry_emphasis}
PROJECT: {ctx['project_goal']}
FEATURES: {json.dumps(ctx['features'], indent=2)}
UI STYLE: {ctx['ui_style']}
BACKEND API ROUTES: {routes_info}
BACKEND URL: Use relative paths like /api/... (the Vite dev server proxies /api to the backend)
COMPONENT ARCHITECTURE: {components_info}
PAGES: {json.dumps(ctx['pages'], indent=2)}

REQUIREMENTS:
1. Import statements (MUST include ALL of these):
   import React, {{ useState, useEffect }} from 'react';
   import axios from 'axios';
   import './App.css';
   CRITICAL: You MUST import EVERY child component you reference in JSX.
   For each <ComponentName /> in the render, add at the top:
     import ComponentName from './components/ComponentName';
   If COMPONENT ARCHITECTURE lists components, import ALL of them.

2. Create functional component: function App() {{ ... }}

3. State management with useState:
   - State for each form field
   - State for data lists
   - State for loading/error/success messages
   - State for active filters/tabs

4. API calls with axios:
   - Use RELATIVE paths: axios.get('/api/items') — the Vite proxy routes /api to the backend
   - Use the routes from BACKEND API ROUTES
   - Handle errors with try/catch
   - Show loading states during API calls

5. UI Requirements — Make it STUNNING:
   - Modern, clean layout with max-width container
   - Beautiful gradient or solid color header
   - Card-based design with subtle shadows and rounded corners
   - Form inputs with proper labels and placeholders
   - Styled buttons with hover effects (transform, box-shadow)
   - Data displayed in clean cards or list items
   - Status messages (success: green, error: red) that auto-dismiss
   - Empty state messages when no data exists
   - Smooth hover animations on interactive elements
   - Responsive design that looks good on all screen sizes
   - Use CSS classes from App.css (don't use excessive inline styles)
   - Icons or emoji to make the UI feel alive

6. End with:
   export default App;

OUTPUT RULES:
- Output ONLY JSX code
- NO markdown code fences
- NO explanations
- Start with 'import React'
- Component MUST be complete — no truncation at all
- MUST have 'export default App;' at the end

Generate the complete App.jsx:"""

    response = llm.invoke(prompt)
    code = normalize_code(response.content)
    code = fix_app_jsx(code)
    return code


def generate_component_file(llm, file_path: str, comp_info: dict, ctx: dict, routes: list) -> str:
    """Generate a React component file based on architecture spec."""
    comp_name = comp_info.get("name", file_path.split("/")[-1].replace(".jsx", ""))
    comp_desc = comp_info.get("description", "A reusable component")
    
    prompt = f"""You are an expert React developer. Generate a COMPLETE React component.

COMPONENT: {comp_name}
DESCRIPTION: {comp_desc}
FILE PATH: {file_path}
PROJECT: {ctx['project_goal']}
BACKEND URL: Use relative paths like /api/... (Vite proxy handles routing)
AVAILABLE ROUTES: {json.dumps(routes)}

REQUIREMENTS:
- Import React and any needed hooks
- Import axios if this component makes API calls
- Accept props as needed
- Use modern functional component pattern
- Include proper error handling
- Style with CSS classes or clean inline styles
- Export as default

OUTPUT RULES:
- Output ONLY JSX code
- NO markdown code fences
- Start with import statements
- End with export default {comp_name};

Generate the complete component:"""

    response = llm.invoke(prompt)
    code = normalize_code(response.content)
    
    # Ensure export default
    if "export default" not in code:
        code += f"\n\nexport default {comp_name};"
    
    return code


def generate_python_file(llm, file_path: str, ctx: dict) -> str:
    """Generate generic Python file."""
    prompt = f"""Generate Python code for {file_path}.
PROJECT: {ctx['project_goal']}
FEATURES: {json.dumps(ctx['features'])}
OUTPUT: Only Python code, no markdown."""
    response = llm.invoke(prompt)
    return normalize_code(response.content)


def generate_main_jsx() -> str:
    """Generate main.jsx entry point with ErrorBoundary."""
    return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    console.error('App Error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return React.createElement('div', {
        style: { padding: '40px', textAlign: 'center', fontFamily: 'Inter, sans-serif',
          background: '#fef2f2', minHeight: '100vh', display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }
      },
        React.createElement('h2', { style: { color: '#dc2626', marginBottom: '16px' } },
          '⚠️ Something went wrong'),
        React.createElement('pre', {
          style: { background: '#fff', padding: '16px', borderRadius: '8px',
            maxWidth: '600px', overflow: 'auto', fontSize: '0.85rem',
            border: '1px solid #fecaca', textAlign: 'left' }
        }, String(this.state.error)),
        React.createElement('button', {
          onClick: () => window.location.reload(),
          style: { marginTop: '20px', padding: '10px 24px', background: '#667eea',
            color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer',
            fontSize: '1rem' }
        }, '🔄 Reload')
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);"""


def generate_vite_config() -> str:
    """Generate Vite configuration."""
    return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    headers: {
      'Content-Security-Policy': "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' ws: wss: http://127.0.0.1:*;"
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  }
});"""


def generate_html_file(project_goal: str) -> str:
    """Generate HTML file."""
    title = project_goal[:60] if project_goal else "Web Application"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>"""


def generate_app_css(ctx: dict) -> str:
    """Generate App.css with beautiful modern styles."""
    return """/* App Styles */
.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.app-header {
  text-align: center;
  padding: 40px 20px 30px;
  margin-bottom: 30px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.app-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.app-header p {
  opacity: 0.9;
  font-size: 1rem;
}

/* Forms */
.form-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #eee;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
  font-family: inherit;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
  background: white;
}

.form-input::placeholder {
  color: #9ca3af;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-danger {
  background: #ef4444;
  color: white;
  font-size: 0.8rem;
  padding: 6px 14px;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Cards / List items */
.item-card {
  background: white;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
}

.item-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.item-title {
  font-weight: 600;
  font-size: 1rem;
  color: #1f2937;
}

.item-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 4px;
}

.item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* Messages */
.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  font-weight: 500;
  animation: slideDown 0.3s ease;
}

.message-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.empty-state-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 1rem;
}

/* Filter bar */
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1.5px solid #e5e7eb;
  background: white;
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* Counter */
.counter {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-bottom: 16px;
}

/* Animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Checkbox */
.checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #667eea;
}

/* Completed state */
.completed .item-title {
  text-decoration: line-through;
  color: #9ca3af;
}
"""


def generate_index_css() -> str:
    """Generate global index.css."""
    return """/* Global Styles */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#root {
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  font-family: inherit;
}

input, textarea, select {
  font-family: inherit;
}
"""


def generate_package_json(project_goal: str) -> str:
    """Generate package.json."""
    name = re.sub(r"[^a-z0-9-]", "-", project_goal.lower()[:30]).strip("-") or "app"
    return f'''{{
  "name": "{name}",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  }},
  "devDependencies": {{
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }}
}}'''


def generate_requirements_txt() -> str:
    """Generate Python requirements.txt."""
    return """flask==3.0.0
flask-cors==4.0.0
"""


def generate_generic_file(llm, file_path: str, ctx: dict) -> str:
    """Generate any other file type using LLM."""
    prompt = f"""Generate the content for {file_path}.
PROJECT: {ctx['project_goal']}
FEATURES: {json.dumps(ctx['features'])}
OUTPUT: Only the file content, no markdown fences."""
    response = llm.invoke(prompt)
    return normalize_code(response.content)


# ============================================
# HELPERS
# ============================================

def find_component_info(file_path: str, components: list) -> dict:
    """Find component info from architecture by file path."""
    for comp in components:
        if comp.get("file_path") == file_path:
            return comp
    # Fallback: extract name from file path
    name = file_path.split("/")[-1].replace(".jsx", "")
    return {"name": name, "description": f"Component: {name}"}


def get_fallback_app_jsx(ctx: dict) -> str:
    """Return a working fallback App.jsx."""
    return """import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API = '';

function App() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API}/api/health`);
      if (res.data.status === 'ok') {
        setMessage('Connected to backend!');
      }
    } catch (err) {
      setMessage('Cannot connect to backend');
    }
  };

  return (
    <div className="app">
      <div className="app-header">
        <h1>""" + ctx.get('project_goal', 'My App')[:40] + """</h1>
        <p>Generated by AI Code Factory</p>
      </div>
      {message && <div className="message message-success">{message}</div>}
      <div className="form-card">
        <p>App is running! Edit App.jsx to customize.</p>
      </div>
    </div>
  );
}

export default App;"""


def fix_backend_code(code: str) -> str:
    """Fix common issues in LLM-generated backend code."""
    lines = code.split("\n")

    # Ensure flask_cors import exists
    has_cors_import = any("flask_cors" in line for line in lines)
    has_cors_call = any("CORS(app)" in line for line in lines)

    if not has_cors_import:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.startswith("from flask import") or line.startswith("import flask"):
                new_lines.append("from flask_cors import CORS")
        lines = new_lines

    if not has_cors_call:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if "app = Flask(" in line:
                new_lines.append("CORS(app)")
        lines = new_lines

    # Ensure uuid import if used
    code = "\n".join(lines)
    if "uuid" in code and "import uuid" not in code:
        code = "import uuid\n" + code

    # Ensure app.run exists at end
    if "app.run(" not in code:
        code += "\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000, debug=False)"

    # Fix common None handling
    code = code.replace(
        "request.get_json().get(", "(request.get_json() or {}).get("
    )

    return code


# PascalCase JSX elements that should NOT be auto-imported
_JSX_BUILTINS = {
    'React', 'Fragment', 'Suspense', 'StrictMode', 'Profiler',
    'App',  # Don't import App from within App.jsx
}


def fix_missing_component_imports(code: str, filename: str = "App.jsx") -> str:
    """
    Scan JSX code for PascalCase component references (e.g. <SearchBar />)
    and inject missing import statements for them.
    """
    # Find PascalCase tags: <SomeName or <SomeName>
    used_components = set(re.findall(r'<([A-Z][A-Za-z0-9]+)', code))
    used_components -= _JSX_BUILTINS
    if not used_components:
        return code

    # Gather already-imported names
    already_imported = set(re.findall(r'import\s+(\w+)\s+from', code))
    for destructured in re.findall(r'import\s*\{([^}]+)\}\s*from', code):
        for name in destructured.split(','):
            already_imported.add(name.strip())

    missing = used_components - already_imported
    if not missing:
        return code

    # Build import lines
    new_imports = []
    for comp in sorted(missing):
        new_imports.append(f"import {comp} from './components/{comp}';")

    # Insert after the last existing import line
    lines = code.split('\n')
    last_import_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import_idx = i

    if last_import_idx >= 0:
        for j, imp in enumerate(new_imports):
            lines.insert(last_import_idx + 1 + j, imp)
    else:
        lines = new_imports + [''] + lines

    comp_names = ', '.join(sorted(missing))
    print(f"      \U0001f527 Auto-injected imports in {filename}: {comp_names}")

    return '\n'.join(lines)


def fix_app_jsx(code: str) -> str:
    """Fix common issues in LLM-generated App.jsx."""
    # Ensure React import
    if "import React" not in code:
        code = "import React, { useState, useEffect } from 'react';\n" + code

    # Ensure axios import
    if "import axios" not in code and "axios" in code:
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("import React"):
                lines.insert(i + 1, "import axios from 'axios';")
                break
        code = "\n".join(lines)

    # Ensure CSS import
    if "import './App.css'" not in code and "import './App.css'" not in code:
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("import React") or line.startswith("import axios"):
                continue
            if line.startswith("import") or line == "":
                continue
            lines.insert(i, "import './App.css';")
            break
        code = "\n".join(lines)

    # Ensure export default exists
    if "export default" not in code:
        code += "\n\nexport default App;"

    # Auto-fix missing component imports
    code = fix_missing_component_imports(code, "App.jsx")

    return code


def fix_all_jsx_imports(generated_files: dict) -> dict:
    """
    Post-generation pass: fix missing component imports across all JSX files.
    Cross-references generated files to know which components exist.
    """
    # Collect known component names from the generated file set
    known_components = set()
    for path in generated_files:
        if 'components/' in path and path.endswith('.jsx'):
            name = path.split('/')[-1].replace('.jsx', '')
            known_components.add(name)

    if not known_components:
        return generated_files

    fixed_count = 0
    for path, content in list(generated_files.items()):
        if not path.endswith('.jsx') or not content:
            continue

        fixed = fix_missing_component_imports(content, filename=path.split('/')[-1])
        if fixed != content:
            generated_files[path] = fixed
            fixed_count += 1

    if fixed_count:
        print(f"   \U0001f527 Fixed imports in {fixed_count} JSX file(s)")

    return generated_files


def extract_routes(code: str) -> list:
    """Extract Flask routes from backend code."""
    routes = []
    pattern = r"@app\.route\(['\"]([^'\"]+)['\"]"
    for match in re.finditer(pattern, code):
        route = match.group(1)
        if route not in routes:
            routes.append(route)
    return routes
