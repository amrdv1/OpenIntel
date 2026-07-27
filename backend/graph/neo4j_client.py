from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import AsyncGenerator, Optional
from backend.config.settings import settings

class Neo4jManager:
    driver: Optional[AsyncDriver] = None

    @classmethod
    def get_driver(cls) -> AsyncDriver:
        if cls.driver is None:
            cls.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return cls.driver

    @classmethod
    async def close_driver(cls):
        if cls.driver is not None:
            await cls.driver.close()
            cls.driver = None

async def get_neo4j() -> AsyncGenerator[AsyncDriver, None]:
    """Dependency to get the neo4j driver inside endpoints."""
    driver = Neo4jManager.get_driver()
    yield driver
