import httpx
import asyncio
from backend.config.settings import settings

class OpenIntelClient:
    def __init__(self):
        self.base_url = settings.API_URL_FOR_BOT
        
    async def execute_scan(self, query: str, query_type: str) -> dict:
        """
        Sends scan request to backend and polls until complete
        """
        async with httpx.AsyncClient() as client:
            # 1. Start async task
            response = await client.post(
                f"{self.base_url}/api/search/async",
                json={"query": query, "query_type": query_type}
            )
            response.raise_for_status()
            data = response.json()
            task_id = data.get("task_id")
            
            if not task_id:
                raise Exception("Failed to get task ID from backend")
                
            # 2. Poll for results
            max_attempts = 60 # 2 minutes max (2s interval)
            attempts = 0
            
            while attempts < max_attempts:
                status_res = await client.get(f"{self.base_url}/api/search/status/{task_id}")
                status_res.raise_for_status()
                status_data = status_res.json()
                
                if status_data.get("status") == "SUCCESS":
                    return status_data.get("result", {})
                elif status_data.get("status") == "FAILURE":
                    raise Exception(status_data.get("error", "Unknown scan failure"))
                    
                attempts += 1
                await asyncio.sleep(2)
                
            raise Exception("Scan timed out")
