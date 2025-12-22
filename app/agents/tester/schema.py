from pydantic import BaseModel, Field
from typing import Optional



class TesterOutput(BaseModel):
    """Comprehensive test results with actionable insights."""
    
    # Overall summary
    tests_passed: bool = Field(..., description="All critical tests passed?")
    
    error_message: Optional[str] = Field(None, description="Critical failure summary")
    