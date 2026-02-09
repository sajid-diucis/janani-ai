from typing import Dict, Any, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    """Standardized result from any agent tool"""
    success: bool
    tool_name: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_tuple(self) -> tuple[str, Optional[Dict[str, Any]]]:
        """Convert to legacy format (message, data) for backward compatibility"""
        return (self.message, self.data)
