"""
repair_node.py
--------------
Self-healing node that fixes broken code based on test failures.
Handles truncated code detection and completion.
"""

from pathlib import Path
from app.agents.coder.node import build_repair_node
from app.runtime.failure_compiler import compile_failure
from app.utils.file_ops import normalize_code
from app.utils.code_validator import validate_file, is_code_truncated


def repair_node(state):
    """
    Repair node that fixes broken backend code.
    
    Detects truncated code and asks LLM to complete it.
    Handles both backend (Python) and frontend (JSX) files.
    """
    project_dir = Path(state["project_dir"])
    current_attempt = state.get("repair_attempts", 0) + 1
    print(f"\n🔧 REPAIR ATTEMPT {current_attempt}/3")
    print("=" * 50)

    error_message = state.get("error_message", "Unknown error")
    generation_issues = state.get("generation_issues", [])

    # Determine which files need repair (deduplicated)
    files_to_repair = []
    seen = set()

    # Add files with generation issues (truncation)
    for issue in generation_issues:
        path = issue.get("file")
        if not path or path in seen:
            continue
        seen.add(path)
        files_to_repair.append({
            "path": path,
            "reason": f"truncated: {issue.get('issues')}"
        })

    # Add backend if error message mentions it
    backend_file = project_dir / "backend" / "app.py"
    if backend_file.exists():
        if "backend" in error_message.lower() or "flask" in error_message.lower() or not files_to_repair:
            if "backend/app.py" not in seen:
                seen.add("backend/app.py")
                files_to_repair.append({
                    "path": "backend/app.py",
                    "reason": f"error: {error_message[:200]}"
                })

    # Check App.jsx for truncation
    app_jsx = project_dir / "frontend" / "src" / "App.jsx"
    app_key = "frontend/src/App.jsx"
    if app_jsx.exists() and app_key not in seen:
        content = app_jsx.read_text(encoding="utf-8")
        is_valid, issues = validate_file(content, "App.jsx")
        if not is_valid:
            seen.add(app_key)
            files_to_repair.append({
                "path": app_key,
                "reason": f"truncated: {issues}"
            })

    if not files_to_repair:
        print("❌ No files identified for repair")
        return {
            "repair_attempts": current_attempt,
            "current_step": "repair_complete",
        }

    print(f"📋 Files to repair: {[f['path'] for f in files_to_repair]}")

    current_files = state.get("files", {})
    repairer = build_repair_node()
    still_bad = []
    new_generation_issues = []

    for file_info in files_to_repair:
        file_path = file_info["path"]
        reason = file_info["reason"]

        full_path = project_dir / file_path
        if not full_path.exists():
            print(f"   ⚠️ {file_path} not found, skipping")
            continue

        print(f"\n   🔧 Repairing: {file_path}")
        print(f"      Reason: {reason[:100]}")

        broken_code = full_path.read_text(encoding="utf-8")

        # Create specialized repair prompt
        if "truncated" in reason.lower():
            failure_report = f"""
FILE: {file_path}
ISSUE: The code is INCOMPLETE/TRUNCATED
SYMPTOMS: {reason}

CURRENT CODE (truncated):
```
{broken_code}
```

TASK: Generate the COMPLETE, WORKING version of this file.
- If Python: ensure it has all imports and ends with app.run()
- If JSX: ensure it has all imports and ends with 'export default'
- Do NOT just add a few lines - regenerate the entire complete file
"""
        else:
            failure_report = compile_failure(project_dir, error_message)

        try:
            fixed_response = repairer.invoke({
                "broken_file": broken_code,
                "failure_report": failure_report,
            })

            fixed_code = normalize_code(fixed_response.content)

            # Validate the fix
            is_valid, issues = validate_file(fixed_code, file_path)

            if len(fixed_code) < 100:
                print(f"      ⚠️ LLM returned suspiciously short code, keeping original")
                new_generation_issues.append({"file": file_path, "issues": ["too_short"]})
                still_bad.append(file_path)
                continue

            if not is_valid:
                print(f"      ⚠️ Fixed code still has issues: {issues[:2]}")
                new_generation_issues.append({"file": file_path, "issues": issues})
                still_bad.append(file_path)
            else:
                print(f"      ✅ Code validated successfully")

            # Write fixed code to disk
            full_path.write_text(fixed_code, encoding="utf-8")
            print(f"      ✅ Fixed code written to disk")

            # Update state["files"] to stay in sync
            current_files[file_path] = fixed_code

        except Exception as e:
            print(f"      ❌ Repair failed: {e}")

    # If after max attempts some files remain bad, write safe fallbacks
    max_attempts = 3
    if still_bad and current_attempt >= max_attempts:
        for bad in set(still_bad):
            try:
                full_path = project_dir / bad
                if bad.endswith("App.jsx"):
                    fallback = """import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
    const [status, setStatus] = useState('Loading...');

    useEffect(() => {
        fetch('http://localhost:5000/api/health')
            .then(r => r.json())
            .then(data => setStatus('Connected: ' + data.status))
            .catch(() => setStatus('Cannot connect to backend'));
    }, []);

    return (
        <div className="app">
            <div className="app-header">
                <h1>Application</h1>
                <p>{status}</p>
            </div>
            <div className="form-card">
                <p>Your app is running! The backend connection status is shown above.</p>
            </div>
        </div>
    );
}

export default App;"""
                    full_path.write_text(fallback, encoding="utf-8")
                    current_files[bad] = fallback
                    new_generation_issues = [gi for gi in new_generation_issues if gi.get("file") != bad]
            except Exception:
                pass

        still_bad = []

    return {
        "repair_attempts": current_attempt,
        "files": current_files,
        "error_message": None,
        "generation_issues": new_generation_issues,
        "files_to_regenerate": still_bad,
        "current_step": "repair_complete",
    }
