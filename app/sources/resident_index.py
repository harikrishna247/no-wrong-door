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
    
    async def list_all(self, page_size: int = 25) -> dict:
        """
        Pages through the full resident index and de-duplicates by id,
        since the index re-orders live while paging, which can cause the
        same record to appear on more than one page (confirmed by the
        service's own docstring on boundary behaviour).
        """
        residents_by_id = {}
        page = 1

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                while True:
                    response = await client.get(
                        f"{self.base_url}/residents",
                        params={"page": page, "page_size": page_size},
                    )
                    if response.status_code != 200:
                        return {
                            "status": "unavailable",
                            "reason": f"page {page} returned {response.status_code}",
                            "residents": list(residents_by_id.values()),
                        }

                    body = response.json()
                    for raw in body.get("results", []):
                        residents_by_id[raw["id"]] = self._normalize(raw)

                    if not body.get("has_more"):
                        break
                    page += 1
        except httpx.RequestError as exc:
            return {
                "status": "unavailable",
                "reason": f"connection error on page {page}: {exc}",
                "residents": list(residents_by_id.values()),
            }

        return {"status": "ok", "residents": list(residents_by_id.values())}