"""
state.py
--------
Defines the shared state used across the LangGraph.
"""

from typing import Dict, Optional, List
from typing_extensions import TypedDict
from typing_extensions import Annotated
from langgraph.channels import LastValue

class ProjectState(TypedDict,total=False):
    user_prompt: Annotated[str, LastValue]
    project_scope: Annotated[dict, LastValue]
    architecture: Annotated[dict, LastValue]
    file_plan: Annotated[List[str], LastValue]
    files: Annotated[Dict[str, str], LastValue]
    tests_passed: Annotated[bool, LastValue]
    error_message: Annotated[Optional[str], LastValue]
    repair_attempts: Annotated[int, LastValue] 
    
    
    # # User input
    # user_prompt: str

    # # Agent outputs
    # project_scope: Optional[dict]
    # architecture: Optional[dict]
    
    # planned_files: List[str]


    # # Code artifacts
    # files: Dict[str, str]

    # # Test results
    # tests_passed: Optional[bool]
    # error_message: Optional[str]

    # repair_attempts: int 