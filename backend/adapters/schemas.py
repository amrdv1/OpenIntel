from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List

class SearchResult(BaseModel):
    source: str
    status: str  # e.g., "success", "error", "not_found"
    profile_url: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    confidence: float = 0.0
    raw_data: Dict[str, Any] = {}
    error_message: Optional[str] = None

class AdapterRequest(BaseModel):
    query: str
    query_type: str  # e.g., "email", "username", "domain", "company"
