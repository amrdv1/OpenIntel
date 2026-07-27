import httpx
from typing import List
from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest
from backend.config.settings import settings

class HunterAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "hunter_io"

    @property
    def supported_types(self) -> List[str]:
        return ["domain", "email"]

    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        if not settings.HUNTER_API_KEY:
            return SearchResult(
                source=self.name,
                status="error",
                error_message="Hunter.io API key not configured"
            )

        if request.query_type == "domain":
            url = f"https://api.hunter.io/v2/domain-search?domain={request.query}&api_key={settings.HUNTER_API_KEY}"
        else:
            # Email Verification API
            url = f"https://api.hunter.io/v2/email-verifier?email={request.query}&api_key={settings.HUNTER_API_KEY}"

        try:
            response = await client.get(url, timeout=self.timeout)
            
            if response.status_code == 401:
                return SearchResult(
                    source=self.name,
                    status="error",
                    error_message="Invalid Hunter.io API key"
                )
                
            response.raise_for_status()
            data = response.json().get("data", {})

            if request.query_type == "domain":
                emails = data.get("emails", [])
                if not emails:
                    return SearchResult(
                        source=self.name,
                        status="not_found",
                        confidence=1.0,
                        error_message="No emails found for this domain"
                    )
                
                summary = f"Found {len(emails)} emails. Organization: {data.get('organization', 'Unknown')}"
                return SearchResult(
                    source=self.name,
                    status="success",
                    title=f"Hunter.io: {request.query}",
                    summary=summary,
                    confidence=0.9,
                    raw_data={"emails": [e.get("value") for e in emails[:10]], "pattern": data.get("pattern")}
                )
            else:
                # Email verification
                status = data.get("status")
                score = data.get("score", 0)
                
                if status == "invalid":
                    return SearchResult(
                        source=self.name,
                        status="not_found",
                        confidence=1.0,
                        summary="Email is invalid or does not exist."
                    )
                
                summary = f"Email Status: {status.capitalize()}. Deliverability Score: {score}%"
                return SearchResult(
                    source=self.name,
                    status="success",
                    title=f"Hunter.io Verification",
                    summary=summary,
                    confidence=score / 100.0,
                    raw_data=data
                )

        except Exception as e:
            return SearchResult(
                source=self.name,
                status="error",
                error_message=str(e)
            )
