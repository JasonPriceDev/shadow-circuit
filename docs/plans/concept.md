
This my sdlc-agent.yml

name: SDLC Agent

on:
  issues:
    types: [opened, edited, labeled]
  pull_request:
    types: [opened, synchronize]
  schedule:

cron: "0 6 * * 1-5"
workflow_dispatch:
  inputs:
prompt:
  description: "What should the agent do?"
  required: true
dry_run:
  description: "Preview only, don't write to GitHub"
  type: boolean
  default: false
jobs:
  run:
    runs-on: ubuntu-latest
    steps:

uses: actions/checkout@v4
uses: actions/setup-python@v5
with:
python-version: "3.12"
run: pip install -r agents/requirements.txt
run: PYTHONPATH=agents python -m sdlc_agent.run
env:
DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
DEEPSEEK_MODEL: ${{ vars.DEEPSEEK_MODEL || 'deepseek-v4-pro' }}
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
TRIGGER_EVENT: ${{ github.event_name }}
ISSUE_NUMBER: ${{ github.event.issue.number || '' }}
PR_NUMBER: ${{ github.event.pull_request.number || '' }}
DRY_RUN: ${{ inputs.dry_run || 'false' }}
And this is my ci.yml:

name: CI

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:

uses: actions/checkout@v4
uses: actions/setup-node@v4
with:
node-version: "22"
run: npm ci
run: npm run typecheck
run: npm run build
Can you bring these into alignment.

…

Show more
2:16 PM

Worked for 1m 42s
Aligned and syntax-checked both workflows:

sdlc-agent.yml
ci.yml
Updated agentic-sdlc-workflow.md
Changes include corrected YAML indentation, issue_comment handling, permissions, concurrency, timeouts, dependency caching, safe manual dry-run defaults, manual prompt forwarding, fork protection, and the documented Edmonton schedule.

Before the agent workflow will run, create this repository variable:

SDLC_AGENT_ENABLED=true
Leaving it undefined or setting it to false acts as the kill switch. The agent implementation must also enforce DRY_RUN internally and filter irrelevant or agent-generated issue comments.


Edited 3 files
+151
-3
outputs/agentic-sdlc-workflow.md
outputs/
agentic-sdlc-workflow.md
+29
-3
outputs/ci.yml
outputs/
ci.yml
+35
-0
outputs/sdlc-agent.yml
outputs/
sdlc-agent.yml
+87
-0
2:18 PM
This is my bug.yml

name: Bug
description: Report a defect. Logged against a Feature or Epic.
title: "[Bug]: "
labels: ["type:bug"]
body:

type: markdown
attributes:
value: |
The SDLC agent will triage this automatically — assigning severity,
attempting root-cause analysis, and proposing a fix. Bugs are logged
against a Feature (or Epic if the feature doesn't exist yet).

type: input
id: parent
attributes:
label: Linked Feature or Epic
description: Number of the Feature or Epic issue this bug belongs to.
placeholder: "#123"
validations:
required: true

type: textarea
id: what-happened
attributes:
label: What happened
description: Steps to reproduce, what you saw.
placeholder: |

Start the game.
Walk right into the first enemy.
Observe: health drains to zero in under a second.
validations:
required: true
type: textarea
id: expected
attributes:
label: What you expected
description: What should have happened instead.
validations:
required: true

type: input
id: scene
attributes:
label: Scene or area
description: Which scene, stage, or boss this occurs in.
placeholder: StageScene (Lantern Rooftops)
validations:
required: false

type: textarea
id: console
attributes:
label: Console output
description: Any browser console errors or warnings.
render: text
validations:
required: false

type: dropdown
id: severity
attributes:
label: Severity (your estimate)
description: The agent will confirm or adjust this.
options:

"critical: crash or unplayable"
"major: wrong behavior"
"minor: cosmetic or edge case"
validations:
required: true
My epic.yml

name: Epic
description: A large body of work within a Spec, broken into Features by the agent.
title: "[Epic]: "
labels: ["type:epic", "agent:generated"]
body:

type: input
id: parent-spec
attributes:
label: Parent Spec
description: Number of the parent type:spec issue this Epic belongs to.
placeholder: "#100"
validations:
required: true

type: textarea
id: description
attributes:
label: Description
description: What this Epic covers. The agent will break this into Features.
validations:
required: true

type: textarea
id: acceptance
attributes:
label: Acceptance criteria
description: How to verify this Epic is done (all its Features complete).
value: |

[ ]
validations:
required: true
type: dropdown
id: area
attributes:
label: Area
options:

player
enemy
boss
stage
systems
ui
build
ci
validations:
required: true
feature.yml

name: Feature
description: A medium work unit within an Epic. Broken into Tasks by the agent.
title: "[Feature]: "
labels: ["type:feature", "agent:generated"]
body:

type: input
id: parent-epic
attributes:
label: Parent Epic
description: Number of the parent type:epic issue this feature belongs to.
placeholder: "#123"
validations:
required: true

type: input
id: parent-spec
attributes:
label: Parent Spec (if no Epic)
description: Number of the parent type:spec issue (only if this feature is not under an Epic).
placeholder: "#100"
validations:
required: false

type: textarea
id: description
attributes:
label: Description
description: What this feature covers. The agent will break this into Tasks.
validations:
required: true

type: textarea
id: acceptance
attributes:
label: Acceptance criteria
description: How to verify this feature is done (all its Tasks complete).
value: |

[ ]
validations:
required: true
type: textarea
id: files
attributes:
label: Files likely involved
description: Expected file paths (the agent will determine exact paths during planning).
placeholder: |

src/scenes/StageScene.ts (modify)
src/components/Invulnerability.ts (create)
validations:
required: false
type: dropdown
id: discipline
attributes:
label: Primary discipline
options:

code
art
audio
design
qa
validations:
required: true
spec.yml

name: Spec
description: Propose a top-level specification. Once approved, the agent generates a plan breaking it into Epics, Features, and Tasks.
title: "[Spec]: "
labels: ["type:spec", "agent:generated"]
body:

type: markdown
attributes:
value: |
A spec is the single source of truth for a body of work. Once you approve
this spec, the SDLC agent will generate a plan and break it down into
Epics → Features → Tasks. See docs/specs/README.md for the lifecycle.

type: input
id: spec-file
attributes:
label: Spec file
description: Path to the spec Markdown file in docs/specs/ (optional if small).
placeholder: docs/specs/lantern-rooftops.md
validations:
required: false

type: textarea
id: summary
attributes:
label: Summary
description: One paragraph describing what this spec covers and why.
validations:
required: true

type: textarea
id: acceptance
attributes:
label: Acceptance criteria
description: Checklist of verifiable outcomes at the spec level.
value: |

[ ]
[ ]
[ ]
validations:
required: true
type: textarea
id: design
attributes:
label: Design notes
description: Mechanics, patterns, layouts, tuning values — whatever the agent needs to plan implementation.
validations:
required: false

type: textarea
id: dependencies
attributes:
label: Dependencies
description: What must exist before this can be built.
validations:
required: false

type: textarea
id: risks
attributes:
label: Risks and open questions
description: What's uncertain, what could go wrong.
validations:
required: false

type: dropdown
id: size
attributes:
label: Does this need to be broken into Epics?
description: Small specs can skip the Epic layer and go straight to Features.
options:

"Yes — break into Epics"
"No — go straight to Features"
validations:
required: true
task.yml

name: Task
description: The smallest unit of work. One pull request per task.
title: "[Task]: "
labels: ["type:task", "agent:generated"]
body:

type: input
id: parent-feature
attributes:
label: Parent Feature
description: Number of the parent type:feature issue this task belongs to.
placeholder: "#200"
validations:
required: true

type: input
id: parent-spec
attributes:
label: Root Spec
description: Number of the top-level type:spec issue (for traceability).
placeholder: "#100"
validations:
required: true

type: textarea
id: description
attributes:
label: Description
description: One implementable piece of work. Exactly one pull request.
validations:
required: true

type: textarea
id: acceptance
attributes:
label: Acceptance criteria
description: How to verify this task is done.
value: |

npm run typecheck passes
npm run build passes
[ ]
validations:
required: true
type: textarea
id: files
attributes:
label: Files to create or modify
description: Specific file paths.
placeholder: |

src/components/Invulnerability.ts (create)
src/scenes/StageScene.ts (modify L31-L34)
validations:
required: true
type: dropdown
id: discipline
attributes:
label: Primary discipline
options:

code
art
audio
design
qa
validations:
required: true
…

Show more
2:22 PM
You stopped after 5s
Bring it into alignment.

2:22 PM

Worked for 2m 44s
Aligned and validated all five issue forms:

bug.yml
spec.yml
epic.yml
feature.yml
task.yml
I also synchronized the provenance rule in agentic-sdlc-workflow.md.

Key changes:

Default hierarchy is now Spec → Task → PR.
Epic and Feature layers are explicitly optional.
Templates apply status:proposed.
Human-created issues no longer automatically receive agent:generated.
Parent fields support both the direct and expanded hierarchies.
Tasks reference symbols instead of fragile line numbers.
Bug reports include reproducibility, revision, evidence, and secret-removal checks.
Submitting a form is clearly separated from implementation approval.
All templates passed YAML and structural validation.

Edited 6 files
+528
-0
outputs/agentic-sdlc-workflow.md
outputs/
agentic-sdlc-workflow.md
+9
-0
outputs/bug.yml
outputs/
bug.yml
+123
-0
outputs/epic.yml
outputs/
epic.yml
+75
-0

Show 3 more files
2:25 PM

## Core concept: *Shadow Circuit* You play **Kai**, a courier-monk whose city h…
This was my concept.md

2:28 PM

Worked for 2m 48s
Revised and aligned the concept document:

concept.md
It now clearly separates:

Authoritative product vision.
First playable vertical-slice scope.
Full-game vision.
Optional backlog such as Red Fang, co-op, and daily challenges.
Candidate ideas requiring specifications.
Unresolved decisions the agent must not guess.
Vertical-slice non-goals.
Accessibility and boss-fairness principles.
All eight districts, bosses, lessons, and progression unlocks were cross-checked against agent-tech-stack.md. Crouch/duck is now the initial Lantern Rooftops action, while Shadow Dodge remains the later Mirror Jack unlock.


Edited concept.md
+428
-0
2:31 PM




Outputs

Create a file or site

Sources

## Core concept: *Shadow Circuit* You play **Kai**, a courier-monk whose city h…

# Agent Tech Stack Reference Status: **Authoritative**. This document is the ca…

# Agentic SDLC Workflow — Harness-Based Plan Status: **Draft for review**. ## 1…

View all
outputs/concept.md
- Escalation that increases complexity without discarding established rules.

### 2.5 Replayable arcade structure

Stages are short enough to replay for improved performance. Scoring and ranking
reward mastery without blocking completion of the main game.

## 3. Scope model

### 3.1 First playable vertical slice

The first product milestone is one polished Lantern Rooftops stage containing:

- Kai's core movement.
- One reliable basic attack.
- Crouch/duck as the initial low-profile defensive action.
- Three basic enemy archetypes.
- Environmental platforming and hazards.
- The Iron Crane boss.
- Health, damage feedback, defeat, retry, and victory flow.
- A minimal score or completion summary sufficient to evaluate replayability.
- Placeholder art and audio where final assets do not yet exist.

The vertical slice exists to validate movement, combat, encounter design,
visual readability, boss architecture, and the production pipeline before
building the remaining districts.

### 3.2 Full-game vision

The full vision contains eight ordered districts and bosses, boss-granted
abilities, revisitable secrets, scoring ranks, and a final encounter that
recombines earlier lessons.

The full-game vision is not one implementation unit. Each district, system, and
mode requires an approved specification.

### 3.3 Optional backlog

The following ideas are not committed scope:

- Red Fang's recurring rival storyline.
- Branching ally/secret-boss outcomes.
- Arcade mode with limited lives.
- Story mode with checkpoints.
- Boss rush.
- Two-player cooperative play.
- Daily challenges.
- Dedicated speedrun mode.
- Unlockable skins and challenge stages.
- Controller and touchscreen support.

These ideas may be explored through Research or Spec issues. An agent must not
include them in a plan merely because they appear here.

## 4. Core player actions

The intended action vocabulary is:

- Move left and right.
- Jump.
- Perform a basic attack.
- Crouch or duck under appropriate attacks.
- Use unlocked movement or combat abilities.

Candidate attacks and techniques include:

- Standing punch.
- Flying kick.
- Crouching sweep.
- Wall kick.
- Downward strike.
- Deflect or parry.

Only the basic attack is assumed for the initial core. Other techniques require
an approved specification or progression unlock. The game should not depend on
long or opaque button combinations.

Exact bindings, buffering, coyote time, invulnerability timing, attack data,
controller mapping, and touch controls belong in implementation specifications.

## 5. Districts and bosses

The stage order, boss identity, player lesson, and progression unlocks must stay
consistent with `src/levels/StageCatalog.ts`.

### 5.1 Lantern Rooftops

A nighttime district of tiled roofs, hanging signs, chimneys, lanterns, and
collapsing platforms.

**Boss — Iron Crane**

Iron Crane is a masked fighter with long-reaching kicks who leaps between
platforms. A later phase may cut lantern ropes, creating falling, burning
obstacles. The exact phase structure requires an approved boss specification.

**Player lesson:** Jumping, ducking or evading, and recognizing attack ranges.

**Unlock:** Flying kick.

### 5.2 Clockwork Foundry

A mechanical district of conveyor belts, crushers, furnaces, steam vents, and
moving gears.

**Boss — Foreman Brass**

Foreman Brass is a mechanical brawler with replaceable arms. Candidate arm
functions include punching, firing rivets, and shielding. The intended encounter
asks the player to exploit machinery to damage his armor.

**Player lesson:** Using the environment during combat.

**Unlock:** Charged punch.

### 5.3 Flooded Catacombs

Underground chambers contain rising water, rafts, crumbling bridges, and
creatures hidden below the surface.

**Boss — Mire Queen**

Mire Queen is a serpent-like guardian who submerges and reappears. Water ripples
telegraph her position. Rising water reduces the safe combat area as the
encounter escalates.

**Player lesson:** Reading environmental clues.

**Unlock:** Water dash.

### 5.4 Neon Market

A crowded cyberpunk market contains moving carts, elevators, electrical signs,
and enemies concealed among civilians.

**Boss — Mirror Jack**

Mirror Jack creates copies. The real boss must have a consistent, learnable
visual or behavioral tell, such as a different shadow or reaction to movement.

**Player lesson:** Observation rather than constant attacking.

**Unlock:** Shadow dodge.

### 5.5 Bamboo Fortress

A forest fortress contains swinging bamboo, rope bridges, falling logs, hidden
archers, smoke, and traps.

**Boss — General Tanuki**

General Tanuki begins mounted on an armored boar. The player avoids charges and
removes the boar's protection before fighting the general directly through
smoke and trap patterns.

**Player lesson:** Reading and adapting to multi-phase boss battles.

**Unlock:** Smoke bomb.

### 5.6 Frozen Observatory

The observatory uses slippery floors, rotating telescopes, falling icicles,
freezing wind, and candidate low-gravity chambers.

**Boss — Sister Aurora**

Sister Aurora creates ice clones and freezes parts of the arena. Her attacks
follow patterns associated with constellations visible through the roof.

**Player lesson:** Movement control and pattern recognition.

**Unlock:** Wall cling.

### 5.7 Storm Temple

A vertical temple climb uses rotating platforms, swinging bells, wind, and
lightning.

**Boss — Raijin-9**

Raijin-9 conducts lightning through metal surfaces, pushing the player toward
safe materials and timed movement. Successful defensive timing redirects
electrical projectiles.

**Player lesson:** Defensive timing and parrying.

**Unlock:** Projectile deflection.

### 5.8 The Shadow Citadel

The final fortress recombines mechanics from the previous seven districts.

