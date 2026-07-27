import logging
from elasticsearch import AsyncElasticsearch

logger = logging.getLogger(__name__)

async def init_es_indices(client: AsyncElasticsearch):
    """
    Создает базовые индексы для платформы OpenIntel, если они не существуют.
    """
    index_name = "osint_reports"
    
    try:
        exists = await client.indices.exists(index=index_name)
        if not exists:
            # Создаем индекс с базовыми настройками (поиск по тексту, нестрогое соответствие)
            await client.indices.create(
                index=index_name,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    },
                    "mappings": {
                        "properties": {
                            "query": {"type": "keyword"},
                            "type": {"type": "keyword"},
                            "content": {"type": "text"},
                            "created_at": {"type": "date"},
                            "confidence": {"type": "float"}
                        }
                    }
                }
            )
            logger.info(f"Elasticsearch index '{index_name}' created.")
        else:
            logger.info(f"Elasticsearch index '{index_name}' already exists.")
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch indices: {e}")
