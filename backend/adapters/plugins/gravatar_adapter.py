import httpx
import hashlib
from typing import List
from backend.adapters.base import BaseAdapter
from backend.adapters.schemas import SearchResult, AdapterRequest

class GravatarAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "gravatar"

    @property
    def supported_types(self) -> List[str]:
        return ["email"]

    async def search(self, request: AdapterRequest, client: httpx.AsyncClient) -> SearchResult:
        # Gravatar requires MD5 hash of the lowercase email
        email_hash = hashlib.md5(request.query.strip().lower().encode("utf-8")).hexdigest()
        url = f"https://en.gravatar.com/{email_hash}.json"
        
        headers = {"User-Agent": "OpenIntel OSINT Platform"}

        try:
            response = await client.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 404:
                return SearchResult(
                    source=self.name,
                    status="not_found",
                    confidence=1.0,
                    error_message="Gravatar profile not found"
                )

            response.raise_for_status()
            data = response.json()
            
            if not data.get("entry"):
                return SearchResult(
                    source=self.name,
                    status="not_found"
                )

            profile = data["entry"][0]
            displayName = profile.get("displayName", "Unknown")
            aboutMe = profile.get("aboutMe", "")
            profileUrl = profile.get("profileUrl")

            return SearchResult(
                source=self.name,
                status="success",
                profile_url=profileUrl,
                title=f"Gravatar: {displayName}",
                summary=aboutMe or "Public profile found",
                confidence=1.0,
                raw_data=profile
            )

        except Exception as e:
            return SearchResult(
                source=self.name,
                status="error",
                error_message=str(e)
            )
