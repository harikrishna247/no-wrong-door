import asyncio

from fastapi import FastAPI

from app.sources.resident_index import ResidentIndexAdapter
from app.sources.benefits_register import BenefitsRegisterAdapter

app = FastAPI()

resident_index = ResidentIndexAdapter()
benefits_register = BenefitsRegisterAdapter()


@app.get("/resident/{resident_id}")
async def get_resident(resident_id: str):
    results = await asyncio.gather(
        resident_index.get(resident_id),
        benefits_register.get(resident_id),
        return_exceptions=True,
    )

    resident_index_result, benefits_result = results

    return {
        "resident_id": resident_id,
        "sources": {
            "resident_index": _to_dict(resident_index_result),
            "benefits_register": _to_dict(benefits_result),
        },
    }


def _to_dict(result) -> dict:
    if isinstance(result, Exception):
        return {"status": "unavailable", "reason": f"unexpected error: {result}"}
    out = {"status": result.status}
    if result.data is not None:
        out["data"] = result.data
    if result.reason is not None:
        out["reason"] = result.reason
    return out