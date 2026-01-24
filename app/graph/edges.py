def should_repair(state):
    """
    Central nervous reflex of the factory.
    Decides: heal, deploy, or halt.
    """

    # Hard safety governor — prevents infinite mutation
    if state.get("repair_attempts", 0) >= 3:
        print("⚠️ MAX REPAIR ATTEMPTS REACHED — HALTING PROJECT")
        return "end"

    # Check if tests passed
    if not state.get("tests_passed", False):
        print(f"[DEBUG] Tests failed, attempting repair (attempt {state.get('repair_attempts', 0) + 1}/3)")
        return "repair"

    # Tests passed - proceed to docker
    print("[DEBUG] Tests passed, proceeding to deployment")
    return "docker"
