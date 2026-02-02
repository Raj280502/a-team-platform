"""
coder_file_node.py
------------------
Generates code files based on project scope and architecture.

FULLY GENERALIZED - Works for ANY type of application.
Includes retry logic for truncated code.
"""

from app.core.state import ProjectState
from app.core.llm import get_llm
from app.utils.file_ops import normalize_code
from app.utils.code_validator import validate_file, is_code_truncated
import json
import re

# Maximum retries for generating a single file
MAX_FILE_RETRIES = 3


def get_fallback_app_jsx() -> str:
    """Return a working fallback App.jsx when LLM fails."""
    return """import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://localhost:5000/items');
      setItems(response.data || []);
    } catch (error) {
      setMessage('Error loading items');
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/add', { title, description });
      setTitle('');
      setDescription('');
      setMessage('Added successfully!');
      fetchItems();
    } catch (error) {
      setMessage('Error adding item');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/delete/${id}`);
      setMessage('Deleted successfully!');
      fetchItems();
    } catch (error) {
      setMessage('Error deleting item');
    }
  };

  return (
    <div style={{
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '30px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ textAlign: 'center', color: '#333' }}>Todo App</h1>
        
        {message && (
          <div style={{
            padding: '10px',
            marginBottom: '20px',
            background: '#d4edda',
            borderRadius: '5px',
            color: '#155724'
          }}>
            {message}
          </div>
        )}

        <form onSubmit={handleAdd} style={{ marginBottom: '30px' }}>
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '12px',
              marginBottom: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px'
            }}
          />
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              marginBottom: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px'
            }}
          />
          <button type="submit" style={{
            width: '100%',
            padding: '12px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            fontSize: '16px',
            cursor: 'pointer'
          }}>
            Add Task
          </button>
        </form>

        <div>
          {items.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#999' }}>No items yet</p>
          ) : (
            items.map((item, index) => (
              <div key={item.id || index} style={{
                padding: '15px',
                marginBottom: '10px',
                background: '#f8f9fa',
                borderRadius: '5px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <strong>{item.title || 'Untitled'}</strong>
                  <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '14px' }}>
                    {item.description || ''}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(item.id)}
                  style={{
                    padding: '8px 16px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer'
                  }}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
"""


def coder_file_node(state: ProjectState) -> ProjectState:
    """
    Generates ALL code files based on project_scope and architecture.
    
    GENERALIZED approach:
    - Reads file_plan from state (set by architect)
    - Generates each file using LLM with appropriate context
    - Validates and retries if code is truncated
    - Post-processes code for common fixes
    """
    llm = get_llm(role="coder")
    
    project_scope = state.get("project_scope", {})
    architecture = state.get("architecture", {})
    file_plan = state.get("file_plan", [])
    
    project_goal = project_scope.get('project_goal', 'A web application')
    features = project_scope.get('core_features', [])
    
    # Start with existing files so we don't overwrite good files
    generated = state.get("files", {}).copy()
    generation_issues = []
    failed_history = state.get("failed_file_history", [])

    # If specific files were flagged for regeneration, only generate those
    files_to_regenerate = state.get("files_to_regenerate") or []
    targets = files_to_regenerate if files_to_regenerate else file_plan

    print(f"\n🔨 Generating {len(targets)} files for: {project_goal}")

    # ============================================
    # Generate each target file WITH RETRY
    # ============================================
    for file_path in targets:
        print(f"   📄 Generating: {file_path}")
        
        content = None
        last_issues = []
        
        for attempt in range(MAX_FILE_RETRIES):
            # Determine file type and generate accordingly
            if file_path.endswith('.py') and 'app.py' in file_path:
                content = generate_backend_file(llm, file_path, project_goal, features, attempt)
            elif file_path.endswith('.py'):
                content = generate_python_file(llm, file_path, project_goal, features)
            elif 'App.jsx' in file_path:
                # Generate App.jsx AFTER backend so we have routes
                backend_code = generated.get("backend/app.py", "")
                routes = extract_routes(backend_code)
                content = generate_app_jsx(llm, project_goal, features, routes, attempt)
            elif 'main.jsx' in file_path:
                content = generate_main_jsx()
                break  # Template, no need to validate
            elif 'vite.config' in file_path:
                content = generate_vite_config()
                break  # Template, no need to validate
            elif file_path.endswith('.html'):
                content = generate_html_file(project_goal)
                break  # Template, no need to validate
            elif file_path.endswith('.css'):
                content = generate_css_file()
                break  # Template, no need to validate
            elif 'package.json' in file_path:
                content = generate_package_json(project_goal)
                break  # Template, no need to validate
            elif 'requirements.txt' in file_path:
                content = generate_requirements_txt()
                break  # Template, no need to validate
            else:
                content = generate_generic_file(llm, file_path, project_goal, features)
                break  # Generic files, skip validation
            
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
            # All retries failed - check if this file has failed before
            print(f"      ❌ Failed after {MAX_FILE_RETRIES} attempts")
            
            # If this file failed before, use template fallback immediately
            if file_path in failed_history:
                print(f"      🛡️ Using template fallback (file failed before)")
                if 'App.jsx' in file_path:
                    content = get_fallback_app_jsx()
                    generated[file_path] = content
                    continue
            
            generation_issues.append({
                "file": file_path,
                "issues": last_issues
            })
            failed_history.append(file_path)
        
        generated[file_path] = content
    
    # ============================================
    # Extract routes for contract testing
    # ============================================
    backend_code = generated.get("backend/app.py", "")
    routes = extract_routes(backend_code)
    print(f"   🔗 Extracted {len(routes)} API routes: {routes}")
    
    if generation_issues:
        print(f"\n   ⚠️ {len(generation_issues)} files had issues (will attempt repair)")

    # Clear files_to_regenerate in the state (we either fixed them or marked issues)
    return {
        "files": generated,
        "extracted_routes": routes,
        "generation_issues": generation_issues,
        "files_to_regenerate": [],
        "failed_file_history": failed_history,
    }


# ============================================
# FILE GENERATORS
# ============================================

def generate_backend_file(llm, file_path: str, project_goal: str, features: list, attempt: int = 0) -> str:
    """Generate Python Flask backend file."""
    
    # Stronger instructions on retry
    retry_emphasis = ""
    if attempt > 0:
        retry_emphasis = f"""
CRITICAL: Previous attempt ({attempt}) was INCOMPLETE/TRUNCATED.
- The code MUST be 100% complete
- Do NOT stop mid-function
- Include ALL imports, routes, and the app.run() block
- VERIFY the code ends with app.run(...) before finishing

"""
    
    prompt = f"""You are an expert Python Flask developer. Generate a COMPLETE, WORKING backend API.
{retry_emphasis}
PROJECT: {project_goal}
FEATURES TO IMPLEMENT: {json.dumps(features, indent=2)}

STRICT REQUIREMENTS:
1. Start with these imports:
   from flask import Flask, request, jsonify
   from flask_cors import CORS

2. Initialize app:
   app = Flask(__name__)
   CORS(app)

3. Use IN-MEMORY storage at module level:
   items = []  # or appropriate data structure

4. Create REST API routes for EACH feature:
   - GET routes for retrieving data
   - POST routes for creating data
   - PUT routes for updating data  
   - DELETE routes for removing data
   - Use simple paths like /items, /add, /delete (NOT /api/...)

5. Add a root route for API info:
   @app.route('/')
   def root():
       return jsonify({{"message": "API is running", "routes": ["/health", "/items", "/add"]}})

6. Each route must:
   - Handle request.get_json() safely: data = request.get_json() or {{}}
   - Return jsonify() responses
   - Return appropriate status codes (200, 201, 400, 404)

7. Add a health check route:
   @app.route('/health')
   def health():
       return jsonify({{"status": "ok"}})

8. End with:
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


def generate_app_jsx(llm, project_goal: str, features: list, routes: list, attempt: int = 0) -> str:
    """Generate React App.jsx with full UI."""
    
    routes_info = json.dumps(routes, indent=2) if routes else '[]'
    
    # Stronger instructions on retry
    retry_emphasis = ""
    if attempt > 0:
        retry_emphasis = f"""
CRITICAL: Previous attempt ({attempt}) was INCOMPLETE/TRUNCATED.
- The component MUST be 100% complete
- Do NOT stop mid-function or mid-JSX
- Include ALL state, functions, and UI elements
- VERIFY the code ends with 'export default App;' before finishing
- Close ALL brackets and parentheses properly

"""
    
    prompt = f"""You are an expert React developer. Generate a COMPLETE, BEAUTIFUL App.jsx component.
{retry_emphasis}
PROJECT: {project_goal}
FEATURES: {json.dumps(features, indent=2)}
BACKEND API ROUTES: {routes_info}
BACKEND URL: http://localhost:5000

REQUIREMENTS:
1. Import statements (MUST include):
   import React, {{ useState, useEffect }} from 'react';
   import axios from 'axios';

2. Create functional component:
   function App() {{ ... }}

3. State management with useState:
   - State for form inputs
   - State for data list/items
   - State for loading/error messages

4. API calls with axios:
   - Use http://localhost:5000 as base URL
   - Use the routes from BACKEND API ROUTES above
   - Handle errors with try/catch
   - Example: await axios.post('http://localhost:5000/add', data)

5. UI Requirements:
   - Create forms with inputs for each feature
   - Add buttons for actions (Add, Delete, Update, etc.)
   - Display list of items/data
   - Show success/error messages
   - Use inline styles for a clean, modern look

6. Make it BEAUTIFUL:
   - Use a gradient background
   - Add padding and margins
   - Round corners on elements
   - Hover effects on buttons
   - Clean typography

7. End with:
   export default App;

OUTPUT RULES:
- Output ONLY JSX code
- NO markdown code fences
- NO explanations
- Start with 'import React'
- Component MUST be complete - no truncation
- MUST have export default App at the end
- CRITICAL: Ensure code ends with 'export default App;'

Generate the complete App.jsx:"""

    response = llm.invoke(prompt)
    code = normalize_code(response.content)
    code = fix_app_jsx(code)
    
    return code


def generate_python_file(llm, file_path: str, project_goal: str, features: list) -> str:
    """Generate generic Python file."""
    prompt = f"""Generate Python code for {file_path}.
PROJECT: {project_goal}
FEATURES: {json.dumps(features)}
OUTPUT: Only Python code, no markdown."""
    response = llm.invoke(prompt)
    return normalize_code(response.content)


def generate_main_jsx() -> str:
    """Generate main.jsx entry point."""
    return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
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
    port: 5173
  }
});"""


def generate_html_file(project_goal: str) -> str:
    """Generate HTML file."""
    title = project_goal[:50] if project_goal else "Web Application"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>"""


def generate_css_file() -> str:
    """Generate CSS file with modern styles."""
    return """/* App Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

#root {
  max-width: 900px;
  margin: 0 auto;
}
"""


def generate_package_json(project_goal: str) -> str:
    """Generate package.json."""
    name = re.sub(r'[^a-z0-9-]', '-', project_goal.lower()[:30]) or "app"
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


def generate_generic_file(llm, file_path: str, project_goal: str, features: list) -> str:
    """Generate any other file type using LLM."""
    prompt = f"""Generate the content for {file_path}.
PROJECT: {project_goal}
FEATURES: {json.dumps(features)}
OUTPUT: Only the file content, no markdown fences."""
    response = llm.invoke(prompt)
    return normalize_code(response.content)


# ============================================
# POST-PROCESSING FUNCTIONS
# ============================================

def fix_backend_code(code: str) -> str:
    """Fix common issues in LLM-generated backend code."""
    lines = code.split('\n')
    
    # Ensure flask_cors import exists
    has_cors_import = any('flask_cors' in line for line in lines)
    has_cors_call = any('CORS(app)' in line for line in lines)
    
    if not has_cors_import:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.startswith('from flask import') or line.startswith('import flask'):
                new_lines.append('from flask_cors import CORS')
        lines = new_lines
    
    if not has_cors_call:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if 'app = Flask(' in line:
                new_lines.append('CORS(app)')
        lines = new_lines
    
    code = '\n'.join(lines)
    
    # Ensure app.run exists at end
    if 'app.run(' not in code:
        code += "\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000, debug=False)"
    
    # Fix common None handling issues
    code = code.replace(
        "request.get_json().get(",
        "(request.get_json() or {}).get("
    )
    
    return code


def fix_app_jsx(code: str) -> str:
    """Fix common issues in LLM-generated App.jsx."""
    # Ensure React import
    if 'import React' not in code:
        code = "import React, { useState, useEffect } from 'react';\n" + code
    
    # Ensure axios import
    if 'import axios' not in code and 'axios' in code:
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import React'):
                lines.insert(i + 1, "import axios from 'axios';")
                break
        code = '\n'.join(lines)
    
    # Ensure export default exists
    if 'export default' not in code:
        code += '\n\nexport default App;'
    
    return code


def extract_routes(code: str) -> list:
    """Extract Flask routes from backend code."""
    routes = []
    
    # Pattern for @app.route('/path', ...)
    pattern = r"@app\.route\(['\"]([^'\"]+)['\"]"
    
    for match in re.finditer(pattern, code):
        route = match.group(1)
        if route not in routes:
            routes.append(route)
    
    return routes
