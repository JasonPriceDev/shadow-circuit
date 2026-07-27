import Phaser from "phaser";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";

export class TitleScene extends Phaser.Scene {
  constructor() {
    super("TitleScene");
  }

  create(): void {
    this.add
      .rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x101426)
      .setDepth(-1);

    this.add
      .text(GAME_WIDTH / 2, 150, "SHADOW CIRCUIT", {
        color: "#ffd166",
        fontFamily: "monospace",
        fontSize: "54px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);

    this.add
      .text(GAME_WIDTH / 2, 240, "A KAI PROTOTYPE", {
        color: "#8ecae6",
        fontFamily: "monospace",
        fontSize: "18px",
      })
      .setOrigin(0.5);

    this.add
      .text(GAME_WIDTH / 2, 380, "PRESS ENTER OR CLICK TO BEGIN", {
        color: "#ffffff",
        fontFamily: "monospace",
        fontSize: "20px",
      })
      .setOrigin(0.5);

    this.input.keyboard?.once("keydown-ENTER", this.startGame, this);
    this.input.once("pointerdown", this.startGame, this);
  }

  private startGame(): void {
    this.scene.start("StageScene");
  }
}
