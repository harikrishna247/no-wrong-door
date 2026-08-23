# DECISIONS.md

Running log of what was chosen, what was rejected and why, what got cut

---

## Day 1 - Stack choice

**Chosen:** FastAPI + Python's asyncio for the gateway, with Pydantic
for the canonical resident model.

**Why**: No frontend is needed for this problem, so FastAPI's built-in /docs page can be used to demonstrate the API.

**Degradation policy**
1. there are three states:
    ok - source responded
    not_found - source responded but has no record for a particular id
    unavailable - source errored, timed out, or the id format doesn't match the source

2. Retry the XML GET request once if it fails, since the failure is often temporary.
If it fails again, mark it as unavailable.

3. Even if one or both sources are unavailable, the endpoint still returns 200 with whatever it has.

4. The same record may appear on two pages, so the gateway removes duplicates by id.

---

## Adapter contract revision

**Chosen:** Replaced the original `fetch()` + `normalize()` split with a single
`get()` method that returns a `SourceResult` (status: ok / not_found / unavailable).

**Why:** Deciding the status requires source-specific knowledge — was it a 404?
a 500? a connection error? — that only the adapter itself has. Splitting fetch
and normalize made sense before the degradation policy existed, but once
ok/not_found/unavailable was defined, one method that owns "ask the source,
interpret what happened" was cleaner than two methods that didn't talk to
each other.

---

## Adding GET /residents

**Chosen:** Added a paginated listing endpoint alongside the single-id lookup.

**Why:** The floor requires correctly handling the duplicate-across-pages bug,
but the original /resident/{id} design only calls /residents/{id} directly and
never touches pagination — so that floor item would go unaddressed by design.
/residents exercises the real paginated listing, with de-duplication by id.
It's also practically useful: a caller wouldn't know an exact id like R-10234
ahead of time, so a listing/browse endpoint isn't just there to check a box.

---

## Day 2 — Surprise challenge: Benefits Register degraded to 40% failure

**What changed:** The Benefits Register now fails ~40% of the time (up from 15%),
permanently. Announced as the Day 2 surprise.

**Chosen:** Added a last-known-good cache to BenefitsRegisterAdapter. The first
successful fetch for a ref is remembered in memory. If a later call fails (even
after the retry), the cached data is returned with a new "stale" status and a
reason, instead of "unavailable".

**Why:** At 40%, retry-once alone still fails visibly about 16% of the time
(0.4 x 0.4) — up from ~2% before. That's frequent enough to hit during a live
demo. Caching turns a real failure into data the system already knows, instead
of just retrying harder.

**Not changed:** The REST adapter (resident_index) — this source wasn't
affected, and per the Day One adapter-boundary decision, one source failing
shouldn't require changes to an unrelated one. Didn't add more retries either,
since each retry costs 0.7-2.4s and the cache was the more honest fix.

**Limitation:** The cache is in-memory and per-process — it's empty on a fresh
start, so a resident being looked up for the very first time while the source
is down still gets "unavailable". With more time, this would be worth
persisting.