from app.core.llm import get_llm
from app.core.state import ProjectState
from app.utils.file_ops import normalize_code

def coder_file_node(state: ProjectState) -> ProjectState:
    llm = get_llm(role="coder")
    generated = {}

    for file_path in state["file_plan"]:

        if file_path == "backend/app.py":
            prompt = f"""
You are generating backend/app.py.

Generate a SINGLE FILE Flask backend.

MANDATORY:
- Use Flask
- Define app = Flask(__name__)
- In-memory task list
- Routes:
    GET /api/health
    GET /api/tasks
    POST /api/tasks
    DELETE /api/tasks/<id>
- Run on host 0.0.0.0 and port 5000
- Output ONLY raw Python source code
"""

        elif file_path == "frontend/src/App.js":
            prompt = f"""
You are generating frontend/src/App.js.

Generate a minimal React functional component.

MANDATORY:
- export default App
- Simple welcome UI
- No backend calls yet
- Output ONLY raw JavaScript source code
"""

        else:
            continue

        raw = llm.invoke(prompt).content
        generated[file_path] = normalize_code(raw)
    state["files"] = generated
    return state
