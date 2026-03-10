"""
schema.py - Architect agent output schema.
Supports multiple tech stacks and component hierarchy.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ComponentSpec(BaseModel):
    """A UI component specification."""
    name: str = Field(..., description="Component name (e.g., 'TaskList', 'AddForm')")
    file_path: str = Field(..., description="Relative file path (e.g., 'frontend/src/components/TaskList.jsx')")
    description: str = Field(..., description="What this component does")


class APIRoute(BaseModel):
    """An API route specification."""
    method: str = Field(..., description="HTTP method (GET, POST, PUT, DELETE)")
    path: str = Field(..., description="Route path (e.g., '/api/tasks')")
    description: str = Field(..., description="What this endpoint does")
    request_body: Optional[List[str]] = Field(default=None, description="Expected request body fields")
    response_type: str = Field(default="json", description="Response type (json, text, file)")


class ArchitectOutput(BaseModel):
    """Structured system architecture produced by the Architect."""

    backend: str = Field(..., description="Backend framework (e.g., 'Flask', 'Express')")
    frontend: str = Field(..., description="Frontend framework (e.g., 'React', 'Vue')")
    backend_file: str = Field(default="backend/app.py", description="Main backend file path")
    api_routes: List[APIRoute] = Field(default_factory=list, description="All API routes")
    components: List[ComponentSpec] = Field(default_factory=list, description="Frontend components")
    styling: str = Field(default="inline CSS", description="Styling approach")
    state_management: str = Field(default="useState", description="State management approach")