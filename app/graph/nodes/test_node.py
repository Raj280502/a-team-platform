from app.runtime.contract_tester import run_contract_tests
from app.runtime.test_runner import run_basic_backend_test, stop_backend_server
from pathlib import Path


def test_node(state):
    project_dir = Path(state["project_dir"])

    # Phase 1: Start backend server
    ok, err = run_basic_backend_test(project_dir)
    if not ok:
        stop_backend_server()
        return {
            "tests_passed": False,
            "error_message": err,
            "contract_report": {"status": "BOOT_FAIL"},
        }

    # Phase 2: Contract enforcement
    try:
        report = run_contract_tests(project_dir)
        
        # Build detailed error message from failed tests
        error_message = None
        if report.get("status") == "DONE":
            failed_tests = [r for r in report.get("results", []) if not r.get("ok")]
            if failed_tests:
                error_lines = ["Contract tests failed:"]
                for test in failed_tests:
                    if "error" in test:
                        error_lines.append(f"  {test['method']} {test['path']}: {test['error']}")
                    else:
                        error_lines.append(f"  {test['method']} {test['path']}: Expected {test['expected']}, got {test['actual']}")
                error_message = "\n".join(error_lines)
        else:
            error_message = f"Contract tests failed: {report.get('status')}"
        
        return {
            "tests_passed": all(r.get("ok") for r in report.get("results", [])),
            "error_message": error_message,
            "contract_report": report,
        }
    finally:
        # Always stop server after tests
        stop_backend_server()
