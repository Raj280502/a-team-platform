"""
contract_tester.py
------------------
Runs contract tests against the generated backend API.
"""

import json
import requests
import time


def run_contract_tests(project_dir):
    """
    Runs contract tests using the schema from contract.json.
    
    Tests each endpoint and validates response status codes.
    """
    
    # Give the server a moment to fully start
    time.sleep(2)

    contract_path = project_dir / "backend" / "contract.json"

    if not contract_path.exists():
        print("   ⚠️ No contract.json found")
        return {"status": "NO_CONTRACT", "results": []}

    try:
        contract = json.loads(contract_path.read_text())
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid contract.json: {e}")
        return {"status": "INVALID_CONTRACT", "results": []}
    
    base_url = contract.get("base_url", "http://localhost:5000")
    endpoints = contract.get("endpoints", [])
    
    if not endpoints:
        print("   ⚠️ No endpoints defined in contract")
        return {"status": "NO_ENDPOINTS", "results": []}

    results = []

    for ep in endpoints:
        method = ep.get("method", "GET").upper()
        path = ep.get("path", "/")
        expected = ep.get("expect", 200)
        body = ep.get("body", {})

        url = base_url + path

        try:
            # Make the appropriate HTTP request
            if method == "GET":
                r = requests.get(url, timeout=10)
            elif method == "POST":
                r = requests.post(url, json=body, timeout=10)
            elif method == "PUT":
                r = requests.put(url, json=body, timeout=10)
            elif method == "DELETE":
                r = requests.delete(url, timeout=10)
            elif method == "PATCH":
                r = requests.patch(url, json=body, timeout=10)
            else:
                results.append({
                    "path": path,
                    "method": method,
                    "error": f"Unsupported method: {method}",
                    "ok": False
                })
                continue

            # Check if response is successful (2xx)
            is_ok = 200 <= r.status_code < 300
            
            results.append({
                "path": path,
                "method": method,
                "expected": expected,
                "actual": r.status_code,
                "ok": is_ok,
                "body_sent": body,
            })

        except requests.Timeout:
            results.append({
                "path": path,
                "method": method,
                "error": "Request timed out",
                "ok": False
            })
        except requests.ConnectionError:
            results.append({
                "path": path,
                "method": method,
                "error": "Connection refused - server may not be running",
                "ok": False
            })
        except Exception as e:
            results.append({
                "path": path,
                "method": method,
                "error": str(e),
                "ok": False
            })

    return {
        "status": "DONE",
        "results": results,
        "total": len(results),
        "passed": len([r for r in results if r.get("ok")]),
        "failed": len([r for r in results if not r.get("ok")]),
    }
