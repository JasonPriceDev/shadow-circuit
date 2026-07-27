# Specs

This directory is the single source of truth for feature, stage, boss, and system
specifications. Every significant piece of work starts as a spec before any code is
written.

## Issue hierarchy

```
Spec (top-level, only broken out if size warrants)
  └── Plan (agent-generated from the approved spec)
        └── Epics (large bodies of work — a stage, boss, or major system)
              └── Features (medium work units within an Epic)
                    └── Tasks (smallest unit — one pull request per task)

Bugs are separate — logged against a Feature (or Epic if the feature doesn't exist yet).
```

## Spec lifecycle

```
You write a spec → Open a type:spec issue → Agent reads it, asks questions
  → Spec approved → Agent generates a Plan
    → Plan broken into Epics (or Features if small)
      → Each Epic broken into Features
        → Each Feature broken into Tasks
          → Each Task gets one draft PR → CI passes → You approve and merge
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

## Issue types

| Type | Purpose | Parent | PRs? |
|---|---|---|---|
| `type:spec` | Top-level specification | — | No |
| `type:epic` | Large body of work (stage, boss, system) | Spec | No |
| `type:feature` | Medium work unit | Epic (or Spec if no Epic) | No |
| `type:task` | Smallest unit of work | Feature | **Yes — one PR per task** |
| `type:bug` | Defect | Feature or Epic | Yes (fix PR) |

| Spec | Covers | Status |
|---|---|---|
| `docs/plans/concept.md` | Full game design: 8 stages, bosses, abilities, scoring | Authoritative GDD |
| `docs/plans/tech-stack.md` | Engineering decisions | Authoritative |
