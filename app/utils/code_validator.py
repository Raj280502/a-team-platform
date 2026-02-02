"""
code_validator.py
-----------------
Validates generated code for completeness and correctness.

Detects:
- Truncated Python files
- Truncated JSX/JavaScript files
- Missing required patterns
- Syntax errors
"""

import ast
import re
from typing import Tuple, List


def validate_python_code(code: str, filename: str = "app.py") -> Tuple[bool, List[str]]:
    """
    Validate Python code for completeness and syntax.
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not code or len(code.strip()) < 50:
        issues.append("Code is empty or too short")
        return False, issues
    
    # Check for syntax errors
    try:
        ast.parse(code)
    except SyntaxError as e:
        issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return False, issues
    
    # Check for truncation indicators
    truncation_signs = [
        (r'\.\.\.$', "Code ends with '...' - likely truncated"),
        (r'#\s*\.\.\.', "Code contains '# ...' - likely truncated"),
        (r'"""$', "Code ends with unclosed docstring"),
        (r"'''$", "Code ends with unclosed docstring"),
        (r'def\s+\w+\([^)]*$', "Function definition is incomplete"),
        (r'class\s+\w+[^:]*$', "Class definition is incomplete"),
        (r'if\s+[^:]+$', "If statement is incomplete"),
        (r':\s*$', "Code ends with colon but no body"),
    ]
    
    lines = code.strip().split('\n')
    last_line = lines[-1] if lines else ""
    
    for pattern, message in truncation_signs:
        if re.search(pattern, last_line):
            issues.append(message)
    
    # For Flask apps, check required patterns
    if "flask" in filename.lower() or "app.py" in filename.lower():
        required_patterns = [
            (r'from flask import', "Missing Flask import"),
            (r'app\s*=\s*Flask\s*\(', "Missing Flask app initialization"),
            (r'@app\.route', "No routes defined"),
            (r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', "Missing if __name__ == '__main__'"),
            (r'app\.run\s*\(', "Missing app.run()"),
        ]
        
        for pattern, message in required_patterns:
            if not re.search(pattern, code):
                issues.append(message)
    
    # Check for unbalanced brackets/parens
    brackets = {'(': ')', '[': ']', '{': '}'}
    stack = []
    in_string = False
    string_char = None
    
    for i, char in enumerate(code):
        if char in '"\'':
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
        elif not in_string:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    issues.append(f"Unbalanced closing bracket '{char}'")
                else:
                    expected = brackets[stack.pop()]
                    if char != expected:
                        issues.append(f"Mismatched brackets: expected '{expected}', got '{char}'")
    
    if stack:
        issues.append(f"Unclosed brackets: {stack}")
    
    return len(issues) == 0, issues


def validate_jsx_code(code: str, filename: str = "App.jsx") -> Tuple[bool, List[str]]:
    """
    Validate JSX/React code for completeness.
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not code or len(code.strip()) < 50:
        issues.append("Code is empty or too short")
        return False, issues
    
    # Check for truncation
    lines = code.strip().split('\n')
    last_line = lines[-1].strip() if lines else ""
    
    truncation_signs = [
        (r'<\w+$', "JSX tag is incomplete"),
        (r'<\w+\s+\w+=$', "JSX attribute is incomplete"),
        (r'{\s*$', "Unclosed JSX expression"),
        (r'=>\s*$', "Arrow function body is missing"),
        (r'return\s*\($', "Return statement is incomplete"),
        (r'\.\.\.$', "Code ends with '...'"),
    ]
    
    for pattern, message in truncation_signs:
        if re.search(pattern, last_line):
            issues.append(message)
    
    # Required patterns for React components - ONLY CRITICAL ONES
    required_patterns = [
        (r'import\s+React', "Missing React import"),
        (r'export\s+default', "Missing export default"),
    ]
    
    for pattern, message in required_patterns:
        if not re.search(pattern, code):
            issues.append(message)
    
    # LENIENT brace/paren checking - only flag if severely unbalanced (> 3 difference)
    open_braces = code.count('{')
    close_braces = code.count('}')
    open_parens = code.count('(')
    close_parens = code.count(')')
    
    brace_diff = abs(open_braces - close_braces)
    paren_diff = abs(open_parens - close_parens)
    
    if brace_diff > 3:
        issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
    
    if paren_diff > 3:
        issues.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    if paren_diff > 3:
        issues.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    
    return len(issues) == 0, issues


def validate_file(code: str, filepath: str) -> Tuple[bool, List[str]]:
    """
    Validate any file based on its extension.
    
    Returns:
        (is_valid, list_of_issues)
    """
    filepath_lower = filepath.lower()
    
    if filepath_lower.endswith('.py'):
        return validate_python_code(code, filepath)
    elif filepath_lower.endswith('.jsx') or filepath_lower.endswith('.tsx'):
        return validate_jsx_code(code, filepath)
    elif filepath_lower.endswith('.js') or filepath_lower.endswith('.ts'):
        # Basic JS validation
        if not code or len(code.strip()) < 20:
            return False, ["Code is empty or too short"]
        return True, []
    elif filepath_lower.endswith('.json'):
        try:
            import json
            json.loads(code)
            return True, []
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
    else:
        # For other files, just check they're not empty
        if not code or len(code.strip()) < 10:
            return False, ["File is empty or too short"]
        return True, []


def is_code_truncated(code: str, filepath: str) -> bool:
    """Quick check if code appears to be truncated."""
    is_valid, issues = validate_file(code, filepath)
    
    truncation_keywords = ['truncated', 'incomplete', 'unclosed', 'missing']
    for issue in issues:
        if any(keyword in issue.lower() for keyword in truncation_keywords):
            return True
    
    return False
