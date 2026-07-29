---
applyTo: "src/**/*.ts,vite.config.ts"
---

# TypeScript and Phaser

- Read the Task, Spec, tech-stack reference, and relevant source first.
- Use named exports, relative imports without `.ts`, double quotes, semicolons,
  trailing commas, strict typing, and `PascalCase.ts` class files.
- Use physics velocity for movement and elapsed/simulation time for gameplay.
- Call `refreshBody()` after scaling static bodies.
- Gate contact damage and one-hit-per-swing attacks.
- Reset scene state on entry; clean up persistent listeners and timers.
- Allow one terminal scene transition per update and return after starting it.
- Read `StageCatalog.ts` before changing stages, bosses, lessons, or unlocks.

Damage, timing, tuning, scoring, accessibility, and mechanics require an
approved Spec. Run typecheck and build, then provide focused playtest steps.
