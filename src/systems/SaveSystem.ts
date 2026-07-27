const SAVE_KEY = "shadow-circuit-save";

export interface SaveData {
  unlockedAbilities: string[];
  highScores: Record<string, number>;
}

export class SaveSystem {
  static load(): SaveData {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) {
      return { unlockedAbilities: [], highScores: {} };
    }

    return JSON.parse(raw) as SaveData;
  }

  static save(data: SaveData): void {
    localStorage.setItem(SAVE_KEY, JSON.stringify(data));
  }
}
