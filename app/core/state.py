"""
state.py
--------
Defines the shared state used across the LangGraph pipeline.
Enhanced for chat-based iterative refinement and streaming.
"""

from typing import Dict, Optional, List, Any
from typing_extensions import TypedDict, Annotated
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
    chat_history: Annotated[List[dict], LastValue]   # Conversation messages for iterative refinement
    is_followup: Annotated[bool, LastValue]           # True if this is a modification to existing project

    # ============================================
    # PROJECT CONFIGURATION
    # ============================================
    project_name: Annotated[str, LastValue]
    project_dir: Annotated[str, LastValue]
    tech_stack: Annotated[str, LastValue]              # react-flask, nextjs, vue-flask, etc.

    # ============================================
    # AGENT OUTPUTS
    # ============================================
    project_scope: Annotated[dict, LastValue]          # Strategist output
    architecture: Annotated[dict, LastValue]           # Architect output
    contract: Annotated[dict, LastValue]               # API contract

    # ============================================
    # SDLC PLANNING STAGES
    # ============================================
    project_overview: Annotated[dict, LastValue]       # Stage 1: Overview
    requirements: Annotated[dict, LastValue]           # Stage 2: Requirements
    user_research: Annotated[dict, LastValue]          # Stage 3: User Research
    task_flows: Annotated[dict, LastValue]             # Stage 4: Task Flows
    user_stories: Annotated[dict, LastValue]           # Stage 5: User Stories

    # ============================================
    # CODE GENERATION
    # ============================================
    file_plan: Annotated[List[str], LastValue]
    files: Annotated[Dict[str, str], LastValue]
    extracted_routes: Annotated[List[str], LastValue]
    request_fields: Annotated[dict, LastValue]
    generation_issues: Annotated[List[dict], LastValue]
    files_to_regenerate: Annotated[List[str], LastValue]
    failed_file_history: Annotated[List[str], LastValue]

    # ============================================
    # STREAMING & PROGRESS
    # ============================================
    current_step: Annotated[str, LastValue]             # Current pipeline step for UI updates
    streaming_content: Annotated[str, LastValue]        # Buffer for streaming code to UI

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