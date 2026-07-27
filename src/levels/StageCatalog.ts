export interface StageDefinition {
  id: string;
  name: string;
  boss: string;
  lesson: string;
  unlocks?: string;
}

export const stages: StageDefinition[] = [
  {
    id: "stage-01",
    name: "Lantern Rooftops",
    boss: "Iron Crane",
    lesson: "Jumping, ducking, and recognizing attack ranges",
    unlocks: "Flying kick",
  },
  {
    id: "stage-02",
    name: "Clockwork Foundry",
    boss: "Foreman Brass",
    lesson: "Using the environment during combat",
    unlocks: "Charged punch",
  },
  {
    id: "stage-03",
    name: "Flooded Catacombs",
    boss: "Mire Queen",
    lesson: "Watching environmental clues",
    unlocks: "Water dash",
  },
  {
    id: "stage-04",
    name: "Neon Market",
    boss: "Mirror Jack",
    lesson: "Observation rather than constant attacking",
    unlocks: "Shadow dodge",
  },
  {
    id: "stage-05",
    name: "Bamboo Fortress",
    boss: "General Tanuki",
    lesson: "Multi-phase boss battles",
    unlocks: "Smoke bomb",
  },
  {
    id: "stage-06",
    name: "Frozen Observatory",
    boss: "Sister Aurora",
    lesson: "Movement control and pattern recognition",
    unlocks: "Wall cling",
  },
  {
    id: "stage-07",
    name: "Storm Temple",
    boss: "Raijin-9",
    lesson: "Defensive timing and parrying",
    unlocks: "Projectile deflection",
  },
  {
    id: "stage-08",
    name: "The Shadow Citadel",
    boss: "Emperor Null",
    lesson: "Mastery of the entire game",
  },
];
