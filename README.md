# No Wrong Door — Resident Data Integration Gateway

A single API that gives a unified view of a resident by combining data from multiple systems, even when some of those systems are slow or down.

## Prerequisites

- Python 3 (no other dependencies needed for the mock services themselves)

## Setup (from a clean clone)

git clone https://github.com/harikrishna247/no-wrong-door.git
cd no-wrong-door
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

## Configuration

The gateway expects the mock services on their default ports:
- Resident Index (REST): 8081
- Benefits Register (XML): 8082

Both are configurable via --port if you need to change them (see below).

## Running it (3 terminals)

**Terminal 1 — Resident Index (REST):**
python mock_services/rest_service.py --port 8081

**Terminal 2 — Benefits Register (XML):**
python mock_services/xml_service.py --port 8082

**Terminal 3 — the gateway itself:**
python -m uvicorn app.main:app --reload

## Trying it

Browser: http://127.0.0.1:8000/docs
- Try /resident/{resident_id} with id R-10234 (a real REST-source id)

Terminal (needed for ids containing slashes, since Swagger double-encodes them):
curl.exe 'http://127.0.0.1:8000/resident/AS%2F2017%2F4288'
curl.exe 'http://127.0.0.1:8000/residents'

## Endpoints

- GET /resident/{id} — Calls both sources concurrently for the given id. Returns a per-source result: ok with data, not_found if that source has no record for this id, or unavailable with a reason if the source failed. Always returns 200, even if one or both sources are down.
- GET /residents — Pages through the full Resident Index (REST source), de-duplicating by id, since the same record can appear on more than one page while paging.

## Project layout

app/
  main.py                     FastAPI app + /resident/{id} and /residents endpoints
  sources/
    base.py                   SourceAdapter contract: get() returns a SourceResult
                              (status: ok / not_found / unavailable)
    resident_index.py         Adapter for the REST source (Resident Index).
                               Handles single lookup + paginated listing with dedup.
    benefits_register.py      Adapter for the XML source (Benefits Register).
                               Handles retry-once on failure, XML parsing.
mock_services/
  rest_service.py             Provided mock: Resident Index (REST, port 8081)
  xml_service.py              Provided mock: Benefits Register (XML, port 8082)
  run_both.sh                 Provided convenience script (bash — see README for
                               the Windows equivalent using two terminals)
  _rest_data.json             Backing data for the REST mock (read-only reference)
  _xml_data.json              Backing data for the XML mock (read-only reference)
DECISIONS.md                  What was chosen, rejected, and why
AI-USAGE.md                   Disclosure of AI tooling used in this build
README.md                     This file
requirements.txt              Python dependencies
.gitignore

## Design decisions

See DECISIONS.md for the reasoning behind the stack, the degradation policy,
and the adapter contract.