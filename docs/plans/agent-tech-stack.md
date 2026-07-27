# Agent Tech Stack Reference

Status: **Authoritative**. This document is the canonical technical reference for any AI agent (Copilot, SDLC harness agent, future agents) working in this repository. It is structured for machine consumption — short sections, exact values, and unambiguous rules.

## 1. Runtime Versions

| Dependency | Version | Notes |
|---|---|---|
| Phaser | `4.2.1` | Arcade Physics enabled |
| TypeScript | `5.9.3` | Strict mode, ES2022 target |
| Vite | `6.4.3` | Dev server + production bundler |
| Node.js | `22` (Bookworm) | Devcontainer base image |
| npm | Lockfile present (`package-lock.json`) | Use `npm ci` for reproducible installs |

## 2. Build & Validation

| Command | What it does | Agent use |
|---|---|---|
| `npm ci` | Clean install from lockfile | Run first in any CI/agent workflow |
| `npm run dev` | Vite dev server on `0.0.0.0:5173` | Local development only |
| `npm run typecheck` | `tsc --noEmit` — strict TypeScript check | **Always run before claiming code compiles** |
| `npm run build` | `tsc --noEmit && vite build` → `dist/` | **Always run before claiming code builds** |
| `npm run preview` | Serve `dist/` locally on `0.0.0.0:4173` | Verify production build |

There is currently **no** `lint` or `test` script. These must be added (see plan §12.2).

## 3. Phaser Configuration

```typescript
// src/config/GameConfig.ts — canonical values
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
  scene: [
    BootScene,
    PreloadScene,
    TitleScene,
    StageScene,
    BossScene,
    GameOverScene,
  ],
};
```

### Scene flow

```
BootScene → PreloadScene → TitleScene → StageScene → BossScene
                ↑              ↑             ↓             │
                │              └── GameOverScene ←─────────┘
                │                                             │
                └─────────────────────────────────────────────┘ (win)
```

- Boot: generates placeholder textures, chains to Preload
- Preload: placeholder — immediately chains to Title
- Title: ENTER or click → StageScene
- Stage: walk right past x=1200 → BossScene; health=0 → GameOverScene
- Boss: boss health=0 → TitleScene; player health=0 → GameOverScene
- GameOver: ENTER → TitleScene

## 4. TypeScript Conventions (Exact)

```typescript
// ✅ Imports
import Phaser from "phaser";
import { Player } from "../actors/Player";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";

// ✅ Exports
export class MyClass { }      // Named only — never `export default`

// ✅ Classes
export class MyScene extends Phaser.Scene {
  private field!: Type;       // ! for fields set in create()
  constructor() { super("MyScene"); }
  create(): void { }          // Scene setup
  update(): void { }          // Per-frame logic
}
```

| Rule | Value |
|---|---|
| File naming | `PascalCase.ts` matching class name |
| Quote style | Double quotes |
| Semicolons | Required |
| Trailing commas | Yes |
| Import style | Relative, no `.ts` extension |
| Export style | Named exports only |
| Type strictness | `strict: true` in tsconfig |
| Definite assignment | `!` for fields set outside constructor |

## 5. Project Structure Map

```text
src/
├── main.ts                     # new Phaser.Game(gameConfig)
├── config/GameConfig.ts        # Dimensions, Phaser config, scene array
├── scenes/
│   ├── BootScene.ts            # generateTexture() placeholders → PreloadScene
│   ├── PreloadScene.ts         # Placeholder → TitleScene
│   ├── TitleScene.ts           # ENTER/click → StageScene
│   ├── StageScene.ts           # Hardcoded Lantern Rooftops, 2 enemies, x>1200→Boss
│   ├── BossScene.ts            # IronCrane boss, X to attack, win→Title, lose→GameOver
│   └── GameOverScene.ts        # ENTER → TitleScene
├── actors/
│   ├── Player.ts               # extends Arcade.Sprite, Health(5), velocity movement
│   ├── Enemy.ts                # extends Arcade.Sprite, Health(2), no AI yet
│   └── Boss.ts                 # extends Arcade.Sprite, StateMachine, Health, chase AI
├── bosses/
│   ├── IronCrane.ts            # Health(8), extends Boss
│   ├── ForemanBrass.ts         # Health(10)
│   ├── MireQueen.ts            # Health(10)
│   ├── MirrorJack.ts           # Health(10)
│   ├── GeneralTanuki.ts        # Health(10)
│   ├── SisterAurora.ts         # Health(10)
│   ├── Raijin9.ts              # Health(10)
│   └── EmperorNull.ts          # Health(16)
├── components/
│   ├── Health.ts               # .damage(n), .isDepleted(), .value — clamps at 0
│   ├── Hitbox.ts               # Interface only — no runtime consumer
│   └── StateMachine.ts         # Generic <T>, .transition(state)
├── systems/
│   ├── InputSystem.ts          # Cursor keys + SPACE + X — NO WASD
│   ├── CombatSystem.ts         # Static basicAttack — not wired to gameplay
│   ├── AnimationSystem.ts      # Placeholder class
│   └── SaveSystem.ts           # localStorage get/set — not wired to gameplay
└── levels/
    ├── StageCatalog.ts         # Array of 8 StageDefinition objects
    ├── stage-01.json           # Tiled map: empty tiles, player-start + iron-crane objects
    └── stage-02.json           # Tiled map: empty shell

public/
├── audio/.gitkeep
├── music/.gitkeep
├── sprites/.gitkeep
└── tilesets/.gitkeep
```

## 6. Physics Patterns (Exact)

### Actor Setup

```typescript
export class Player extends Phaser.Physics.Arcade.Sprite {
  readonly health = new Health(5);

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, "player-placeholder");
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
    this.setOrigin(0.5, 1);  // Bottom-center for platformers
  }
}
```

### Movement (velocity-based, NOT frame-dependent)

```typescript
const body = this.body as Phaser.Physics.Arcade.Body;
const speed = 220;
body.setVelocityX((Number(input.right) - Number(input.left)) * speed);

if (input.jump && body.blocked.down) {
  body.setVelocityY(-470);
}
```

### Platforms & Colliders

```typescript
// Static group
this.platforms = this.physics.add.staticGroup();
this.platforms.create(x, y, "platform-placeholder");

// Scaled static body — MUST refresh
const floor = this.physics.add.staticImage(x, y, "key");
floor.setScale(15, 1).refreshBody();

// Dynamic collider
this.physics.add.collider(player, group);
this.physics.add.collider(player, enemies, callback);
```

### World Bounds & Camera

```typescript
this.physics.world.setBounds(0, 0, 1600, GAME_HEIGHT);
this.cameras.main.setBounds(0, 0, 1600, GAME_HEIGHT);
this.cameras.main.startFollow(player, true, 0.08, 0.08);
```

## 7. Texture Keys (BootScene Placeholders)

| Key | Width | Height | Color | Used by |
|---|---|---|---|---|
| `player-placeholder` | 28 | 40 | `0xffd166` (yellow) | Player |
| `enemy-placeholder` | 28 | 36 | `0xef476f` (red) | Enemy |
| `boss-placeholder` | 64 | 80 | `0x9b5de5` (purple) | Boss |
| `platform-placeholder` | 64 | 16 | `0x3f8f8c` (teal) | Stage/Boss floors |

Generated in `BootScene.createTexture()` using `this.make.graphics()`. Generated textures are available before any dependent scene starts.

## 8. Stage Catalog (Canonical Data)

From `src/levels/StageCatalog.ts`:

| id | Name | Boss | Lesson | Unlocks |
|---|---|---|---|---|
| stage-01 | Lantern Rooftops | Iron Crane | Jump, duck, recognize attack ranges | Flying kick |
| stage-02 | Clockwork Foundry | Foreman Brass | Use environment during combat | Charged punch |
| stage-03 | Flooded Catacombs | Mire Queen | Watch environmental clues | Water dash |
| stage-04 | Neon Market | Mirror Jack | Observation, not constant attacking | Shadow dodge |
| stage-05 | Bamboo Fortress | General Tanuki | Multi-phase boss battles | Smoke bomb |
| stage-06 | Frozen Observatory | Sister Aurora | Movement control, pattern recognition | Wall cling |
| stage-07 | Storm Temple | Raijin-9 | Defensive timing, parrying | Projectile deflection |
| stage-08 | The Shadow Citadel | Emperor Null | Mastery of entire game | — |

## 9. Boss State Machine

From `src/components/StateMachine.ts` with states defined in `src/actors/Boss.ts`:

```
intro → idle → telegraph → attack → recovery → idle
                              ↘ stunned → idle
                              ↘ phaseChange → idle
                              ↘ defeated (terminal)
```

The base `Boss.updateBehavior(player)` currently:
1. Reads direction toward player: `Math.sign(player.x - this.x)`
2. Sets velocity: `direction * 50`
3. Transitions to `idle` (no states are actually implemented)

Each boss subclass in `src/bosses/` should override `updateBehavior()` with state-specific logic.

## 10. Known Defects (Review-Aware)

These are confirmed bugs from the prior code review. Any agent generating or reviewing code in these areas must account for them.

| # | File | Line(s) | Defect | Severity |
|---|---|---|---|---|
| 1 | `StageScene.ts` | 31-34 | Contact damage fires every physics step — no invulnerability cooldown | Major |
| 2 | `BossScene.ts` | 42-45 | Same contact-damage issue | Major |
| 3 | `BossScene.ts` | 51-57 | Boss damage is global and frame-dependent — no hitbox, range, or facing check | Major |
| 4 | `StageScene.ts` | 11, 52-55 | `stageComplete` survives scene reuse — stage cannot reach boss on replay | Major |
| 5 | `StageScene.ts` | 52-59 | Boss and game-over transitions can fire in same update | Medium |
| 6 | `InputSystem.ts` | 10-21 | Only registers arrows, Space, X — not WASD as UI advertises | Minor |

## 11. Key File Index

| File | Role | Read when... |
|---|---|---|
| `src/config/GameConfig.ts` | Dimensions, Phaser config, scene list | Any layout, sizing, or scene work |
| `src/levels/StageCatalog.ts` | Stage/boss/unlock data | Planning stage or boss work |
| `docs/plans/concept.md` | Game design document | Understanding mechanics, boss patterns, visual direction |
| `docs/plans/tech-stack.md` | Engineering rationale | Understanding why Phaser/Vite/Tiled were chosen |
| `docs/plans/agentic-sdlc-workflow.md` | SDLC process definition | Understanding the issue/PR workflow |
| `docs/plans/agent-tech-stack.md` | This file | Any agent orientation |
| `.github/copilot-instructions.md` | In-editor coding conventions | Copilot-assisted coding |
| `agents/sdlc_agent/instructions.py` | SDLC harness agent prompt | SDLC agent behavior |
| `tsconfig.json` | TypeScript strict settings | Type errors, compilation |
| `vite.config.ts` | Dev server port, base path | Build/serve issues |
| `package.json` | Scripts and dependencies | Install, build, typecheck |
| `package-lock.json` | Reproducible dependency versions | CI installation |

## 12. Vite Configuration

```typescript
// vite.config.ts
export default defineConfig({
  base: "./",               // Relative paths for static hosting
  server: {
    host: "0.0.0.0",       // Accessible from devcontainer port forwarding
    port: 5173,
  },
});
```

## 13. Devcontainer

- Base: `mcr.microsoft.com/vscode/devcontainers/typescript-node:1-22-bookworm`
- Remote user: `node`
- Ports forwarded: `5173` (Vite dev server)
- SSH: host `~/.ssh` mounted read-only at `/home/node/.ssh`
- Env: `.env` file required (ignored by git)
- Post-create: `scripts/post-create.sh` — configures git identity + `npm ci`
- Extensions: ESLint, Prettier, DeepSeek V4 for Copilot Chat
