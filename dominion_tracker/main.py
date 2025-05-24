from parser import parse_log
from state import PlayerState
from engine import apply_event


def main():
    with open("game_log.txt") as f:
        log_text = f.read()

    events = parse_log(log_text, player_initial='O')
    state = PlayerState()

    for turn, action_line in events:
        apply_event(state, turn, action_line)

    print("Current Turn Hand:", state.hand)
    print("Deck (top first):", list(state.deck))
    print("Discard Pile:", state.discard)

if __name__ == "__main__":
    main()
