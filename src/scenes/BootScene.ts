import Phaser from "phaser";

export class BootScene extends Phaser.Scene {
  constructor() {
    super("BootScene");
  }

  create(): void {
    this.createTexture("player-placeholder", 28, 40, 0xffd166);
    this.createTexture("enemy-placeholder", 28, 36, 0xef476f);
    this.createTexture("boss-placeholder", 64, 80, 0x9b5de5);
    this.createTexture("platform-placeholder", 64, 16, 0x3f8f8c);
    this.scene.start("PreloadScene");
  }

  private createTexture(
    key: string,
    width: number,
    height: number,
    color: number,
  ): void {
    const graphics = this.make.graphics({ x: 0, y: 0 });
    graphics.fillStyle(color, 1);
    graphics.fillRect(0, 0, width, height);
    graphics.generateTexture(key, width, height);
    graphics.destroy();
  }
}
