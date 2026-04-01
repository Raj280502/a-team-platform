"""
schema.py - Strategist agent output schema.
Enhanced with UI/UX requirements and page structure.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class FeatureSpec(BaseModel):
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="What the user can do")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Criteria for completion")
    priority: str = Field(..., description="'must-have' or 'should-have'")


class PageSpec(BaseModel):
    """Specification for a single page/view in the application."""
    name: str = Field(..., description="Page name (e.g., 'Dashboard', 'Settings')")
    route: str = Field(..., description="Route path (e.g., '/', '/settings')")
    description: str = Field(..., description="What this page shows/does")
    components: List[str] = Field(default_factory=list, description="Key UI components on this page")
    states: List[str] = Field(default_factory=list, description="UI states like 'empty', 'loading'")


class ModelField(BaseModel):
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Data type")
    required: bool = Field(..., description="Is the field required")
    description: str = Field(..., description="Field description")


class DataModelSpec(BaseModel):
    name: str = Field(..., description="Model name")
    fields: List[ModelField] = Field(default_factory=list, description="Model fields")


class ApiEndpointSpec(BaseModel):
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Endpoint path")
    purpose: str = Field(..., description="What the endpoint does")
    request_body: Optional[Dict[str, Any]] = Field(None, description="Request body example")
    response_body: Optional[Dict[str, Any]] = Field(None, description="Response body example")


class UiStyleSpec(BaseModel):
    theme: str = Field(..., description="Theme (light/dark/system)")
    tone: str = Field(..., description="Visual tone")
    color_notes: str = Field(..., description="Color palette notes")


class StrategistOutput(BaseModel):
    """Structured output produced by the Strategist agent."""

    project_goal: str = Field(..., description="Clear one-sentence description of what the app does")
    target_users: List[str] = Field(..., description="Primary user personas")
    core_features: List[FeatureSpec] = Field(..., description="List of specific features")
    pages: List[PageSpec] = Field(default_factory=list, description="Pages/views in the application")
    data_models: List[DataModelSpec] = Field(default_factory=list, description="Key data entities")
    api_endpoints: List[ApiEndpointSpec] = Field(default_factory=list, description="Required API endpoints")
    ui_style: UiStyleSpec = Field(..., description="UI style/theme description")
    technical_constraints: List[str] = Field(default_factory=list, description="Hard technical constraints or limitations")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by the AI")