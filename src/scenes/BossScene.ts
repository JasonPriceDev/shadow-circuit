import Phaser from "phaser";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";
import { IronCrane } from "../bosses/IronCrane";
import { Player } from "../actors/Player";
import { InputSystem } from "../systems/InputSystem";

export class BossScene extends Phaser.Scene {
  private player!: Player;
  private boss!: IronCrane;
  private inputSystem!: InputSystem;

  constructor() {
    super("BossScene");
  }

  create(data: { boss?: string }): void {
    this.add
      .rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x281b3f)
      .setDepth(-1);
    this.add
      .text(GAME_WIDTH / 2, 60, `BOSS: ${data.boss ?? "IRON CRANE"}`, {
        color: "#ffd166",
        fontFamily: "monospace",
        fontSize: "28px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);

    this.player = new Player(this, 240, 390);
    this.boss = new IronCrane(this, 720, 390);
    this.inputSystem = new InputSystem(this);

    const floor = this.physics.add.staticImage(GAME_WIDTH / 2, 500, "platform-placeholder");
    floor.setScale(15, 1).refreshBody();
    this.physics.add.collider(this.player, floor);
    this.physics.add.collider(this.boss, floor);
    this.physics.add.collider(this.player, this.boss, () => {
      this.player.health.damage(1);
    });

    this.add
      .text(GAME_WIDTH / 2, 450, "Defeat the Iron Crane to unlock the flying kick.", {
        color: "#ffffff",
        fontFamily: "monospace",
        fontSize: "16px",
      })
      .setOrigin(0.5);
  }

  update(): void {
    this.player.updateMovement(this.inputSystem.read());
    this.boss.updateBehavior(this.player);

    if (this.player.isAttacking()) {
      this.boss.health.damage(1);
    }

    if (this.boss.health.isDepleted()) {
      this.scene.start("TitleScene");
    } else if (this.player.health.isDepleted()) {
      this.scene.start("GameOverScene");
    }
  }
}
