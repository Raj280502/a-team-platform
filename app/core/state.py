"""
state.py
--------
Defines the shared state used across the LangGraph.
"""

from typing import Dict, Optional, List, Any
from typing_extensions import TypedDict
from typing_extensions import Annotated
from langgraph.channels import LastValue


class ProjectState(TypedDict, total=False):
    """
    Shared state passed between all nodes in the graph.
    
    This is the "memory" of the AI code factory.
    """
    
    # ============================================
    # USER INPUT
    # ============================================
    user_prompt: Annotated[str, LastValue]
    
    # ============================================
    # PROJECT CONFIGURATION
    # ============================================
    project_name: Annotated[str, LastValue]       # Derived from prompt
    project_dir: Annotated[str, LastValue]        # Full path to project
    
    # ============================================
    # AGENT OUTPUTS
    # ============================================
    project_scope: Annotated[dict, LastValue]     # Strategist output
    architecture: Annotated[dict, LastValue]      # Architect output
    contract: Annotated[dict, LastValue]          # API contract
    
    # ============================================
    # CODE GENERATION
    # ============================================
    file_plan: Annotated[List[str], LastValue]    # Files to generate
    files: Annotated[Dict[str, str], LastValue]   # Generated code
    extracted_routes: Annotated[List[str], LastValue]  # Backend routes
    request_fields: Annotated[dict, LastValue]    # Expected JSON fields per route
    generation_issues: Annotated[List[dict], LastValue]  # Files with truncation issues
    files_to_regenerate: Annotated[List[str], LastValue]  # Specific files to regenerate
    failed_file_history: Annotated[List[str], LastValue]  # Track which files have failed before
    
    # ============================================
    # TESTING & REPAIR
    # ============================================
    tests_passed: Annotated[bool, LastValue]
    error_message: Annotated[Optional[str], LastValue]
    contract_report: Annotated[dict, LastValue]
    repair_attempts: Annotated[int, LastValue]
    
    # ============================================
    # PREVIEW
    # ============================================
    preview_started: Annotated[bool, LastValue]
    preview_url: Annotated[str, LastValue] 