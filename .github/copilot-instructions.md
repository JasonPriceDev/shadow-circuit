# Copilot Instructions — Shadow Circuit

Shadow Circuit is a Phaser 4.2.1, TypeScript 5.9.3, Vite 6.4.3 browser
platformer using Arcade Physics. DeepSeek V4 Pro is the primary model.

Follow `AGENTS.md` and applicable `.github/instructions/*.instructions.md`
files. For nontrivial work, read the approved Spec/Task and
`docs/plans/agent-tech-stack.md`.

Key facts:

- Canvas: `960 × 540`; gravity: `{ x: 0, y: 1000 }`; Vite base: `./`.
- First milestone: Lantern Rooftops, three enemy archetypes, Iron Crane.
- `src/config/GameConfig.ts`: dimensions, physics, scenes.
- `src/levels/StageCatalog.ts`: canonical stages, bosses, lessons, unlocks.
- `docs/plans/concept.md`: product intent; optional ideas are not scope.
- `docs/plans/agentic-sdlc-workflow.md`: approval and PR policy.

Known hazards: continuous collider damage, frame-dependent attacks, stale scene
state, competing scene transitions, scaled static bodies without
`refreshBody()`, and runtime/UI input mismatch. The defect list is in
`docs/plans/agent-tech-stack.md`; listing a defect does not authorize a fix.

Make the smallest scoped change. Validate with `npm run typecheck` and
`npm run build`. Do not claim gameplay was tested unless it was played.