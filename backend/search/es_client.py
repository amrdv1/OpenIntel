from elasticsearch import AsyncElasticsearch
from typing import AsyncGenerator, Optional
from backend.config.settings import settings

class ESManager:
    client: Optional[AsyncElasticsearch] = None

    @classmethod
    def get_client(cls) -> AsyncElasticsearch:
        if cls.client is None:
            # We configure basic auth, though we disabled xpack.security in compose
            # Passing it doesn't hurt.
            cls.client = AsyncElasticsearch(
                settings.elastic_url,
                basic_auth=("elastic", settings.ELASTIC_PASSWORD),
                request_timeout=30
            )
        return cls.client

    @classmethod
    async def close_client(cls):
        if cls.client is not None:
            await cls.client.close()
            cls.client = None

async def get_es() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = ESManager.get_client()
    yield client
