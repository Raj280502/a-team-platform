"""
schema.py
---------
Defines the structured output schema for the Strategist agent.

Why this file exists:
- Prevents hallucinated responses
- Enforces consistency
- Makes downstream automation possible
"""

from pydantic import BaseModel
from typing import List, Optional
from pydantic import Field


class StrategistOutput(BaseModel):
    """
    Structured output produced by the Strategist agent.
    """

    project_goal: str = Field(..., description="High-level project objective")
    target_users: str = Field(..., description="Primary user personas")
    core_features: List[str] = Field(..., description="Key MVP features")
    technical_constraints: List[str] = Field(..., description="Hard tech limits")
    