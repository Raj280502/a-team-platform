import re
import json


def extract_patch_json(text: str):
    """
    Extracts and safely parses a JSON patch from a model output,
    even if it contains raw newlines and quotes.
    """
    # extract first {...}
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON patch found")

    raw = match.group(0)

    # repair unescaped newlines and quotes inside values
    raw = raw.replace("\r", "").replace("\n", "\\n")
    raw = raw.replace('\\"', '"').replace('"', '\\"')

    try:
        return json.loads(raw)
    except Exception:
        # fallback – let python repair it
        return json.loads(raw.encode("utf-8", "ignore").decode())
