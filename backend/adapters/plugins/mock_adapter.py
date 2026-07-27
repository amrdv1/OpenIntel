import httpx
from typing import List
from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest

class MockAdapter(BaseAdapter):
    """
    Тестовый адаптер-заглушка для демонстрации работы Plugin Engine.
    """
    
    @property
    def name(self) -> str:
        return "mock_source"

    @property
    def supported_types(self) -> List[str]:
        return ["email", "username"]

    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        # Имитируем полезную работу
        return SearchResult(
            source=self.name,
            status="success",
            profile_url=f"https://mocksource.local/{request.query}",
            title=f"Mock Profile for {request.query}",
            summary="This is a generated mock profile for testing purposes.",
            confidence=1.0,
            raw_data={"found_in": "mock_db", "query": request.query}
        )
