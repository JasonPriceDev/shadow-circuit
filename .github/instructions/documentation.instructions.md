---
applyTo: "docs/**/*.md,docs/sdlc/manifest.json"
---

# Documentation and Traceability

- Distinguish draft, approved, current, target, optional, and unresolved content.
- Specs need stable IDs, observable acceptance criteria, non-goals,
  dependencies, risks, open questions, and verification.
- Record confirmed discovery decisions; do not promote assumptions.
- Register tracked artifacts in `docs/sdlc/manifest.json`.
- Run `python scripts/sdlc/traceability.py validate` after relationship changes.
- Assess downstream impact when an upstream artifact changes.
- Prefer paths, symbols, issue numbers, and commit SHAs over line numbers.
- Report documentation drift instead of guessing.

Editing a Concept or Spec does not authorize downstream implementation.
