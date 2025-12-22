"""
state.py
--------
Defines the shared state used across the LangGraph.
"""

from typing import Dict, Optional
from typing_extensions import TypedDict


class ProjectState(TypedDict):
    # User input
    user_prompt: str

    # Agent outputs
    project_scope: Optional[dict]
    architecture: Optional[dict]

    # Code artifacts
    files: Dict[str, str]

    # Test results
    tests_passed: Optional[bool]
    error_message: Optional[str]

    repair_attempts: int 