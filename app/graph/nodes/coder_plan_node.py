"""
coder_plan_node.py
------------------
Prepares for code generation phase.
Sets up the file plan and initializes containers.
"""

from app.core.state import ProjectState


def coder_plan_node(state: ProjectState) -> ProjectState:
    """
    Prepares the coder phase.
    The file_plan is already built by architect_node.
    This node initializes the generation containers.
    """
    file_plan = state.get("file_plan", [])
    print(f"\n📋 CODER PLAN: {len(file_plan)} files queued for generation")

    for i, f in enumerate(file_plan, 1):
        print(f"   {i}. {f}")

    return {
        "files": state.get("files", {}),
        "extracted_routes": [],
        "request_fields": {},
        "generation_issues": [],
        "files_to_regenerate": [],
        "failed_file_history": state.get("failed_file_history", []),
        "current_step": "coder_plan_ready",
    }
