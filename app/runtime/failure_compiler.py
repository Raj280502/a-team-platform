import re
from pathlib import Path

def compile_failure(project_dir: Path, raw_error: str) -> dict:
    # Handle None or empty error messages
    if not raw_error:
        raw_error = "Unknown error - tests failed but no error message provided"
    
    failing_routes = extract_failing_routes(raw_error)
    
    # Build helpful fix guidance
    fix_guidance = []
    if failing_routes:
        fix_guidance.append("FAILING ROUTES - Fix these in backend/app.py:")
        for method, path in failing_routes:
            fix_guidance.append(f"  - {method} {path}")
            if method == "GET":
                fix_guidance.append(f"    Use: @app.route('{path}', methods=['GET'])")
            elif method == "DELETE":
                fix_guidance.append(f"    Use: @app.route('{path}', methods=['DELETE'])")
            elif method == "PUT":
                fix_guidance.append(f"    Use: @app.route('{path}', methods=['PUT'])")
    
    enhanced_error = raw_error
    if fix_guidance:
        enhanced_error = "\n".join(fix_guidance) + "\n\nOriginal Error:\n" + raw_error
    
    return {
        "raw_error": enhanced_error,
        "failing_files": ["backend/app.py"] if failing_routes else extract_failing_files(raw_error),
        "failing_lines": extract_line_numbers(raw_error),
        "failing_routes": failing_routes,
        "stacktrace": raw_error,
        "fix_policy": "PATCH_ONLY"
    }

def extract_failing_routes(err: str):
    """Extract HTTP method and path from contract test failures."""
    if not err:
        return []
    
    # Pattern: GET /tasks: ... or POST /add: ...
    routes = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s:]+)', err)
    return list(set(routes))

def extract_failing_files(err: str):
    if not err:
        return []
    return list(set(re.findall(r'File "([^"]+)"', err)))

def extract_line_numbers(err: str):
    return re.findall(r'line (\d+)', err)
