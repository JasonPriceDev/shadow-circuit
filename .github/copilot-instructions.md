# Shadow Circuit

Follow `AGENTS.md` and applicable `.github/instructions/*.instructions.md`.

Shadow Circuit is a Phaser 4.2.1, TypeScript 5.9.3, Vite 6.4.3 browser
platformer using Arcade Physics. DeepSeek V4 Pro is the primary model.

- Canvas: `960 × 540`; gravity: `{ x: 0, y: 1000 }`; Vite base: `./`.
- `src/config/GameConfig.ts` owns dimensions, physics, and scene registration.
- `src/levels/StageCatalog.ts` owns stages, bosses, lessons, and unlocks.
- `docs/plans/concept.md` is upstream product intent.
- `docs/plans/agent-tech-stack.md` is the implementation reference.
- `docs/plans/agentic-sdlc-workflow.md` defines discovery, approvals, and PRs.

Make the smallest authorized change. Use project skills for discovery and SDLC
synchronization. Do not turn brainstorming or prototype code into approved
production scope.
