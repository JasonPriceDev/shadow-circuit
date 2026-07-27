# Specs

This directory is the single source of truth for feature, stage, boss, and system specifications. Every significant piece of work starts as a spec before any code is written.

## Spec lifecycle

```
You write a spec → Open a type:spec issue → Agent reads it, asks questions
  → Agent generates a plan (task checklist) → Agent opens one issue per task
    → Each task gets one draft PR → CI passes → You approve and merge → Done
```

## Spec format

Create a Markdown file in this directory. Minimum sections:

```markdown
# Spec: [Title]

Status: Draft | Approved | In Progress | Done

## Summary
One paragraph describing what this is and why.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Design Notes
Mechanics, boss patterns, level layouts, tuning — whatever the agent needs to plan.

## Dependencies
What must exist before this can be built.

## Risks / Open Questions
What's uncertain, what could go wrong.
```

## Example

See `docs/plans/concept.md` for the game-level design document.
See `docs/plans/tech-stack.md` for the engineering decisions document.

## Existing specs

| Spec | Covers | Status |
|---|---|---|
| `docs/plans/concept.md` | Full game design: 8 stages, bosses, abilities, scoring | Authoritative GDD |
| `docs/plans/tech-stack.md` | Engineering decisions | Authoritative |
