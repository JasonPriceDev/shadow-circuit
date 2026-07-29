# Agent Tech Stack Reference

Status: **Authoritative implementation constraints**

Last revised: **2026-07-27**

Verification baseline: **Set to the adoption commit SHA.**

## 1. Authority

Approved Specs and recorded decisions define product requirements. This file
defines implementation constraints. Executable source and configuration define
current behavior. If this reference conflicts with executable configuration,
report documentation drift and stop the affected work.

The Concept is upstream intent. A Concept change requires downstream impact
assessment; it does not silently override an approved Spec.

## 2. Runtime versions

| Dependency | Required version/source |
|---|---|
| Phaser | `4.2.1` from `package-lock.json` |
| TypeScript | `5.9.3` from `package-lock.json` |
| Vite | `6.4.3` from `package-lock.json` |
| Node.js | `22` in dev container and CI |
| Python | `3.12` in dev container, agent workflow, and sync workflow |
| Agent Framework Core | `1.11.0` |
| Agent Framework OpenAI | `1.11.0` |
| PyGithub | `2.9.1` |
| python-dotenv | `1.2.2` |

Agent packages are pinned in `agents/requirements.txt`. Upgrade the model,
framework, or packages only through a compatibility PR.

## 3. Local agent environment

`.devcontainer/devcontainer.json` provides Node 22, Python 3.12, GitHub CLI,
Graphviz, Pandoc, validation tools, and VS Code customizations.

`vizards.deepseek-v4-for-copilot` exposes DeepSeek V4 Pro and Flash through the
VS Code model picker. Set its key with `DeepSeek: Set API Key`; do not place the
key in repository settings. DeepSeek V4 Pro is the default agent model and
Flash is the utility model.

The extension and default-model settings are version-sensitive. Confirm the
active model in the picker after VS Code or extension upgrades.

Secrets:

- Local harness: ignored `.env`, loaded only outside GitHub Actions.
- VS Code model provider: VS Code SecretStorage.
- GitHub Actions harness: `DEEPSEEK_API_KEY` secret.
- Never expose an entire host `.ssh` directory inside the container.

## 4. Build and validation

| Command | Meaning |
|---|---|
| `npm ci` | Reproduce the lockfile installation |
| `npm run dev` | Start Vite locally |
| `npm run typecheck` | Run strict `tsc --noEmit` |
| `npm run build` | Typecheck and build production assets |
| `npm run preview` | Serve the production build |
| `python scripts/sdlc/traceability.py validate` | Validate artifact relationships |
| `python scripts/sdlc/traceability.py impact --format markdown` | Report upstream drift and descendants |
| `python scripts/sdlc/sync_issues.py` | Preview managed GitHub issue synchronization |

There is currently no lint or test script. Say those checks are unavailable;
never imply they passed. Adding frameworks or dependencies requires an approved
Task.

## 5. Product runtime configuration

Canonical game configuration is `src/config/GameConfig.ts`:

```typescript
export const GAME_WIDTH = 960;
export const GAME_HEIGHT = 540;

export const gameConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  parent: "game",
  width: GAME_WIDTH,
  height: GAME_HEIGHT,
  backgroundColor: "#101426",
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  physics: {
    default: "arcade",
    arcade: {
      gravity: { x: 0, y: 1000 },
      debug: false,
    },
  },
};
```

Vite uses base `./`. `src/levels/StageCatalog.ts` is canonical for stages,
bosses, lessons, and unlocks.

## 6. TypeScript conventions

- `PascalCase.ts` matching the primary class.
- Named exports and relative imports without `.ts`.
- Double quotes, semicolons, and trailing commas.
- TypeScript `strict: true`; do not use `any` to suppress errors.
- Use definite assignment only for fields reliably initialized by lifecycle
  code.
- Use simulation time, elapsed time, or physics velocity; never frame counts.
- Do not introduce a formatter, state library, or architectural convention
  without approved scope.

## 7. Phaser rules

- Reset per-run scene state on each entry.
- Give listeners and timers explicit lifetimes.
- Permit one terminal scene transition per update; return after starting it.
- Call `refreshBody()` after scaling static bodies.
- Treat collision callbacks as continuous.
- Gate contact damage with invulnerability/cooldown behavior defined by a Spec.
- Gate attacks with hitboxes and one-hit-per-swing logic.
- Use world and camera bounds deliberately.
- Mechanics, timing, damage, scoring, accessibility, and tuning require
  approved acceptance criteria.

## 8. Discovery and prototype stack

Discovery artifacts may use:

- Markdown for decisions and Specs.
- Mermaid or Graphviz for flows and relationships.
- SVG for reviewable screen mockups.
- HTML/CSS/TypeScript for small interactive mockups.
- Isolated Phaser code when timing or interaction must be demonstrated.

Prototype locations are `docs/mockups/` and `prototypes/`. They are
non-production, must include launch/review instructions, and may not introduce
dependencies without approval. Prototype code is evidence, not an
implementation shortcut.

DeepSeek V4 is text-only. The VS Code extension may proxy image understanding
through an available vision model, but raster generation is not part of the
GitHub Actions harness.

## 9. Agent architecture

Interactive VS Code roles:

- Discovery
- Spec Prototyper
- Delivery Planner
- SDLC Engineer

On-demand skills:

- `$discover-concept`
- `$sync-sdlc`

The Actions runtime creates one `sdlc-agent` using
`OpenAIChatCompletionClient`:

```python
client = OpenAIChatCompletionClient(
    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)
```

The harness disables direct file access and web search. It uses validated tools
for repository reads, GitHub operations, discovery writes, implementation
writes, traceability, and fixed validation commands.

## 10. Authorization boundaries

Concept submission authorizes draft files only on
`agent/discovery-<issue>-<slug>` and only under:

- `docs/discovery/`
- `docs/specs/`
- `docs/mockups/`
- `prototypes/`
- `docs/sdlc/`

An approver `/revise` comment authorizes updates to that discovery package.

Production files require `approve:implement` or `approve:revise`, an
`agent/task-<issue>-<slug>` branch, and expected file SHAs.

The agent denies changes to its container, workflows, instructions, agents,
skills, policy, dependencies, lockfiles, and SDLC scripts.

## 11. Traceability and synchronization

`docs/sdlc/manifest.json` uses:

```json
{
  "id": "SPEC-core-gameplay",
  "kind": "spec",
  "path": "docs/specs/core-gameplay.md",
  "status": "draft",
  "upstream": ["CONCEPT-shadow-circuit"],
  "github_issue": 42
}
```

IDs are stable uppercase identifiers. Paths are repository-relative. Upstream
IDs must exist and the graph must be acyclic.

`state.json` stores approved hashes and metadata. `sync_issues.py` may update
only its marker-delimited issue block and the mapped `status:*` label.
Application requires an explicit approval environment variable. Scripts never
close issues or rewrite requirements.

## 12. Known implementation hazards

Before planning relevant changes, inspect for:

- Continuous collider damage.
- Frame-dependent attacks or cooldowns.
- State persisting across scene restarts.
- Competing scene transitions.
- Scaled static bodies without `refreshBody()`.
- Runtime/UI input mismatch.
- Stage or unlock duplication outside `StageCatalog.ts`.

This list is orientation, not authorization to fix unrelated defects.

## 13. Required compatibility checks

Before live implementation, verify:

- Python 3.12 imports against pinned packages.
- DeepSeek Chat Completions tool calling.
- Supported thinking/reasoning parameters.
- Harness todo looping and iteration caps.
- Dry-run enforcement in every mutation tool.
- Approval actors, labels, proposal markers, and consumption.
- Discovery path and branch restrictions.
- Expected-SHA conflicts and duplicate-event idempotency.
- Traceability validation, drift, cycles, and issue-block replacement.
- Secret redaction and fork behavior.
