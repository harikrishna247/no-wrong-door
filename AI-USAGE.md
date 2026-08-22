# AI-USAGE.md

## Tools used
Claude (Anthropic), used interactively throughout the build.

## What it was used for
- Repo/file scaffolding: guidance on folder structure, commit sequencing,
  and the shape of DECISIONS.md / README.md / this file.
- Concept explanations: asyncio.gather with return_exceptions, the
  adapter interface pattern (fetch()/normalize()), field-level conflict
  resolution strategy — explained so I could implement them myself.
- Code review / debugging: [update as this happens — e.g. "reviewed the
  timeout handling in gateway.py and caught a case where a slow source
  wasn't being cancelled properly"].
- Did not use it for: writing the resolver logic, the adapters, or the
  core gateway endpoint .

## Note
This file is updated as the build progresses, not written once at the end.