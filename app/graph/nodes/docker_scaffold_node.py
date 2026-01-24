# from pathlib import Path
# import re
# from app.core.state import ProjectState

# # Map import names to pip package names (common mismatches)
# IMPORT_TO_PACKAGE = {
#     "flask": "flask",
#     "flask_cors": "flask-cors",
#     "flask_sqlalchemy": "flask-sqlalchemy",
#     "flask_login": "flask-login",
#     "flask_wtf": "flask-wtf",
#     "sqlalchemy": "sqlalchemy",
#     "requests": "requests",
#     "numpy": "numpy",
#     "pandas": "pandas",
#     "PIL": "pillow",
#     "cv2": "opencv-python",
#     "sklearn": "scikit-learn",
#     "dotenv": "python-dotenv",
#     "jwt": "pyjwt",
#     "bcrypt": "bcrypt",
#     "pymongo": "pymongo",
#     "redis": "redis",
#     "celery": "celery",
#     "marshmallow": "marshmallow",
#     "pydantic": "pydantic",
#     "fastapi": "fastapi",
#     "uvicorn": "uvicorn",
# }

# # Standard library modules to ignore
# STDLIB_MODULES = {
#     "os", "sys", "re", "json", "math", "random", "datetime", "time", "collections",
#     "itertools", "functools", "typing", "pathlib", "logging", "unittest", "io",
#     "subprocess", "threading", "multiprocessing", "socket", "http", "urllib",
#     "email", "html", "xml", "sqlite3", "csv", "hashlib", "secrets", "uuid",
#     "copy", "pickle", "shelve", "dbm", "gzip", "zipfile", "tarfile", "tempfile",
#     "shutil", "glob", "fnmatch", "linecache", "struct", "codecs", "unicodedata",
#     "stringprep", "textwrap", "difflib", "enum", "graphlib", "dataclasses",
#     "contextlib", "abc", "atexit", "traceback", "gc", "inspect", "dis", "warnings",
#     "weakref", "types", "operator", "numbers", "decimal", "fractions", "statistics",
#     "cmath", "array", "bisect", "heapq", "queue", "asyncio", "concurrent", "sched",
#     "signal", "mmap", "ctypes", "select", "selectors", "contextvars", "base64",
#     "binascii", "quopri", "uu", "calendar", "locale", "gettext", "argparse",
#     "getopt", "configparser", "fileinput", "stat", "filecmp", "netrc", "xdrlib",
#     "plistlib", "platform", "errno", "curses", "readline", "rlcompleter",
# }

# def extract_imports(code: str) -> set:
#     """Extract imported module names from Python code."""
#     imports = set()
    
#     # Match 'import x' or 'import x as y'
#     for match in re.finditer(r'^import\s+([\w\.]+)', code, re.MULTILINE):
#         module = match.group(1).split('.')[0]
#         imports.add(module)
    
#     # Match 'from x import y' or 'from x.y import z'
#     for match in re.finditer(r'^from\s+([\w\.]+)\s+import', code, re.MULTILINE):
#         module = match.group(1).split('.')[0]
#         imports.add(module)
    
#     return imports

# def get_pip_packages(code: str) -> list:
#     """Get list of pip packages needed for the code."""
#     imports = extract_imports(code)
#     packages = set()
    
#     for imp in imports:
#         # Skip standard library modules
#         if imp in STDLIB_MODULES:
#             continue
#         # Map to pip package name or use import name
#         pkg = IMPORT_TO_PACKAGE.get(imp, imp)
#         packages.add(pkg)
    
#     # Always include flask as base
#     packages.add("flask")
    
#     return sorted(packages)

# def docker_scaffold_node(state: ProjectState) -> ProjectState:
#     root = Path("app/workspace/generated_projects/todo_app")

#     docker = root / "docker"
#     docker.mkdir(parents=True, exist_ok=True)

#     # Get generated backend code and extract required packages
#     files = state.get("files", {})
#     backend_code = files.get("backend/app.py", "")
#     pip_packages = get_pip_packages(backend_code)
#     pip_install_cmd = " ".join(pip_packages)
    
#     print(f"[docker_scaffold] Detected packages: {pip_packages}")

#     # Backend Dockerfile with dynamically detected packages
#     (docker / "backend.Dockerfile").write_text(
#         f"""FROM python:3.10-slim
# WORKDIR /app
# COPY backend /app/backend
# RUN pip install {pip_install_cmd}
# EXPOSE 5000
# CMD ["python", "/app/backend/app.py"]
# """
#     )

#     # Frontend Dockerfile  
#     (docker / "frontend.Dockerfile").write_text(
#         """FROM node:20-alpine
# WORKDIR /app
# COPY frontend/package.json /app/
# RUN npm install
# COPY frontend /app/
# EXPOSE 5173
# CMD ["npm", "run", "dev", "--", "--host"]
# """
#     )

#     # docker-compose.yml
#     (docker / "docker-compose.yml").write_text(
#         """services:
#   backend:
#     build:
#       context: ..
#       dockerfile: docker/backend.Dockerfile
#     ports:
#       - "5000:5000"

#   frontend:
#     build:
#       context: ..
#       dockerfile: docker/frontend.Dockerfile
#     ports:
#       - "5173:5173"
# """
#     )

#     return {}


from pathlib import Path
from app.core.state import ProjectState


def docker_scaffold_node(state: ProjectState) -> ProjectState:
    root = Path("app/workspace/generated_projects/todo_app")

    # ---------- Backend Dockerfile ----------
    (root / "backend" / "Dockerfile").write_text("""
FROM python:3.10-slim

WORKDIR /app
COPY app.py .

RUN pip install flask flask-cors

EXPOSE 5000

CMD ["python", "app.py"]
""")

    # ---------- Frontend Dockerfile ----------
    (root / "frontend" / "Dockerfile").write_text("""
FROM node:20 AS build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
""")

    # ---------- docker-compose.yml ----------
    (root / "docker-compose.yml").write_text("""
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
""")

    print("✅ Correct Docker files scaffolded")
    return {}
