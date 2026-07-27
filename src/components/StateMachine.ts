export class StateMachine<TState extends string> {
  constructor(private currentState: TState) {}

  transition(nextState: TState): void {
    this.currentState = nextState;
  }

  get state(): TState {
    return this.currentState;
  }
}
