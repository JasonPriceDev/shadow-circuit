---
name: discover-concept
description: Interview a product owner, record confirmed discovery decisions, split a game concept into coherent draft specifications, and create reviewable SVG/HTML/Phaser prototypes. Use for concept discovery, requirements elicitation, spec authoring, mockups, prototypes, or revisions to a discovery package.
---

# Discover a Concept

1. Read `AGENTS.md`, the Concept, existing discovery records, existing Specs,
   and the tech-stack constraints.
2. Interview the human one question at a time. Prioritize player outcome, core
   loop, controls, failure/success, progression, screen states, accessibility,
   content scope, verification, dependencies, and non-goals.
3. After each answer, propose a concise decision. Record it only after
   confirmation. Keep assumptions and open questions separate.
4. Challenge contradictions and requirements that are subjective, untestable,
   technically incompatible, or too broad.
5. End discovery only when the core experience is explainable, material choices
   are confirmed or explicitly deferred, and each intended Spec has an
   observable outcome.
6. Choose the smallest coherent Spec set. Do not mirror document headings
   mechanically.
7. Create a discovery package:
   - `docs/discovery/<concept>/decisions.md`
   - `docs/discovery/<concept>/assumptions.md`
   - `docs/discovery/<concept>/open-questions.md`
   - draft files under `docs/specs/`
   - optional non-production artifacts under `docs/mockups/` or `prototypes/`
8. Give prototypes explicit launch and review steps. Prefer SVG or small
   HTML/CSS prototypes; use isolated Phaser only when interaction matters.
9. Register tracked artifacts in `docs/sdlc/manifest.json`, then run
   `python scripts/sdlc/traceability.py validate`.
10. Report confirmed decisions, unresolved questions, generated artifacts,
    validation evidence, and the exact human approval needed next.

Never edit production gameplay code during discovery. Never silently convert an
assumption, optional idea, or prototype shortcut into an acceptance criterion.
