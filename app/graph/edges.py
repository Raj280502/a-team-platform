def should_repair(state) -> str:
    """
    Decide whether to attempt repair or stop.
    """

    # Stop if tests passed
    if state["tests_passed"]:
        return "end"

    # Stop after 1 repair attempt (MVP rule)
    if state["repair_attempts"] >= 1:
        return "end"

    return "repair"

def should_continue(state):
    if not state["tests_passed"]:
        return "repair"

    return "docker"
