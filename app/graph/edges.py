def should_repair(state):
    """
    Central nervous reflex of the factory.
    Decides: heal, preview, or halt.
    
    Enhanced to also check for generation_issues (truncated code).
    """

    # Hard safety governor — prevents infinite mutation
    max_attempts = 3
    current_attempts = state.get("repair_attempts", 0)
    
    if current_attempts >= max_attempts:
        print(f"⚠️ MAX REPAIR ATTEMPTS ({max_attempts}) REACHED — PROCEEDING TO PREVIEW")
        return "preview"

    # Check for generation issues (truncated code)
    generation_issues = state.get("generation_issues", [])
    if generation_issues:
        print(f"🔧 Found {len(generation_issues)} truncated files, attempting repair")
        return "repair"

    # Check if tests passed
    if not state.get("tests_passed", False):
        print(f"🔧 Tests failed, attempting repair (attempt {current_attempts + 1}/{max_attempts})")
        return "repair"

    # Tests passed - proceed to preview
    print("✅ Tests passed! Proceeding to preview...")
    return "preview"


def should_deploy(state):
    """
    After preview, decide whether to end.
    Future: Could add Docker deployment option.
    """
    # For now, always end after preview
    # Future enhancement: Ask user if they want Docker deployment
    return "end"
