import httpx
from xml.etree import ElementTree

from app.sources.base import SourceAdapter, SourceResult


class BenefitsRegisterAdapter(SourceAdapter):
    name = "benefits_register"

    def __init__(self, base_url: str = "http://127.0.0.1:8082"):
        self.base_url = base_url
        self._cache: dict[str, dict] = {}  # ref -> last known-good normalized data

    async def get(self, resident_ref: str) -> SourceResult:
        url = f"{self.base_url}/records/{resident_ref}"

        response = await self._call_with_retry(url)
        if response is None:
            return self._fallback_or_unavailable(resident_ref, "service unreachable after retry")

        if response.status_code == 404:
            return SourceResult(status="not_found")

        if response.status_code != 200:
            return self._fallback_or_unavailable(
                resident_ref, f"failed with {response.status_code} after retry"
            )

        try:
            record = self._parse_xml(response.text)
        except ElementTree.ParseError as exc:
            return self._fallback_or_unavailable(resident_ref, f"malformed XML: {exc}")

        normalized = self._normalize(record)
        self._cache[resident_ref] = normalized  # remember this success
        return SourceResult(status="ok", data=normalized)

    def _fallback_or_unavailable(self, resident_ref: str, reason: str) -> SourceResult:
        """
        Live call failed. If we've successfully fetched this ref before in
        this process's lifetime, serve that instead of a bare failure —
        clearly labeled 'stale' so the caller knows it's not fresh.
        """
        cached = self._cache.get(resident_ref)
        if cached is not None:
            return SourceResult(status="stale", data=cached, reason=f"live call failed ({reason}); showing last known data")
        return SourceResult(status="unavailable", reason=reason)
    async def _call_with_retry(self, url: str):
        """
        This source fails ~15% of calls randomly and is always slow.
        Per DECISIONS.md: retry once on failure, since a GET has no side
        effects and the failure is usually transient, not a real outage.
        """
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url)
                if response.status_code == 200 or response.status_code == 404:
                    return response
                # a 500 or similar - worth one retry before giving up
            except httpx.RequestError:
                pass  # connection-level failure - also worth one retry
        return None

    def _parse_xml(self, xml_text: str) -> dict:
        root = ElementTree.fromstring(xml_text)
        record = root.find("Record")
        if record is None:
            record = root 
        return {
            "ref": record.findtext("Ref"),
            "name": record.findtext("Name"),
            "born": record.findtext("Born"),
            "addr": record.findtext("Addr"),
            "town": record.findtext("Town"),
            "benefit_code": record.findtext("BenefitCode"),
            "review_due": record.findtext("ReviewDue"),
        }

    def _normalize(self, record: dict) -> dict:
        return {
            "source": self.name,
            "ref": record.get("ref"),
            "name": record.get("name"),
            "date_of_birth": record.get("born"),
            "address": record.get("addr"),
            "city": record.get("town"),
            "benefit_code": record.get("benefit_code"),
            "review_due": record.get("review_due"),
        }