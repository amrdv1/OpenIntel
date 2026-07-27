from fastapi import APIRouter, Depends, Query
from elasticsearch import AsyncElasticsearch
from typing import Optional

from backend.api.schemas import ReportsResponse, ReportItem
from backend.search.es_client import get_es

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/", response_model=ReportsResponse)
async def get_reports(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(50, description="Max number of reports to return"),
    es_client: AsyncElasticsearch = Depends(get_es)
):
    # Если есть поисковый запрос, ищем по полю query, иначе достаем последние
    body = {
        "size": limit,
        "sort": [{"created_at": {"order": "desc"}}],
    }
    
    if q:
        body["query"] = {
            "match": {
                "query": q
            }
        }
    else:
        body["query"] = {"match_all": {}}

    try:
        res = await es_client.search(index="osint_reports", body=body)
        hits = res["hits"]["hits"]
        
        reports = []
        for hit in hits:
            source = hit["_source"]
            reports.append(ReportItem(
                id=hit["_id"],
                query=source.get("query", ""),
                type=source.get("type", ""),
                created_at=source.get("created_at", ""),
                results_count=len(source.get("results", []))
            ))
            
        return ReportsResponse(reports=reports)
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return ReportsResponse(reports=[])
