import datetime
from fastapi import APIRouter, Depends
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
import hashlib

from backend.api.schemas import SearchRequestParams, SearchResponse, TaskResponse, TaskStatusResponse
from backend.adapters.schemas import AdapterRequest
from backend.adapters.engine import plugin_engine
from backend.cache.service import CacheService
from backend.cache.redis_client import get_redis
from backend.search.es_client import get_es
from backend.worker.tasks import search_osint_task
from celery.result import AsyncResult

router = APIRouter(prefix="/search", tags=["OSINT Search"])

def _generate_cache_key(query: str, query_type: str) -> str:
    raw = f"{query_type}:{query}".encode("utf-8")
    return "osint:search:" + hashlib.md5(raw).hexdigest()

@router.post("/", response_model=SearchResponse)
async def perform_search(
    params: SearchRequestParams,
    redis_client: redis.Redis = Depends(get_redis),
    es_client: AsyncElasticsearch = Depends(get_es)
):
    cache_service = CacheService(redis_client)
    cache_key = _generate_cache_key(params.query, params.query_type)

    # 1. Проверяем кэш
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        # Восстанавливаем объекты из кэша
        return SearchResponse(
            query=params.query,
            query_type=params.query_type,
            cached=True,
            results=cached_data
        )

    # 2. Выполняем поиск через плагины
    adapter_req = AdapterRequest(query=params.query, query_type=params.query_type)
    search_results = await plugin_engine.execute_search(adapter_req)

    # 3. Сохраняем результаты в кэш (TTL 24 часа по умолчанию в CacheService)
    # Преобразуем Pydantic модели в dict для JSON-сериализации
    results_dict = [res.model_dump() for res in search_results]
    await cache_service.set(cache_key, results_dict)

    # 4. Асинхронно (в фоне) сохраняем в Elasticsearch
    # Для упрощения в этом этапе делаем синхронно в рамках HTTP-запроса, 
    # в реальном production лучше отправлять это в Celery или фоновые задачи FastAPI
    if search_results:
        try:
            doc = {
                "query": params.query,
                "type": params.query_type,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "results": results_dict
            }
            await es_client.index(index="osint_reports", document=doc)
        except Exception as e:
            # Не падаем, если не удалось сохранить историю
            print(f"Failed to save to Elasticsearch: {e}")

    return SearchResponse(
        query=params.query,
        query_type=params.query_type,
        cached=False,
        results=search_results
    )

@router.post("/async", response_model=TaskResponse)
async def perform_search_async(
    params: SearchRequestParams,
    redis_client: redis.Redis = Depends(get_redis)
):
    # Опционально: можно тоже проверять кэш и если есть - не запускать таску
    
    # Запускаем Celery-задачу
    task = search_osint_task.delay(params.query, params.query_type)
    
    return TaskResponse(task_id=task.id, status="pending")

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    
    if task_result.ready():
        result = task_result.result or {}
        return TaskStatusResponse(
            task_id=task_id,
            status=result.get("status", "completed"),
            results=result.get("results", [])
        )
    else:
        return TaskStatusResponse(
            task_id=task_id,
            status=task_result.status
        )
