import argparse
from dominion_tracker.parser import Parser, read_events
from dominion_tracker.engine import GameEngine

def main():
    parser = argparse.ArgumentParser(description="Process Dominion game log.")
    parser.add_argument(
        "--players", "-p",
        required=True,
        help="Comma-separated player IDs (e.g. O,L),first player will be tracked"
    )
    parser.add_argument(
        "--log", "-l",
        required=True,
        help="Path to the game log file"
    )

    args = parser.parse_args()

    player_ids = tuple(p.strip() for p in args.players.split(","))
    log_file = args.log

    parser_obj = Parser(player_id=player_ids[0])  # Assume we track the first player
    engine = GameEngine()

    events = read_events(log_file, player_ids=player_ids)

    for event_text in events:
        action = parser_obj.parse_event(event_text)
        if action:
            engine.apply(action)

    print(engine.summary())

if __name__ == "__main__":
    main()
