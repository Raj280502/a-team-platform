from app.core.state import ProjectState


def coder_plan_node(state: ProjectState) -> ProjectState:
    """
    Prepares the coding phase.
    
    Uses the file_plan from architect (dynamic, not hardcoded).
    Initializes containers for route extraction.
    """
    
    # Use file_plan from architect node (already dynamic)
    file_plan = state.get("file_plan", [])
    
    print(f"📋 Coder planning {len(file_plan)} files to generate")
    
    return {
        "file_plan": file_plan,
        # Initialize containers for extraction
        "extracted_routes": [],
        "request_fields": {}
    }
