import Phaser from "phaser";
import { Boss } from "../actors/Boss";

export class MirrorJack extends Boss {
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, 10);
    this.setTint(0x8ecae6);
  }
}
