import Phaser from "phaser";
import { BootScene } from "../scenes/BootScene";
import { BossScene } from "../scenes/BossScene";
import { GameOverScene } from "../scenes/GameOverScene";
import { PreloadScene } from "../scenes/PreloadScene";
import { StageScene } from "../scenes/StageScene";
import { TitleScene } from "../scenes/TitleScene";

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
