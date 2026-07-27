import httpx
from abc import ABC, abstractmethod
from typing import List
from backend.adapters.schemas import SearchResult, AdapterRequest

class BaseAdapter(ABC):
    """
    Абстрактный базовый класс для всех OSINT-плагинов.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Уникальное имя плагина (например, 'github')."""
        pass

    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """Список поддерживаемых типов запросов (например, ['username', 'email'])."""
        pass

    @property
    def timeout(self) -> int:
        """Таймаут запроса в секундах (по умолчанию 10)."""
        return 10

    @abstractmethod
    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        """
        Основной метод выполнения поиска.
        
        :param request: Объект запроса, содержащий query и query_type.
        :param client: Глобальный асинхронный HTTP-клиент (httpx.AsyncClient) для запросов.
        :return: SearchResult
        """
        pass
