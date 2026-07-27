from pydantic import BaseModel, Field
from typing import List, Optional
from backend.adapters.schemas import SearchResult

class SearchRequestParams(BaseModel):
    query: str = Field(..., description="Строка поиска (email, username, domain и т.д.)")
    query_type: str = Field(..., description="Тип запроса для маршрутизации по плагинам (email, username, domain, company)")

class SearchResponse(BaseModel):
    query: str
    query_type: str
    cached: bool = False
    results: List[SearchResult] = []

class TaskResponse(BaseModel):
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[List[SearchResult]] = None

class ReportItem(BaseModel):
    id: str
    query: str
    type: str
    created_at: str
    results_count: int

class ReportsResponse(BaseModel):
    reports: List[ReportItem]

class GraphNode(BaseModel):
    id: str
    label: str
    value: str

class GraphLink(BaseModel):
    source: str
    target: str
    type: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]
