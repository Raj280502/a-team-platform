"""
schema.py - Strategist agent output schema.
Enhanced with UI/UX requirements and page structure.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PageSpec(BaseModel):
    """Specification for a single page/view in the application."""
    name: str = Field(..., description="Page name (e.g., 'Dashboard', 'Settings')")
    route: str = Field(..., description="Route path (e.g., '/', '/settings')")
    description: str = Field(..., description="What this page shows/does")
    components: List[str] = Field(default_factory=list, description="Key UI components on this page")


class StrategistOutput(BaseModel):
    """Structured output produced by the Strategist agent."""

    project_goal: str = Field(..., description="Clear one-sentence description of what the app does")
    target_users: str = Field(..., description="Primary user persona")
    core_features: List[str] = Field(..., description="List of 4-8 specific features the app must have")
    pages: List[PageSpec] = Field(default_factory=list, description="Pages/views in the application")
    data_models: List[str] = Field(default_factory=list, description="Key data entities (e.g., 'Task', 'User', 'Recipe')")
    api_endpoints: List[str] = Field(default_factory=list, description="Required API endpoints (e.g., 'GET /tasks', 'POST /tasks')")
    ui_style: str = Field(default="modern minimal", description="UI style/theme description (e.g., 'dark modern', 'colorful playful')")
    technical_constraints: List[str] = Field(default_factory=list, description="Hard technical constraints or limitations")