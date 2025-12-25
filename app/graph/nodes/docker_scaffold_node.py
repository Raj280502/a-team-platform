from pathlib import Path
from app.core.state import ProjectState

def docker_scaffold_node(state: ProjectState) -> ProjectState:
    root = Path("workspace/generated_projects/todo_app")

    docker = root / "docker"
    docker.mkdir(parents=True, exist_ok=True)

    # Backend Dockerfile
    (docker / "backend.Dockerfile").write_text(
        """FROM python:3.10-slim
WORKDIR /app
COPY backend /app/backend
RUN pip install flask
CMD ["python", "/app/backend/app.py"]
"""
    )

    # Frontend Dockerfile
    (docker / "frontend.Dockerfile").write_text(
        """FROM node:20-alpine
WORKDIR /app
COPY frontend /app/frontend
RUN npm install -g serve
CMD ["serve", "-s", "/app/frontend", "-l", "3000"]
"""
    )

    # docker-compose.yml
    (docker / "docker-compose.yml").write_text(
        """services:
  backend:
    build:
      context: ..
      dockerfile: docker/backend.Dockerfile
    ports:
      - "5000:5000"

  frontend:
    build:
      context: ..
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:3000"
"""
    )

    return state
