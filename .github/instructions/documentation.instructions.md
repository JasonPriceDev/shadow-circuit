---
applyTo: "docs/**/*.md"
---

# Documentation

- State document authority/status and, when useful, last-revised date.
- Distinguish current behavior, requirements, targets, optional ideas, open
  questions, and non-goals.
- Do not turn brainstorming into approved scope.
- Prefer paths, symbols, issue numbers, and commit SHAs over line numbers.
- Mark copied code as illustrative or name its canonical source.
- Report documentation drift instead of guessing.

Verify duplicated facts against their source:

- Stages/unlocks: `StageCatalog.ts`.
- Versions/scripts: manifests and lockfiles.
- TypeScript/Vite/Phaser configuration: their config files.
- Agent packages: `agents/requirements.txt`.
- Labels and approvals: `agentic-sdlc-workflow.md`.

Specs need a summary, observable acceptance criteria, constraints,
dependencies, risks/open questions, verification, and non-goals where needed.
Editing a Spec does not authorize implementation.

Use concise, testable language and consistent canonical names. Check headings,
links, tables, and code fences. Never claim an implementation or check exists
without verification.