---
applyTo: "src/**/*.ts,vite.config.ts"
---

# TypeScript and Phaser

- Read the Task, Spec, `agent-tech-stack.md`, and relevant source first.
- Use named exports, relative imports without `.ts`, double quotes, semicolons,
  trailing commas, and `PascalCase.ts` class files.
- Keep strict typing; do not use `any` to suppress errors. Prefer inference for
  obvious locals and annotations at boundaries or where needed.
- Use `!` only for fields reliably initialized by lifecycle code.

Scenes:

- Register scenes in `GameConfig.ts`; use unique keys.
- Reset per-run state on every entry.
- Give listeners and timers explicit lifetimes; clean up persistent ones.
- Allow only one terminal transition per update and return after starting it.

Gameplay:

- Use physics velocity for normal movement.
- Use elapsed/simulation time, never render-frame counts, for gameplay timing.
- Call `refreshBody()` after scaling static bodies.
- Assume collision callbacks run every physics step.
- Gate contact damage with invulnerability and attacks with hitboxes plus
  one-hit-per-swing logic.
- Values for damage, timing, phases, scoring, and accessibility require an
  approved Spec.
- Read `StageCatalog.ts` before changing a stage, boss, lesson, or unlock.
- Crouch/duck is an initial action; Shadow Dodge is the Mirror Jack unlock.

Run `npm run typecheck` and `npm run build`. Provide manual playtest steps for
gameplay changes and state when they were not performed.
