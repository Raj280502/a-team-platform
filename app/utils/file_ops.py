"""
file_ops.py
-----------
Handles safe file system operations.

AI never writes to disk directly.
"""

from pathlib import Path


def write_files(base_dir: Path, files: dict):
    for artifact in files.values():

        # Prevent directory traversal
        if ".." in artifact.path:
            raise ValueError("Invalid file path detected")

        file_path = base_dir / artifact.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(artifact.content, encoding="utf-8")