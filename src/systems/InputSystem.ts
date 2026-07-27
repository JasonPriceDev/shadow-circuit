import Phaser from "phaser";

export interface InputState {
  left: boolean;
  right: boolean;
  jump: boolean;
  attack: boolean;
}

export class InputSystem {
  private readonly cursors: Phaser.Types.Input.Keyboard.CursorKeys;
  private readonly keys: Record<"jump" | "attack", Phaser.Input.Keyboard.Key>;

  constructor(scene: Phaser.Scene) {
    if (!scene.input.keyboard) {
      throw new Error("Keyboard input is required for the platformer.");
    }

    this.cursors = scene.input.keyboard.createCursorKeys();
    this.keys = {
      jump: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE),
      attack: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.X),
    };
  }

  read(): InputState {
    return {
      left: Boolean(this.cursors.left?.isDown),
      right: Boolean(this.cursors.right?.isDown),
      jump: Boolean(this.cursors.up?.isDown || this.keys.jump.isDown),
      attack: Boolean(this.keys.attack.isDown),
    };
  }
}
