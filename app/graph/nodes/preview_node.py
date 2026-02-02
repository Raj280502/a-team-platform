"""
preview_node.py
---------------
Starts the generated application using Docker for reliable preview.
"""

import subprocess
import time
import webbrowser
from pathlib import Path
import os


def preview_node(state):
    """
    Start the generated application using Docker Compose.
    
    This ensures:
    - Consistent environment across all machines
    - Both frontend and backend run reliably
    - Easy cleanup when done
    """
    project_dir = Path(state["project_dir"])
    
    print("\n" + "=" * 60)
    print("🐳 STARTING DOCKER PREVIEW")
    print("=" * 60)
    
    # ============================================
    # Generate Docker files if not exist
    # ============================================
    if not _ensure_docker_files(project_dir):
        print("❌ Failed to create Docker files")
        return {"preview_started": False, "preview_url": None}
    
    # ============================================
    # Build and start containers
    # ============================================
    print("\n📦 Building Docker containers...")
    
    try:
        # Stop any existing containers first
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=project_dir,
            capture_output=True,
            timeout=30,
        )
        
        # Build containers
        build_result = subprocess.run(
            ["docker", "compose", "build", "--no-cache"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for build
        )
        
        if build_result.returncode != 0:
            print(f"❌ Docker build failed:\n{build_result.stderr[:500]}")
            # Fallback to non-docker preview
            return _fallback_preview(project_dir)
        
        print("✅ Docker build successful")
        
        # Start containers in detached mode
        print("\n🚀 Starting containers...")
        up_result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if up_result.returncode != 0:
            print(f"❌ Docker start failed:\n{up_result.stderr[:500]}")
            return _fallback_preview(project_dir)
        
        print("✅ Containers started")
        
        # Wait for services to be ready
        print("\n⏳ Waiting for services to start...")
        time.sleep(5)
        
        # ============================================
        # Open Browser
        # ============================================
        frontend_url = "http://localhost:3000"
        backend_url = "http://localhost:5000"
        
        print(f"\n🌐 Opening browser at {frontend_url}")
        webbrowser.open(frontend_url)
        
        # ============================================
        # Show status
        # ============================================
        print("\n" + "=" * 60)
        print("🎉 APPLICATION IS RUNNING IN DOCKER!")
        print("=" * 60)
        print(f"\n   Frontend:  {frontend_url}")
        print(f"   Backend:   {backend_url}")
        print(f"   Project:   {project_dir}")
        print("\n   To stop:   docker compose down")
        print("   To logs:   docker compose logs -f")
        print("=" * 60)
        
        return {
            "preview_started": True,
            "preview_url": frontend_url,
            "docker_running": True,
        }
        
    except subprocess.TimeoutExpired:
        print("❌ Docker operation timed out")
        return _fallback_preview(project_dir)
    except FileNotFoundError:
        print("❌ Docker not found - is Docker Desktop running?")
        return _fallback_preview(project_dir)
    except Exception as e:
        print(f"❌ Docker error: {e}")
        return _fallback_preview(project_dir)


def _ensure_docker_files(project_dir: Path) -> bool:
    """Create Docker files if they don't exist."""
    
    backend_dockerfile = project_dir / "backend" / "Dockerfile"
    frontend_dockerfile = project_dir / "frontend" / "Dockerfile"
    compose_file = project_dir / "docker-compose.yml"
    
    try:
        # Backend Dockerfile
        if not backend_dockerfile.exists():
            backend_dockerfile.parent.mkdir(parents=True, exist_ok=True)
            backend_dockerfile.write_text("""FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask flask-cors

# Copy application
COPY app.py .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
""")
            print("   ✅ Created backend Dockerfile")
        
        # Frontend Dockerfile (multi-stage build)
        if not frontend_dockerfile.exists():
            frontend_dockerfile.parent.mkdir(parents=True, exist_ok=True)
            frontend_dockerfile.write_text("""FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:5000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
""")
            print("   ✅ Created frontend Dockerfile")
        
        # Docker Compose file
        if not compose_file.exists():
            compose_file.write_text("""version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
""")
            print("   ✅ Created docker-compose.yml")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create Docker files: {e}")
        return False


def _fallback_preview(project_dir: Path):
    """Fallback to direct execution if Docker fails."""
    import sys
    
    print("\n⚠️ Falling back to direct execution (no Docker)...")
    
    backend_dir = project_dir / "backend"
    
    try:
        # Start Flask directly
        print("📦 Starting Flask backend on http://localhost:5000 ...")
        
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
        )
        
        time.sleep(2)
        
        if backend_process.poll() is not None:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed: {stderr.decode()[:200]}")
            return {"preview_started": False, "preview_url": None}
        
        print("✅ Backend running on http://localhost:5000")
        
        # Open backend URL
        webbrowser.open("http://localhost:5000")
        
        print("\n" + "=" * 60)
        print("🎉 BACKEND IS RUNNING!")
        print("=" * 60)
        print("\n   Backend API: http://localhost:5000")
        print("\n   For frontend, run manually:")
        print(f"   cd {project_dir / 'frontend'}")
        print("   npm install && npm run dev")
        print("=" * 60)
        
        return {
            "preview_started": True,
            "preview_url": "http://localhost:5000",
            "docker_running": False,
        }
        
    except Exception as e:
        print(f"❌ Fallback preview failed: {e}")
        return {"preview_started": False, "preview_url": None}
