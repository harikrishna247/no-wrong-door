import httpx
from xml.etree import ElementTree

from app.sources.base import SourceAdapter, SourceResult


class BenefitsRegisterAdapter(SourceAdapter):
    name = "benefits_register"

    def __init__(self, base_url: str = "http://127.0.0.1:8082"):
        self.base_url = base_url

    async def get(self, resident_ref: str) -> SourceResult:
        url = f"{self.base_url}/records/{resident_ref}"

        response = await self._call_with_retry(url)
        if response is None:
            return SourceResult(status="unavailable", reason="service unreachable after retry")

        if response.status_code == 404:
            return SourceResult(status="not_found")

        if response.status_code != 200:
            return SourceResult(status="unavailable", reason=f"failed with {response.status_code} after retry")

        try:
            record = self._parse_xml(response.text)
        except ElementTree.ParseError as exc:
            return SourceResult(status="unavailable", reason=f"malformed XML: {exc}")

        return SourceResult(status="ok", data=self._normalize(record))

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
        return {
            "ref": root.findtext("Ref"),
            "name": root.findtext("n"),
            "born": root.findtext("Born"),
            "addr": root.findtext("Addr"),
            "town": root.findtext("Town"),
            "benefit_code": root.findtext("BenefitCode"),
            "review_due": root.findtext("ReviewDue"),
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