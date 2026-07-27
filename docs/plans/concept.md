## Core concept: *Shadow Circuit*

You play **Kai**, a courier-monk whose city has been taken over by eight warlords. Each warlord controls a district and possesses part of an ancient machine called the Shadow Circuit.

The player runs, jumps, climbs, dodges traps, collects keys, and fights enemies using simple martial-arts attacks. Every stage ends with a distinctive boss battle.

### Core controls

Keep the controls simple enough for keyboards, controllers, and touchscreens:

- Move left/right
- Jump
- Attack
- Crouch or dodge
- Optional secondary move activated by attack combinations

Possible attacks:

- Standing punch
- Flying kick
- Crouching sweep
- Wall kick
- Downward strike
- Deflect or parry

The depth should come from timing and enemy behaviour rather than complicated button combinations.

## Stage ideas and bosses

### 1. Lantern Rooftops

A nighttime district filled with tiled roofs, hanging signs, chimneys, and collapsing platforms.

**Boss: The Iron Crane**

A masked fighter who uses long-reaching kicks and leaps between platforms. During the second phase, he cuts the ropes holding the lanterns, causing burning obstacles to fall.

**Player lesson:** jumping, ducking, and recognizing attack ranges.

---

### 2. Clockwork Foundry

Conveyor belts, crushers, furnaces, steam vents, and moving gears.

**Boss: Foreman Brass**

A huge mechanical brawler with replaceable arms. One arm punches, another fires rivets, and another acts as a shield. The player must trick him into striking machinery that damages his armour.

**Player lesson:** using the environment during combat.

---

### 3. Flooded Catacombs

Underground chambers with rising water, rafts, crumbling bridges, and creatures hiding below the surface.

**Boss: The Mire Queen**

A serpent-like guardian who disappears beneath the water. Ripples reveal where she will emerge. As the fight continues, the water level rises and reduces the safe area.

**Player lesson:** watching environmental clues.

---

### 4. Neon Market

A crowded cyberpunk market with moving carts, elevators, electric signs, and enemies hiding among civilians.

**Boss: Mirror Jack**

A shapeshifter who creates copies of himself. The real boss casts a slightly different shadow or reacts differently when the player moves.

**Player lesson:** observation rather than constant attacking.

---

### 5. Bamboo Fortress

A forest stage with swinging bamboo, rope bridges, falling logs, and hidden archers.

**Boss: General Tanuki**

A small but cunning commander who rides a giant armoured boar. First, the player avoids charges and removes the boar’s armour. Then the general fights directly using smoke bombs and traps.

**Player lesson:** multi-phase boss battles.

---

### 6. Frozen Observatory

Slippery floors, rotating telescopes, falling icicles, low gravity chambers, and freezing wind.

**Boss: Sister Aurora**

A warrior who creates ice clones and freezes sections of the floor. Her attacks synchronize with constellations visible through the observatory roof.

**Player lesson:** movement control and pattern recognition.

---

### 7. Storm Temple

A vertical climb through a temple struck by lightning. Platforms rotate, bells swing, and strong winds affect jumps.

**Boss: Raijin-9**

An ancient thunder guardian. Lightning travels through metal floors, forcing the player to jump onto wooden platforms. Successful parries redirect electrical projectiles back at the boss.

**Player lesson:** defensive timing and parrying.

---

### 8. The Shadow Citadel

A final fortress combining mechanics from every previous level.

**Boss: Emperor Null**

The emperor uses stolen techniques from all seven bosses. Each phase resembles an earlier encounter, but the attacks are faster and combined in new ways.

After his apparent defeat, the Shadow Circuit activates and transforms him into a giant pixelated energy creature. The final phase becomes a platforming battle where the player climbs the boss itself and destroys several weak points.

**Player lesson:** mastery of the entire game.

## Recurring rival

You could also introduce a rival who appears throughout the game—similar to an arcade-game pursuer.

**Character: Red Fang**

Red Fang sometimes:

- Steals a required key
- Activates traps
- Challenges the player in short fights
- Temporarily joins the player against a boss
- Becomes either an ally or secret final boss depending on player choices

This gives the game a continuing character arc rather than making each stage feel disconnected.

## Progression system

Instead of traditional experience points, each defeated boss could unlock one new move:

| Boss defeated | Ability unlocked |
|---|---|
| Iron Crane | Flying kick |
| Foreman Brass | Charged punch |
| Mire Queen | Water dash |
| Mirror Jack | Shadow dodge |
| General Tanuki | Smoke bomb |
| Sister Aurora | Wall cling |
| Raijin-9 | Projectile deflection |

Earlier levels could contain secret areas that become accessible after new abilities are unlocked.

## Scoring and replayability

To preserve the arcade feel, each stage could score the player based on:

- Completion time
- Damage taken
- Enemies defeated
- Collectibles found
- Longest attack combination
- Whether the boss was defeated without taking damage

You could award ranks such as **D, C, B, A, S**, with hidden character skins or challenge stages unlocked for high scores.

Optional game modes could include:

- Arcade mode with limited lives
- Story mode with checkpoints
- Boss rush
- Two-player cooperative mode
- Daily challenge using a fixed level layout
- Speedrun mode with an on-screen timer

## Visual direction

For an authentic 8-bit appearance:

- Use a limited colour palette for each stage
- Design characters around 24×32 or 32×32 pixel sprites
- Animate attacks with only three to six strong frames
- Use screen shake, hit pauses, and bright impact flashes
- Keep backgrounds detailed but lower contrast than interactive objects
- Use short chiptune tracks with a unique musical theme for every boss

The game can look 8-bit while still using modern effects such as smooth camera movement, particles, dynamic lighting, and responsive controls.

## Browser technology

A practical starting stack would be:

- **Phaser** for gameplay, physics, animation, input, and audio
- **TypeScript** for maintainable game code
- **Tiled** for constructing tile-based levels
- Pixel-art tools such as Aseprite, LibreSprite, or Piskel
- Static hosting through GitHub Pages, Cloudflare Pages, Netlify, or a similar service

Structure each boss as a state machine:

```text
Idle
  ↓
Choose attack
  ↓
Telegraph attack
  ↓
Execute attack
  ↓
Recovery period
  ↓
Return to idle
```

That structure makes bosses challenging without making their behaviour feel random or unfair.

My strongest recommendation would be to begin with **one polished stage, three basic enemies, and the Iron Crane boss**. That vertical slice would let you test movement, combat, level design, visual style, and boss architecture before building the other seven stages.
