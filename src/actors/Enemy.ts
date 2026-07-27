import Phaser from "phaser";
import { Health } from "../components/Health";

export class Enemy extends Phaser.Physics.Arcade.Sprite {
  readonly health = new Health(2);

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, "enemy-placeholder");
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
    this.setOrigin(0.5, 1);
  }
}
