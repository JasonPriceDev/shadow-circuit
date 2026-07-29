# Agentic SDLC Workflow

Status: **Draft for review**

Last revised: **2026-07-27**

## 1. Purpose

This workflow takes Shadow Circuit from product concept through discovery,
approved specifications, synchronized work items, implementation, review, and
release. Humans own product decisions and authorization. Agents conduct
discovery, draft artifacts, analyze impact, propose plans, implement approved
Tasks, and report evidence.

GitHub is the durable control plane. VS Code provides the high-bandwidth
discovery experience. DeepSeek V4 Pro is the primary model in both VS Code and
the GitHub Actions harness.

## 2. Lifecycle

```text
Concept
  → Discovery interview
  → Draft discovery package
      ├─ decisions and open questions
      ├─ draft Spec or Specs
      ├─ screen mockups or prototype
      └─ proposed delivery breakdown
  → Human review and revision
  → Approved Specs
  → Approved plan and synchronized issues
  → Approved Tasks
  → Draft implementation PRs
  → Human review, playtest, merge, and release
```

No downstream phase is authorized by an upstream draft. Silence is never
approval.

## 3. Interaction surfaces

| Surface | Use |
|---|---|
| VS Code Chat — Discovery agent | Live interview; one question at a time |
| VS Code Chat — Spec Prototyper | Draft Specs, mockups, and prototypes |
| VS Code Chat — Delivery Planner | Work breakdown and impact assessment |
| VS Code Chat — SDLC Engineer | Local implementation of one approved Task |
| GitHub Concept issue | Durable discovery thread and approval target |
| Draft discovery PR | Review and revision of Specs/prototypes |
| GitHub Task issue | Approved implementation boundary |
| Draft implementation PR | Code review and evidence |
| GitHub Actions SDLC harness | Asynchronous triage, revisions, planning, and implementation |

The VS Code Agents window and main Chat view use the same agent sessions.
GitHub remains authoritative even when discovery occurs in VS Code.

## 4. Roles

| Role | Agent/human responsibility |
|---|---|
| Product owner/approver | Human confirms decisions, priorities, Specs, plans, merges, and releases |
| Discovery facilitator | Agent challenges ambiguity and records confirmed decisions |
| Game/product designer | Agent proposes; human decides mechanics, tuning, flows, and presentation |
| Spec author | Agent writes coherent, testable draft Specs |
| Prototype designer | Agent creates reviewable SVG, HTML/CSS, or isolated Phaser artifacts |
| Producer/planner | Agent proposes hierarchy, dependencies, milestones, and impact |
| Programmer | Agent implements one approved Task |
| QA/playtester | Agent runs automation and writes checklists; human observes gameplay |
| Pixel artist/audio designer | Agent writes briefs and placeholders; finished assets require suitable tools and human review |

The GitHub Actions harness is one orchestration agent using scoped tools. The
VS Code custom-agent profiles provide focused interactive roles.

## 5. Durable artifacts and ownership

| Information | Canonical source |
|---|---|
| Product intent | `docs/plans/concept.md` |
| Confirmed discovery decisions | `docs/discovery/<concept>/decisions.md` |
| Requirements and acceptance criteria | `docs/specs/*.md` |
| Artifact IDs and relationships | `docs/sdlc/manifest.json` |
| Approved artifact fingerprints | `docs/sdlc/state.json` |
| Discussion and requested changes | GitHub comments and reviews |
| Workflow state | GitHub `status:*` labels |
| Implementation scope | Task issue plus parent Spec |
| Implementation evidence | Pull requests and CI |

Generated GitHub issue blocks are mirrors. Humans edit the canonical artifact or
manifest, not the marker-delimited block.

## 6. Concept discovery

### 6.1 Starting discovery

Open a `type:concept` issue and link `docs/plans/concept.md`, or select the
Discovery agent in VS Code and request:

> Interview me about `docs/plans/concept.md`. Ask one question at a time,
> challenge assumptions, and record only confirmed decisions.

Concept submission authorizes draft artifacts under:

- `docs/discovery/`
- `docs/specs/`
- `docs/mockups/`
- `prototypes/`
- `docs/sdlc/`

It does not authorize production gameplay changes.

### 6.2 Interview protocol

The Discovery agent:

1. Reads the Concept, repository, existing Specs, and constraints.
2. Asks one focused question.
3. Restates the proposed decision.
4. Records it only after confirmation.
5. Keeps assumptions and open questions separate.
6. Challenges contradictions, untestable language, hidden dependencies, and
   premature solutions.
7. Stops only when the core experience and each intended Spec outcome can be
   explained and verified.

### 6.3 Discovery package

The agent creates or updates:

```text
docs/discovery/<concept>/
├── decisions.md
├── assumptions.md
└── open-questions.md

docs/specs/*.md
docs/mockups/*
prototypes/*
```

It chooses one Spec or several coherent Specs based on independently reviewable
outcomes, not document size.

Prototypes are non-production evidence. They must include launch and review
instructions. Prototype shortcuts are not requirements.

## 7. Review and approval

The agent uses one deterministic branch and draft PR:

```text
agent/discovery-<concept-issue>-<slug>
```

Ordinary PR comments are discussion. An approver starts a comment or review
with `/revise` to authorize updating the discovery package. The agent updates
the same branch and PR idempotently.

When ready, the agent posts a proposal marker on the Concept issue:

```text
<!-- sdlc-agent:proposal:<stable-id> -->
```

The human adds `approve:spec`. A later run records and consumes that exact
approval. The human reviews and merges the discovery PR.

## 8. Planning and work hierarchy

Default:

```text
Concept → Spec → Task → Pull Request
```

Expanded only when useful:

```text
Concept → Spec → Epic → Feature → Task → Pull Request
```

Use an Epic for multiple independently valuable Features. Use a Feature for
multiple independently reviewable Tasks. Each Task maps to at most one
implementation PR.

After Spec approval:

1. The agent proposes the hierarchy with a proposal ID.
2. The human adds `approve:plan`.
3. The agent records the approved plan.
4. The agent proposes the exact issue set.
5. The human adds `approve:create-issues`.
6. The agent creates/reuses issues using deterministic markers.
7. Each Task receives its own `approve:implement`.

## 9. Upstream changes and impact

Every tracked artifact has a stable ID in `docs/sdlc/manifest.json`. The
traceability script stores approved fingerprints in `docs/sdlc/state.json`.

When an upstream file, relationship, status, or issue link changes:

1. `traceability.py impact` identifies changed artifacts and descendants.
2. The agent reads the semantic change.
3. Each descendant is classified:
   - `unaffected`
   - `needs-clarification`
   - `needs-revision`
   - `obsolete`
   - `new-work`
4. The agent posts one idempotent impact report.
5. Affected work moves to `status:needs-review` when appropriate.
6. Approved downstream artifacts are not automatically rewritten or closed.
7. After human-approved revisions, the snapshot and managed issue blocks are
   refreshed.

Scripts determine graph mechanics and drift. The model assesses meaning.

## 10. Labels

### Types

`type:concept`, `type:spec`, `type:epic`, `type:feature`, `type:task`,
`type:bug`, `type:chore`, `type:research`

### Status

`status:proposed`, `status:needs-review`, `status:triaged`, `status:ready`,
`status:in-progress`, `status:in-review`, `status:playtest`, `status:done`,
`status:blocked`

Only one primary status label may be present.

### Approval

`approve:spec`, `approve:plan`, `approve:create-issues`,
`approve:implement`, `approve:revise`, `approve:close`

Approval labels are single-use capabilities tied to an exact proposal marker
and approved actor.

### Taxonomy and provenance

Area, discipline, and severity labels are defined in
`agents/sdlc_agent/config.py`. `agent:generated` is applied only to
agent-created issues and PRs.

Run the manual `SDLC Bootstrap` workflow once to create/update labels and create
missing milestones.

## 11. Tool and branch boundaries

Read tools may inspect repository files, search text, read issues/PRs/checks,
and validate traceability.

Discovery writes require a Concept event or approver `/revise` and are restricted
to discovery roots. Implementation writes require `approve:implement` or
`approve:revise`, a deterministic `agent/task-<issue>-<slug>` branch, allowed
paths, and expected file SHAs.

The agent cannot modify its workflows, instructions, permissions, dependencies,
lockfiles, or synchronization scripts.

It never merges, writes directly to `main`, force-pushes, or deletes branches.

## 12. Idempotency and concurrency

Generated resources contain:

```text
<!-- sdlc-agent:<operation>:<subject>:<proposal-id> -->
```

The agent reuses matching branches, comments, issues, and PRs. GitHub workflows
serialize by issue or PR number. File updates require expected SHAs.

GitHub generally suppresses workflow runs caused by `GITHUB_TOKEN`. Each phase
therefore begins from an explicit human event, manual dispatch, or bounded
continuation; no phase depends on an agent-authored event retriggering Actions.

## 13. Validation and CI

`CI / check` runs:

```text
npm ci
npm run typecheck
npm run build
```

`SDLC Traceability / traceability` validates the graph, reports impact, checks
the committed snapshot, and checks managed issue metadata.

There is no lint or test script until an approved Task adds them. Do not require
nonexistent check names in branch rules.

## 14. Definition of Done

A Task is done only when:

- It implements one approved Task and parent Spec.
- Acceptance criteria map to evidence.
- Traceability is current.
- Clean install, typecheck, and build pass.
- Relevant tests pass once tests exist.
- Visual/gameplay work has completed human review or playtest evidence.
- CI passes on the final commit.
- The human approves and merges.
- Durable artifact and issue state is updated.

## 15. Rollout

1. Install the repository files and rebuild the dev container.
2. Run `DeepSeek: Set API Key` in VS Code.
3. Run `SDLC Bootstrap` with preview, then `apply: true`.
4. Add `DEEPSEEK_API_KEY` to Actions secrets.
5. Add `SDLC_AGENT_ENABLED=true` to Actions variables.
6. Run a manual SDLC Agent dry run.
7. Conduct one VS Code discovery interview.
8. Generate one discovery package and draft PR.
9. Exercise `/revise` and `approve:spec`.
10. Validate plan/issue synchronization.
11. Enable implementation on one bounded Task.

Before live implementation, verify Agent Framework imports, DeepSeek tool
calling, iteration behavior, dry-run enforcement, approval consumption,
expected-SHA conflicts, and duplicate-event handling.
