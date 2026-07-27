# Shadow Circuit

A browser-based 8-bit martial arts platformer featuring fast-paced combat, retro
pixel art, challenging stages, and unique boss battles.

## Development

The project uses Phaser 4, TypeScript, Vite, Arcade Physics, and Tiled.

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The repository includes a
Dockerfile-based devcontainer with Node.js 22, common development and GitHub
CLI tools, and the recommended editor extensions. It mounts the host's
`~/.ssh` directory read-only at `/home/node/.ssh`:

```bash
code .
# Reopen in Container
```

### DeepSeek model access in Copilot Chat

The devcontainer automatically installs the [DeepSeek V4 for Copilot Chat](https://marketplace.visualstudio.com/items?itemName=vizards.deepseek-v4-for-copilot)
extension, which adds DeepSeek V4 Pro/Flash to the Copilot Chat model picker. The
extension is BYOK (bring your own key) and stores the key in VS Code's OS-level
secret storage, never in a repo file, so it must be set once per environment:

1. Get an API key from [platform.deepseek.com](https://platform.deepseek.com/).
2. Open the Command Palette and run `DeepSeek: Set API Key`, then paste the key.
3. In Copilot Chat, open the model picker and select **DeepSeek V4 Pro** or
   **DeepSeek V4 Flash**.

Re-run step 2 inside each new devcontainer instance, since secret storage does not
persist across container rebuilds.

## Repository layout

```text
src/
├── actors/       # Player, enemies, and shared boss behavior
├── bosses/       # Boss-specific implementations from the concept
├── components/   # Health, hitboxes, and state machines
├── config/       # Phaser game configuration
├── levels/       # Tiled-compatible stage data
├── scenes/       # Boot, title, stage, boss, and game-over flow
└── systems/      # Input, combat, animation, and save systems
public/
├── audio/
├── music/
├── sprites/
└── tilesets/
```

The current vertical slice starts with Lantern Rooftops and transitions to the
Iron Crane boss. Placeholder textures are generated at boot so the gameplay
loop can be developed before art and audio assets are committed.

## Build

```bash
npm run typecheck
npm run build
```
