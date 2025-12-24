"""
state.py
--------
Defines the shared state used across the LangGraph.
"""

from typing import Dict, Optional, List
from typing_extensions import TypedDict


class ProjectState(TypedDict):
    user_prompt: str
    project_scope: dict
    architecture: dict
    file_plan: List[str]
    files: Dict[str, str]
    tests_passed: bool
    error_message: Optional[str]