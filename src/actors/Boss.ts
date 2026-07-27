import Phaser from "phaser";
import { Health } from "../components/Health";
import { StateMachine } from "../components/StateMachine";
import { Player } from "./Player";

export class Boss extends Phaser.Physics.Arcade.Sprite {
  readonly health: Health;
  readonly stateMachine = new StateMachine<
    "intro" | "idle" | "telegraph" | "attack" | "recovery" | "stunned" | "phaseChange" | "defeated"
  >("intro");

  constructor(
    scene: Phaser.Scene,
    x: number,
    y: number,
    health: number,
    texture = "boss-placeholder",
  ) {
    super(scene, x, y, texture);
    this.health = new Health(health);
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
    this.setOrigin(0.5, 1);
  }

  updateBehavior(player: Player): void {
    const body = this.body as Phaser.Physics.Arcade.Body;
    const direction = Math.sign(player.x - this.x);
    body.setVelocityX(direction * 50);
    this.stateMachine.transition("idle");
  }
}
