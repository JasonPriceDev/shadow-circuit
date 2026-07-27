import Phaser from "phaser";
import { GAME_HEIGHT, GAME_WIDTH } from "../config/GameConfig";
import { Enemy } from "../actors/Enemy";
import { Player } from "../actors/Player";
import { InputSystem } from "../systems/InputSystem";

export class StageScene extends Phaser.Scene {
  private player!: Player;
  private inputSystem!: InputSystem;
  private enemies!: Phaser.Physics.Arcade.Group;
  private stageComplete = false;

  constructor() {
    super("StageScene");
  }

  create(): void {
    this.cameras.main.setBackgroundColor("#16213e");
    this.physics.world.setBounds(0, 0, 1600, GAME_HEIGHT);
    this.cameras.main.setBounds(0, 0, 1600, GAME_HEIGHT);

    this.createBackdrop();
    this.createPlatforms();

    this.player = new Player(this, 120, 360);
    this.inputSystem = new InputSystem(this);
    this.enemies = this.physics.add.group();
    this.enemies.add(new Enemy(this, 480, 360));
    this.enemies.add(new Enemy(this, 700, 360));

    this.physics.add.collider(this.player, this.platforms);
    this.physics.add.collider(this.enemies, this.platforms);
    this.physics.add.collider(this.player, this.enemies, () => {
      this.player.health.damage(1);
    });

    this.cameras.main.startFollow(this.player, true, 0.08, 0.08);
    this.add
      .text(20, 20, "LANTERN ROOFTOPS  |  ARROWS/WASD: MOVE  SPACE: JUMP  X: ATTACK", {
        color: "#ffffff",
        fontFamily: "monospace",
        fontSize: "14px",
      })
      .setScrollFactor(0)
      .setDepth(10);
  }

  update(): void {
    const state = this.inputSystem.read();
    this.player.updateMovement(state);

    if (this.player.x > 1200 && !this.stageComplete) {
      this.stageComplete = true;
      this.scene.start("BossScene", { boss: "Iron Crane" });
    }

    if (this.player.health.isDepleted()) {
      this.scene.start("GameOverScene");
    }
  }

  private platforms!: Phaser.Physics.Arcade.StaticGroup;

  private createPlatforms(): void {
    this.platforms = this.physics.add.staticGroup();
    for (let x = 32; x < 1600; x += 64) {
      this.platforms
        .create(x, GAME_HEIGHT - 24, "platform-placeholder")
        .setOrigin(0.5);
    }

    this.platforms.create(360, 380, "platform-placeholder");
    this.platforms.create(620, 300, "platform-placeholder");
    this.platforms.create(900, 390, "platform-placeholder");
  }

  private createBackdrop(): void {
    this.add
      .rectangle(800, 270, 1600, GAME_HEIGHT, 0x16213e)
      .setDepth(-2);
    for (let x = 40; x < 1600; x += 120) {
      this.add
        .rectangle(x, 330, 80, 180, 0x1f4068)
        .setOrigin(0.5, 1)
        .setDepth(-1);
      this.add
        .rectangle(x + 35, 285, 8, 8, 0xffd166)
        .setDepth(-1);
    }
  }
}
