import Phaser from "phaser";
import { Boss } from "../actors/Boss";

export class EmperorNull extends Boss {
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, 16);
    this.setTint(0xef476f);
  }
}
