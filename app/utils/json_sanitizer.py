import re

def extract_json(text: str) -> str:
    # Extract first JSON object from garbage text
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")
    return match.group(0)
