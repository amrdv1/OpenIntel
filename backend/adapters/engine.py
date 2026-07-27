import os
import importlib
import inspect
import asyncio
import httpx
import logging
from typing import List, Dict, Type

from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest

logger = logging.getLogger(__name__)

class PluginEngine:
    def __init__(self):
        self.adapters: Dict[str, BaseAdapter] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Динамически загружает все адаптеры из папки plugins."""
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if not os.path.exists(plugins_dir):
            return

        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = f"backend.adapters.plugins.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseAdapter) and obj is not BaseAdapter:
                            # Пропускаем абстрактные классы, если они вдруг есть
                            if not inspect.isabstract(obj):
                                instance = obj()
                                self.adapters[instance.name] = instance
                                logger.info(f"Loaded plugin: {instance.name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin from {filename}: {e}")

    async def execute_search(self, request: AdapterRequest) -> List[SearchResult]:
        """
        Выполняет поиск по всем плагинам, поддерживающим данный query_type.
        Запускает их параллельно с использованием общего httpx.AsyncClient.
        """
        applicable_adapters = [
            adapter for adapter in self.adapters.values()
            if request.query_type in adapter.supported_types
        ]

        if not applicable_adapters:
            logger.warning(f"No adapters found for query_type: {request.query_type}")
            return []

        # Используем единый клиент для группы запросов для оптимизации (connection pooling)
        async with httpx.AsyncClient() as client:
            tasks = []
            for adapter in applicable_adapters:
                # Обертка для обработки ошибок на уровне движка
                tasks.append(self._safe_execute(adapter, request, client))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            final_results = []
            for res in results:
                if isinstance(res, Exception):
                    # Если gather вернул исключение (хотя _safe_execute должен ловить всё)
                    logger.error(f"Unhandled exception in gather: {res}")
                else:
                    final_results.append(res)
            return final_results

    async def _safe_execute(self, adapter: BaseAdapter, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        try:
            # Ограничиваем время выполнения на уровне движка
            async with asyncio.timeout(adapter.timeout):
                return await adapter.search(request, client)
        except asyncio.TimeoutError:
            logger.error(f"Plugin {adapter.name} timed out.")
            return SearchResult(
                source=adapter.name,
                status="error",
                error_message="Timeout exceeded",
                raw_data={}
            )
        except Exception as e:
            logger.error(f"Plugin {adapter.name} failed with error: {e}")
            return SearchResult(
                source=adapter.name,
                status="error",
                error_message=str(e),
                raw_data={}
            )

# Глобальный инстанс движка для использования в FastAPI
plugin_engine = PluginEngine()
