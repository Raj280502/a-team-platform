from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
import re
    
  

class CoderOutput(BaseModel):
    """
    Structured output of the Coder agent.

    Rules:
    - Keys are relative file paths
    - Values are RAW file contents (plain text)
    - NO nested JSON
    """

    new_files: Optional[Dict[str, str]] = Field(
        default=None,
        description="New files to create: {relative_path: file_content}"
    )

    modified_files: Optional[Dict[str, str]] = Field(
        default=None,
        description="Files to modify: {relative_path: updated_content}"
    )