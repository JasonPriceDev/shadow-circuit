export class Health {
  constructor(
    readonly maximum: number,
    private current = maximum,
  ) {}

  damage(amount: number): void {
    this.current = Math.max(0, this.current - amount);
  }

  isDepleted(): boolean {
    return this.current === 0;
  }

  get value(): number {
    return this.current;
  }
}
