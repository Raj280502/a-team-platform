from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
import re



class FileArtifact(BaseModel):
    """Represents a single generated file with validation."""
    path: str = Field(
        ...,
        description="Relative file path, e.g. Dockerfile, backend/app.py, requirements.txt"
    )

    content: str = Field(
        ...,
        description="Complete, valid file content",
        max_length=50000  # ~50KB limit
    )
    

class CoderOutput(BaseModel):
    """Structured output of the Coder agent - ONLY files, no free text."""
    
    files: Dict[str, FileArtifact] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="Generated files indexed by path"
    )
    
    