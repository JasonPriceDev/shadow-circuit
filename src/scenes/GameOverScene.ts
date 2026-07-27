import Phaser from "phaser";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";

export class GameOverScene extends Phaser.Scene {
  constructor() {
    super("GameOverScene");
  }

  create(): void {
    this.add
      .rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x101426)
      .setDepth(-1);
    this.add
      .text(GAME_WIDTH / 2, 220, "KAI HAS FALLEN", {
        color: "#ef476f",
        fontFamily: "monospace",
        fontSize: "36px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
    this.add
      .text(GAME_WIDTH / 2, 330, "PRESS ENTER TO RETURN TO THE TITLE", {
        color: "#ffffff",
        fontFamily: "monospace",
        fontSize: "18px",
      })
      .setOrigin(0.5);
    this.input.keyboard?.once("keydown-ENTER", () => {
      this.scene.start("TitleScene");
    });
  }
}
