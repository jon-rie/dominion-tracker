from pathlib import Path
from dominion_tracker.parser import Parser, read_events
from dominion_tracker.engine import GameEngine
import sys

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--players", required=True, help="Comma separated player IDs")
    parser.add_argument("--log", required=True, help="Path to the game log file")
    args = parser.parse_args()

    player_ids = tuple(args.players.split(","))
    log_path = Path(args.log).resolve()

    # Determine project root (two levels up from this file)
    project_root = Path(__file__).resolve().parent.parent

    # Use absolute path for cards CSV
    card_csv_path = project_root / "cards" / "dominion_cards.csv"

    # Instantiate parser with absolute path
    parser_obj = Parser(player_id=player_ids[0], card_csv_path=str(card_csv_path))
    engine = GameEngine()

    events = read_events(str(log_path), player_ids=player_ids)

    for event_text in events:
        action = parser_obj.parse_event(event_text)
        if action:
            engine.apply(action)

    print(engine.summary())

if __name__ == "__main__":
    main()
