"""
file_ops.py
-----------
Handles safe file system operations.

Responsibilities:
- Normalize AI-generated code
- Prevent malformed writes
- Write files safely to disk

AI agents NEVER write files directly.
"""

from pathlib import Path
import re

def normalize_code(content: str) -> str:
    """
    Fix accidental JSON-stringified code.

    This happens when the LLM wraps code inside a JSON string.

    Example bad output:
        "{ \"from flask import Flask\\napp = Flask(__name__)\" }"

    This function cleans it into valid source code.
    """
    content = content.strip()

    # Remove all markdown fences robustly
    content = re.sub(r"^```[a-zA-Z]*\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    return content.strip()


def write_files(base_dir: Path, files: dict[str, str]):
    """
    Writes files to disk after normalization.

    Args:
        base_dir (Path): Root directory of generated project
        files (dict): {relative_path: file_content}
    """

    for relative_path, raw_content in files.items():

        # Security check: prevent directory traversal
        if ".." in relative_path:
            raise ValueError("Invalid file path detected")

        file_path = base_dir / relative_path

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Normalize content before writing
        clean_content = normalize_code(raw_content)

        # Write file
        file_path.write_text(clean_content, encoding="utf-8")
