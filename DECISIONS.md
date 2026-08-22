# DECISIONS.md

Running log of what was chosen, what was rejected and why, what got cut

---

## Day 1 - Stack choice

**Chosen:** FastAPI + Python's asyncio for the gateway, with Pydantic
for the canonical resident model.

**Why**: No frontend is needed for this problem, so FastAPI’s built-in /docs page can be used to demonstrate the API.

**Degradation policy**
1.there are three states:
    ok - source responded
    not_found - source responded but has no record for an particular id
    unavailable - source errored , timed out ,or the id format doesn't math the source

2.Retry the XML GET request once if it fails, since the failure is often temporary.
If it fails again, mark it as unavailable

3.even if one or both sources are unavailable , the endpoint still returns 200 with whatever it has

4.The same record may appear on two pages, so the gateway should remove duplicatesThe same record may appear on two pages, so the gateway should remove duplicates