import asyncio
from celery.utils.log import get_task_logger
from elasticsearch import AsyncElasticsearch
from neo4j import AsyncGraphDatabase
from backend.worker.celery_app import celery_app
from backend.adapters.engine import plugin_engine
from backend.adapters.schemas import AdapterRequest
from backend.config.settings import settings
import datetime

logger = get_task_logger(__name__)

async def run_async_search(query: str, query_type: str):
    """Асинхронная обертка для вызова движка"""
    req = AdapterRequest(query=query, query_type=query_type)
    results = await plugin_engine.execute_search(req)
    results_dict = [res.model_dump() for res in results]
    
    # Сохраняем в Elasticsearch
    if results_dict:
        try:
            es = AsyncElasticsearch([f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
            doc = {
                "query": query,
                "type": query_type,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "results": results_dict
            }
            await es.index(index="osint_reports", document=doc)
            await es.close()
        except Exception as e:
            logger.error(f"Failed to save to Elasticsearch: {e}")

    # Сохраняем граф связей в Neo4j
    if results_dict:
        try:
            driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri, 
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            async with driver.session() as session:
                # 1. Создаем центральный узел (то, что искали)
                query_node_label = "Domain" if query_type == "domain" else "Email" if query_type == "email" else "User"
                await session.run(
                    f"MERGE (q:{query_node_label} {{value: $query}})",
                    query=query
                )
                
                # 2. Обрабатываем результаты
                for res in results_dict:
                    source = res.get("source")
                    status = res.get("status")
                    if status != "success":
                        continue
                        
                    raw = res.get("raw_data", {})
                    
                    if source == "hunter_io" and query_type == "domain":
                        # Найдены емейлы для домена
                        emails = raw.get("emails", [])
                        for em in emails:
                            await session.run(
                                """
                                MATCH (d:Domain {value: $domain})
                                MERGE (e:Email {value: $email})
                                MERGE (d)-[:HAS_EMAIL]->(e)
                                """,
                                domain=query, email=em
                            )
                    
                    elif source == "github":
                        # Связь профиля с email или просто создание профиля
                        username = raw.get("login", "")
                        if username:
                            await session.run(
                                """
                                MERGE (u:GitHubUser {value: $username, url: $url})
                                """,
                                username=username, url=res.get("profile_url", "")
                            )
                            if query_type == "email":
                                await session.run(
                                    """
                                    MATCH (e:Email {value: $email})
                                    MATCH (u:GitHubUser {value: $username})
                                    MERGE (e)-[:LINKED_TO]->(u)
                                    """,
                                    email=query, username=username
                                )

                    elif source == "shodan" and query_type == "domain":
                        ip = raw.get("top_ip")
                        if ip:
                            await session.run(
                                """
                                MATCH (d:Domain {value: $domain})
                                MERGE (i:IPAddress {value: $ip, org: $org})
                                MERGE (d)-[:RESOLVES_TO]->(i)
                                """,
                                domain=query, ip=ip, org=raw.get("top_org", "")
                            )
                            
            await driver.close()
        except Exception as e:
            logger.error(f"Failed to save to Neo4j: {e}")

    return results_dict

@celery_app.task(bind=True, name="search_osint_task")
def search_osint_task(self, query: str, query_type: str):
    """
    Celery-задача для выполнения OSINT-поиска в фоне.
    Так как Celery синхронный, мы запускаем асинхронный код через asyncio.run()
    """
    logger.info(f"Starting OSINT search task for {query_type}:{query}")
    try:
        results = asyncio.run(run_async_search(query, query_type))
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Возвращаем ошибку в результат, чтобы пользователь мог её увидеть
        return {"status": "error", "message": str(e), "results": []}
