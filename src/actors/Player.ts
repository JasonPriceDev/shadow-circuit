import Phaser from "phaser";
import { Health } from "../components/Health";
import { InputState } from "../systems/InputSystem";

export class Player extends Phaser.Physics.Arcade.Sprite {
  readonly health = new Health(5);
  private attacking = false;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, "player-placeholder");
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
    this.setOrigin(0.5, 1);
  }

  updateMovement(input: InputState): void {
    const body = this.body as Phaser.Physics.Arcade.Body;
    const speed = 220;
    body.setVelocityX((Number(input.right) - Number(input.left)) * speed);

    if (input.jump && body.blocked.down) {
      body.setVelocityY(-470);
    }

    this.attacking = input.attack;
    if (this.attacking) {
      this.setTint(0xffffff);
    } else {
      this.clearTint();
    }
  }

  isAttacking(): boolean {
    return this.attacking;
  }
}
