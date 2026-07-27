import Phaser from "phaser";
import { Boss } from "../actors/Boss";

export class IronCrane extends Boss {
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, 8);
    this.setTint(0x9b5de5);
  }
}
