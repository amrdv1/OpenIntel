import httpx
from typing import List
from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest

class GithubAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "github"

    @property
    def supported_types(self) -> List[str]:
        return ["username", "email"]

    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        if request.query_type == "username":
            url = f"https://api.github.com/users/{request.query}"
        else:
            # Поиск по email
            url = f"https://api.github.com/search/users?q={request.query} in:email"

        headers = {"Accept": "application/vnd.github.v3+json"}
        
        try:
            response = await client.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 404:
                return SearchResult(
                    source=self.name,
                    status="not_found",
                    confidence=1.0,
                    error_message="User not found on GitHub"
                )
            
            if response.status_code == 403 or response.status_code == 429:
                return SearchResult(
                    source=self.name,
                    status="error",
                    error_message="GitHub API Rate Limit exceeded"
                )

            response.raise_for_status()
            data = response.json()
            
            if request.query_type == "email":
                # Обработка ответа search API
                if data.get("total_count", 0) == 0:
                    return SearchResult(
                        source=self.name,
                        status="not_found",
                        confidence=1.0
                    )
                # Берем первого найденного
                user_data = data["items"][0]
                # Можно сделать дополнительный запрос, но для простоты берем базовые данные
                profile_url = user_data.get("html_url")
                username = user_data.get("login")
                
                return SearchResult(
                    source=self.name,
                    status="success",
                    profile_url=profile_url,
                    title=f"GitHub User: {username}",
                    summary="Found via Email search.",
                    confidence=0.9,
                    raw_data=user_data
                )
            else:
                # Обработка прямого запроса пользователя
                return SearchResult(
                    source=self.name,
                    status="success",
                    profile_url=data.get("html_url"),
                    title=data.get("name") or data.get("login"),
                    summary=data.get("bio") or f"Company: {data.get('company')}, Location: {data.get('location')}",
                    confidence=1.0,
                    raw_data=data
                )

        except Exception as e:
            return SearchResult(
                source=self.name,
                status="error",
                error_message=str(e)
            )
