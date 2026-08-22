# DECISIONS.md

Running log of what was chosen, what was rejected and why, what got cut

---

## Day 1 - Stack choice

**Chosen:** FastAPI + Python's asyncio for the gateway, with Pydantic
for the canonical resident model.

**Why**: No frontend is needed for this problem, so FastAPI’s built-in /docs page can be used to demonstrate the API.

