"""
schema.py
---------
Defines the structured output for the Architect agent.
"""

from pydantic import BaseModel, Field
from typing import List


class Service(BaseModel):
    """Represents one runnable service in the system."""
    name: str = Field(..., description="Unique service name (e.g., 'auth-service')")
    framework: str = Field(..., description="Framework/technology stack")
    port: int = Field(..., ge=1024, le=65535, description="Exposed port number")


class ArchitectOutput(BaseModel):
    """
    Structured system architecture produced by the Architect.
    """

    backend: str = Field(..., description="Backend technology stack (e.g., 'FastAPI + PostgreSQL')")
    frontend: str = Field(..., description="Frontend technology stack (e.g., 'Next.js + Tailwind')")
    services: List[Service] = Field(..., min_items=1, max_items=10, description="Microservices breakdown")
    use_docker: bool = Field(..., description="Use Docker Compose for deployment?")
    