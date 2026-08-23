# AI-USAGE.md

## Tool used
Claude (Anthropic), used interactively throughout the build.

## What it was used for
- Repo scaffolding: folder structure, commit sequencing, and the shape of
  DECISIONS.md, README.md, and this file.
- Concept explanations: asyncio.gather with return_exceptions, the adapter
  interface pattern (SourceAdapter/SourceResult), why pagination over a
  live-reordering list produces duplicates, why a dict de-dupes by key.
- Guidance while writing ResidentIndexAdapter, BenefitsRegisterAdapter, and
  the /resident/{id} and /residents endpoints. I wrote and typed the code
  myself, with the reasoning explained as we went.
- Debugging help on real issues hit during the build: a .gitignore pattern
  mismatch (venv/ vs .venv/), a file casing bug (Decisions.md vs
  DECISIONS.md), the XML adapter reading the wrong nesting level
  (<Record> is a child of the root, not the root itself), and a FastAPI
  routing bug where ids containing "/" weren't matching until the route
  became {resident_id:path}.
- Day 2 surprise challenge: guidance on designing the last-known-good cache
  for the Benefits Register adapter, including the retry-rate math that
  justified caching over just adding more retries.
- Help structuring README.md and DECISIONS.md.

## What it was not used for
- Deciding the degradation policy itself (ok/not_found/unavailable/stale) —
  my call, documented in DECISIONS.md.
- Writing code unsupervised — every file was typed and understood by me.