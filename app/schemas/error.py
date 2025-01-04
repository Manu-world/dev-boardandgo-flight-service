from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponseSchema(BaseModel):
    detail: str
    code: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
