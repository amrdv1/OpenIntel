from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager

from database.session import get_db
from cache.redis_client import get_redis
from search.es_client import ESManager, get_es
from search.service import init_es_indices
from graph.neo4j_client import Neo4jManager, get_neo4j
from neo4j import AsyncDriver

from api.routes import search as search_router
from api.routes import reports as reports_router
from api.routes import graph as graph_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    es_client = ESManager.get_client()
    await init_es_indices(es_client)
    neo4j_driver = Neo4jManager.get_driver()
    yield
    # Shutdown
    await ESManager.close_client()
    await Neo4jManager.close_driver()

app = FastAPI(
    title="OpenIntel API",
    description="Enterprise OSINT Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production нужно указать конкретные домены
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов API
app.include_router(search_router.router, prefix="/api")
app.include_router(reports_router.router, prefix="/api")
app.include_router(graph_router.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to OpenIntel API"}

@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection is successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health/cache")
async def health_cache(redis_client: redis.Redis = Depends(get_redis)):
    try:
        await redis_client.ping()  # type: ignore
        return {"status": "ok", "message": "Redis connection is successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health/search")
async def health_search(es_client: AsyncElasticsearch = Depends(get_es)):
    try:
        info = await es_client.info()
        return {"status": "ok", "message": "Elasticsearch connection is successful", "cluster_name": info.get("cluster_name")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health/graph")
async def health_graph(neo4j_driver: AsyncDriver = Depends(get_neo4j)):
    try:
        await neo4j_driver.verify_connectivity()
        return {"status": "ok", "message": "Neo4j connection is successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
