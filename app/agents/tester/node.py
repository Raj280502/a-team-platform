"""
node.py
-------
Defines the Tester agent.

This agent:
- Receives test results
- Converts them into structured output
"""

from app.agents.tester.schema import TesterOutput


def tester_node(test_result: tuple[bool, str | None]) -> TesterOutput:
    """
    Tester agent node.

    Args:
        test_result: Tuple of (passed, error_message)

    Returns:
        TesterOutput
    """

    passed, error = test_result

    return TesterOutput(
        tests_passed=passed,
        error_message=error
    )
