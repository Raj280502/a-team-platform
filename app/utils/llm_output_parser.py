"""
Custom LLM Output Parser for Code Generation

This parser handles LLM output that contains code blocks in a format
that's easier for LLMs to generate correctly than escaped JSON strings.
"""

import re
import json
from typing import Dict, Any


def parse_code_blocks(text: str) -> Dict[str, str]:
    """
    Parse code blocks from LLM output using markdown-style formatting.
    
    Expected format:
    ```filename: path/to/file.py
    code content here
    ```
    
    Or:
    ```path/to/file.py
    code content here
    ```
    
    Or JSON format:
    {"modified_files": {"path/to/file.py": "code here"}}
    
    Returns:
        Dict mapping file paths to code content
    """
    result = {}
    
    # First, try to parse markdown code blocks
    try:
        # Pattern matches: ```optional_lang optional_filename:\npath\ncode\n```
        # More flexible pattern that handles various formats
        pattern = r'```(?:[a-z]*\s*)?(?:filename:\s*)?([^\n`]+\.(?:py|jsx?|html|json|css|txt))\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for filename, code in matches:
                filename = filename.strip()
                result[filename] = code.strip()
            
            if result:
                print(f"[DEBUG] Extracted {len(result)} files via markdown blocks")
                return result
    except Exception as e:
        print(f"[DEBUG] Code block parsing failed: {e}")
    
    # Try to extract JSON, but with lenient parsing
    try:
        json_match = re.search(r'\{[\s\S]*"modified_files"[\s\S]*\}', text)
        if json_match:
            json_str = json_match.group(0)
            # Try standard JSON parsing
            try:
                data = json.loads(json_str)
                if "modified_files" in data:
                    return data["modified_files"]
                elif "new_files" in data:
                    return data["new_files"]
            except json.JSONDecodeError:
                # Try to extract file paths and code manually
                return extract_files_manually(json_str)
    except Exception as e:
        print(f"[DEBUG] JSON extraction failed: {e}")
    
    return result


def extract_files_manually(json_str: str) -> Dict[str, str]:
    """
    Manually extract file paths and content when JSON parsing fails.
    
    This is a fallback when the JSON is malformed due to unescaped quotes.
    """
    result = {}
    
    try:
        # Look for patterns like "filename": "content"
        # This is a simple heuristic that looks for file paths followed by content
        pattern = r'"([^"]+\.(py|jsx?|html|json|css))"\s*:\s*"([^"]*(?:\\"[^"]*)*)"'
        matches = re.findall(pattern, json_str)
        
        for filename, _, code in matches:
            # Unescape the code
            code = code.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            result[filename] = code
            
    except Exception as e:
        print(f"[DEBUG] Manual extraction failed: {e}")
    
    return result


def parse_repair_output(raw_output: Any) -> Dict[str, Any]:
    """
    Parse repair node output from LLM.
    
    Args:
        raw_output: Raw output from LLM (could be string or object with .content)
        
    Returns:
        Dict with "modified_files" key containing file modifications
    """
    # Extract text content
    if hasattr(raw_output, 'content'):
        text = raw_output.content
    else:
        text = str(raw_output)
    
    print(f"[DEBUG] Parsing repair output, length: {len(text)}")
    
    # Try to parse code blocks or JSON
    files = parse_code_blocks(text)
    
    if not files:
        print("[DEBUG] No files extracted from output")
        print(f"[DEBUG] First 500 chars: {text[:500]}")
    else:
        print(f"[DEBUG] Successfully extracted {len(files)} file(s)")
    
    return {"modified_files": files}
