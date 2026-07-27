# Copilot Instructions for Shadow Circuit

You are assisting with **Shadow Circuit**, a browser-based 8-bit martial arts platformer built with Phaser 4, TypeScript, Vite, and Arcade Physics.

## Project Identity

- **Game**: Shadow Circuit — Kai, a courier-monk, fights through 8 districts controlled by warlords
- **Stage 1**: Lantern Rooftops → Iron Crane boss
- **Canvas**: 960×540, pixel-art scaling (`pixelArt: true`)
- **Physics**: Arcade Physics, gravity `{x: 0, y: 1000}`
- **Scene order**: Boot → Preload → Title → Stage → Boss → GameOver
- **Base path**: `./` (relative, for static hosting)

## TypeScript Conventions

```typescript
// ✅ DO
import Phaser from "phaser";
import { Player } from "../actors/Player";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";

export class MyScene extends Phaser.Scene {
  private myField!: Type;

  constructor() {
    super("MyScene");
  }

  create(): void { }
  update(): void { }
}
```

- **PascalCase** classes and files (e.g. `IronCrane.ts` exports `class IronCrane`)
- **Named exports only**, no `export default`
- **Relative imports** without `.ts` extension: `from "../actors/Player"`
- **Double quotes**, **semicolons**, **trailing commas**
- **Strict TypeScript**: all types explicit, no implicit `any`
- Use `!` (definite assignment) for fields initialized in `create()`: `private player!: Player;`
- `tsconfig.json` is strict, `ES2022` target, `Bundler` resolution, `noEmit`

## Phaser Scene Lifecycle

```typescript
export class ExampleScene extends Phaser.Scene {
  constructor() {
    super("ExampleScene"); // key must match GameConfig scene list
  }

  create(): void {
    // Set up game objects, physics, input, cameras
    // This runs ONCE when the scene starts
  }

  update(): void {
    // Runs every frame — keep it lean
    // Move actors, check win/lose conditions
  }
}
```

- **Never** start timers or add event listeners outside `create()` — they survive scene shutdown
- **Always** use `this.input.keyboard?.once(...)` for one-shot listeners (ENTER to start, etc.)
- **Never** use `scene.restart()` without resetting scene-run state in `init()` or `create()`
- Scene transitions: `this.scene.start("NextScene", { optionalData })`

## Physics Patterns

### Adding physics to an actor

```typescript
export class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, "texture-key");
    scene.add.existing(this);        // add to display list
    scene.physics.add.existing(this); // add to physics world
    this.setCollideWorldBounds(true);
  }
}
```

- Use `this.body as Phaser.Physics.Arcade.Body` to access velocity, `blocked.down`, etc.
- Use `body.setVelocityX()` / `body.setVelocityY()` — **never** set `x`/`y` directly for physics objects
- Set origin to bottom-center for platformer characters: `this.setOrigin(0.5, 1);`

### Collisions

```typescript
// Static group for platforms — call refreshBody() after scaling
const floor = this.physics.add.staticImage(x, y, "key");
floor.setScale(15, 1).refreshBody();

// Dynamic collisions
this.physics.add.collider(player, enemies, () => {
  // ⚠️ This fires EVERY physics step while overlapping
  // Always add a cooldown or invulnerability window
});
```

- Static groups use `this.physics.add.staticGroup()`
- Dynamic groups use `this.physics.add.group()`

### Camera

```typescript
this.cameras.main.setBounds(0, 0, levelWidth, GAME_HEIGHT);
this.cameras.main.startFollow(player, true, 0.08, 0.08);
```

## Texture Generation (Placeholder)

```typescript
// In BootScene.create():
private createTexture(key: string, w: number, h: number, color: number): void {
  const gfx = this.make.graphics({ x: 0, y: 0 });
  gfx.fillStyle(color, 1);
  gfx.fillRect(0, 0, w, h);
  gfx.generateTexture(key, w, h);
  gfx.destroy();
}
```

Current placeholder textures: `player-placeholder` (28×40, yellow), `enemy-placeholder` (28×36, red), `boss-placeholder` (64×80, purple), `platform-placeholder` (64×16, teal).

## Component Patterns

### Health

```typescript
import { Health } from "../components/Health";
// Constructor: new Health(maximum, current?)
// Methods: .damage(amount), .isDepleted(), .value
// Clamps at 0 — never goes negative
```

### State Machine

```typescript
import { StateMachine } from "../components/StateMachine";
// new StateMachine<StateUnion>("initialState")
// .transition("newState") — call from updateBehavior()
```

### Input System

```typescript
import { InputSystem, InputState } from "../systems/InputSystem";
// Reads cursor keys + SPACE + X
// Returns { left, right, jump, attack } booleans
// ⚠️ Does NOT register WASD despite UI text — only arrows work
```

## File Organization

```
src/
├── main.ts              # Creates Phaser.Game with gameConfig
├── config/GameConfig.ts # Game dimensions, Phaser config, scene list
├── scenes/              # Boot → Preload → Title → Stage → Boss → GameOver
├── actors/              # Player, Enemy, Boss (base)
├── bosses/              # IronCrane, ForemanBrass, ... (subclass Boss)
├── components/          # Health, Hitbox, StateMachine
├── systems/             # InputSystem, CombatSystem, AnimationSystem, SaveSystem
└── levels/              # Tiled JSON + StageCatalog.ts
```

## ⚠️ Known Anti-Patterns (AVOID)

1. **Contact damage without cooldown** — `damage(1)` in a collider callback fires every physics step. Always add invulnerability frames gated by simulation time.
2. **Frame-dependent damage** — `if (isAttacking()) boss.damage(1)` in `update()` hits every render frame. Use physics hitboxes with one-hit-per-swing gating.
3. **Scene state not reset on entry** — flags set in `create()` survive scene stop/start. Reset run-state in `init()` or at the top of `create()`.
4. **Multiple scene transitions in one update** — evaluating win AND lose in the same `update()` can queue two `scene.start()` calls. Check conditions once and return immediately.
5. **Missing `refreshBody()` after scaling** — static bodies must call `.refreshBody()` after `.setScale()`.
6. **Direct position manipulation** — use `setVelocity` on physics bodies, not `x =` / `y =`.
7. **Duplicate event listeners** — use `.once()` for one-shot input, never `.on()` without corresponding `.off()` in `shutdown`.

## Build Commands

```bash
npm run dev       # Vite dev server on http://localhost:5173
npm run typecheck # tsc --noEmit (strict)
npm run build     # tsc --noEmit && vite build → dist/
npm run preview   # Serve dist/ locally
```

## When Writing New Code

- Match existing patterns: look at `StageScene.ts` for stage layout, `BossScene.ts` for boss encounters, `Player.ts` for actor setup
- Read `src/config/GameConfig.ts` for dimensions before hardcoding numbers
- Read `src/levels/StageCatalog.ts` for stage/boss/unlock data
- Read `docs/plans/concept.md` for design intent before implementing mechanics
- Run `npm run typecheck` after changes — strict mode catches a lot
