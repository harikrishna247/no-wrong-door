import httpx

from app.sources.base import SourceAdapter, SourceResult


class ResidentIndexAdapter(SourceAdapter):
    name = "resident_index"

    def __init__(self, base_url: str = "http://127.0.0.1:8081"):
        self.base_url = base_url

    async def get(self, resident_id: str) -> SourceResult:
        url = f"{self.base_url}/residents/{resident_id}"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            return SourceResult(status="unavailable", reason=f"connection error: {exc}")

        if response.status_code == 404:
            return SourceResult(status="not_found")

        if response.status_code != 200:
            return SourceResult(status="unavailable", reason=f"unexpected status {response.status_code}")

        raw = response.json()
        return SourceResult(status="ok", data=self._normalize(raw))

    def _normalize(self, raw: dict) -> dict:
        return {
            "source": self.name,
            "id": raw.get("id"),
            "name": f"{raw.get('first_name', '')} {raw.get('last_name', '')}".strip(),
            "date_of_birth": raw.get("date_of_birth"),
            "address": raw.get("address_line"),
            "city": raw.get("city"),
            "phone": raw.get("phone"),
            "program_status": raw.get("program_status"),
            "last_contact": raw.get("last_contact"),
        }