"""
edges.py - Conditional edge logic for the LangGraph.
"""

from app.core.state import ProjectState

MAX_REPAIR_ATTEMPTS = 3


def should_repair(state: ProjectState) -> str:
    """
    Decides next step after testing:
    - 'repair' → Tests failed, retry if under limit
    - 'preview' → Tests passed, show the app
    - 'end' → Tests failed but max retries reached
    """
    tests_passed = state.get("tests_passed", False)
    repair_attempts = state.get("repair_attempts", 0)

    if tests_passed:
        print("   ✅ Tests passed → Preview")
        return "preview"

    if repair_attempts >= MAX_REPAIR_ATTEMPTS:
        print(f"   ⚠️ Max repair attempts ({MAX_REPAIR_ATTEMPTS}) reached → Preview anyway")
        return "preview"  # Show preview even with issues

    print(f"   🔧 Tests failed → Repair (attempt {repair_attempts + 1}/{MAX_REPAIR_ATTEMPTS})")
    return "repair"


def should_deploy(state: ProjectState) -> str:
    """After preview, go to end."""
    return "end"
