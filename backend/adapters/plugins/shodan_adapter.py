import httpx
from typing import List
from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest
from backend.config.settings import settings

class ShodanAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "shodan"

    @property
    def supported_types(self) -> List[str]:
        return ["domain"]

    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        if not settings.SHODAN_API_KEY:
            return SearchResult(
                source=self.name,
                status="error",
                error_message="Shodan API key not configured"
            )

        # Shodan Host Search API
        url = f"https://api.shodan.io/shodan/host/search?key={settings.SHODAN_API_KEY}&query={request.query}"

        try:
            response = await client.get(url, timeout=self.timeout)
            
            if response.status_code == 401:
                return SearchResult(
                    source=self.name,
                    status="error",
                    error_message="Invalid Shodan API key"
                )

            response.raise_for_status()
            data = response.json()

            total = data.get("total", 0)
            if total == 0:
                return SearchResult(
                    source=self.name,
                    status="not_found",
                    confidence=1.0,
                    error_message="No hosts found in Shodan for this domain"
                )

            # Берем наиболее релевантный хост или агрегируем инфу
            top_match = data["matches"][0]
            ip_str = top_match.get("ip_str")
            ports = [match.get("port") for match in data["matches"][:5]] # Берем порты с первых 5 совпадений
            org = top_match.get("org", "Unknown Org")

            summary = f"Organization: {org}. Top ports found: {list(set(ports))}."

            return SearchResult(
                source=self.name,
                status="success",
                profile_url=f"https://www.shodan.io/search?query={request.query}",
                title=f"Shodan Results for {request.query}",
                summary=summary,
                confidence=0.85,
                raw_data={"total_matches": total, "top_ip": ip_str, "top_org": org}
            )

        except Exception as e:
            return SearchResult(
                source=self.name,
                status="error",
                error_message=str(e)
            )
