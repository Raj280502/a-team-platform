"""
test_node.py
------------
Tests the generated application by running the backend
and executing contract tests.
"""

from app.runtime.contract_tester import run_contract_tests
from app.runtime.test_runner import run_basic_backend_test, stop_backend_server
from pathlib import Path


def test_node(state):
    """
    Test node - validates the generated code.
    
    1. Starts the Flask backend
    2. Runs contract tests against all endpoints
    3. Reports results
    """
    project_dir = Path(state["project_dir"])
    
    print("\n🧪 TESTING: Validating generated code...")
    print("=" * 50)

    # Phase 1: Start backend server
    print("   📡 Starting backend server...")
    ok, err = run_basic_backend_test(project_dir)
    
    if not ok:
        print(f"   ❌ Backend failed to start: {err[:100] if err else 'Unknown error'}...")
        stop_backend_server()
        return {
            "tests_passed": False,
            "error_message": err or "Backend failed to start",
            "contract_report": {"status": "BOOT_FAIL"},
        }
    
    print("   ✅ Backend started successfully")

    # Phase 2: Contract enforcement
    try:
        print("   📋 Running contract tests...")
        report = run_contract_tests(project_dir)
        
        results = report.get("results", [])
        passed = [r for r in results if r.get("ok")]
        failed = [r for r in results if not r.get("ok")]
        
        print(f"\n   Results: {len(passed)} passed, {len(failed)} failed")
        
        # Build detailed error message from failed tests
        error_message = None
        if failed:
            error_lines = ["Contract tests failed:"]
            for test in failed:
                if "error" in test:
                    error_lines.append(f"   {test['method']} {test['path']}: {test['error']}")
                else:
                    error_lines.append(f"   {test['method']} {test['path']}: Expected {test.get('expected')}, got {test.get('actual')}")
            error_message = "\n".join(error_lines)
            print(f"\n   ❌ Failed tests:")
            for line in error_lines[1:]:
                print(f"      {line}")
        else:
            print("   ✅ All contract tests passed!")
        
        return {
            "tests_passed": len(failed) == 0,
            "error_message": error_message,
            "contract_report": report,
        }
        
    except Exception as e:
        print(f"   ❌ Test execution error: {e}")
        return {
            "tests_passed": False,
            "error_message": f"Test execution error: {str(e)}",
            "contract_report": {"status": "ERROR", "error": str(e)},
        }
    finally:
        # Always stop server after tests
        stop_backend_server()
        print("   📡 Backend server stopped")
