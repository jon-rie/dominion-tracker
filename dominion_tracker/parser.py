import re
from typing import List, Optional
from dominion_tracker.engine import Action, ActionType
import csv
from pathlib import Path

def read_events(file_path: str, player_ids: tuple[str, ...]) -> list[str]:
    events = []
    current_event = []

    with open(file_path) as f:
        lines = [line.strip() for line in f if line.strip()]  # Strip and skip empty lines

    for i, line in enumerate(lines):
        # New event starts
        if line.startswith("Turn") or any(line.startswith(pid) for pid in player_ids):
            if current_event:
                events.append(" ".join(current_event))
                current_event = []

        current_event.append(line)

        if line.startswith("Turn"):
            # Look back in the last few events to find the draw (and optional shuffle) event of "O"
            pos = len(events) - 1
            player_id = events[pos].split()[0]
            if pos > 0 and "shuffles" in events[pos - 1]:
                insert_at = pos - 1
            else:
                insert_at = pos
            events.insert(insert_at, f"{player_id} ends turn")

    # Append last event if it exists
    if current_event:
        events.append(" ".join(current_event))

    return events

def singularize(card_name: str) -> str:
    if card_name.endswith("ies"):
        return card_name[:-3] + "y"  # e.g. "parties" -> "party"
    if card_name.endswith("s") and not card_name.endswith("ss"):
        return card_name[:-1]       # e.g. "coppers" -> "copper"
    return card_name

class Parser:

    def __init__(self, player_id: str, card_csv_path: str = "cards/dominion_cards.csv", max_card_words: int = 3):
        self.player_id = player_id
        self.max_card_words = max_card_words
        path = Path(card_csv_path)
        self.valid_card_names = self._load_card_names(path)

    
    def _load_card_names(self, path: Path) -> dict:
        card_names = {}
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            for row in reader:
                if not row:
                    continue
                name = row[0].strip()
                if name:
                    card_names[name.lower()] = name
        return card_names

    def parse_event(self, event: str) -> Optional[Action]:
        """Parse a full event string into an Action for the specified player, or None."""
        
        if not event.startswith(self.player_id):
            return None

        text = event.lower()

        cards = self.extract_cards(text)

        # Determine action type from keywords
        if "draws" in text:
            return Action(ActionType.DRAW, cards)

        if "plays" in text:
            return Action(ActionType.PLAY, cards)

        if "discards" in text:
            # Discard from hand or played? We'll assume hand for now
            return Action(ActionType.DISCARD_HAND, cards)

        if "shuffles" in text:
            # Shuffle means move discard to deck, cards param empty (usually)
            return Action(ActionType.SHUFFLE, [])

        if "buys and gains" in text or "gains" in text:
            return Action(ActionType.GAIN, cards)
        
        if "trashes" in text:
            return Action(ActionType.TRASH, cards)
        
        if "ends" in text:
            return Action(ActionType.END_TURN, [])

        return None


    def extract_cards(self, text: str) -> List[str]:
        """Extract card names (single or multi-word) from text using known card name list."""

        # Normalize input
        clean_text = re.sub(r"\(\+\$.*?\)", "", text)
        clean_text = re.sub(r"[.,]", " ", clean_text)
        tokens = clean_text.split()

        for i in range(len(tokens)):
            tokens[i] = singularize(tokens[i])

        result = []
        i = 0
        while i < len(tokens):

            # Handle leading numeric count
            if tokens[i].isdigit():
                count = int(tokens[i])
                i += 1
            else:
                count = 1

            # Try to match up to 3-word card names (greedy)
            matched = False
            for span in range(self.max_card_words, 0, -1):
                if i + span <= len(tokens):
                    candidate = " ".join(tokens[i:i + span])
                    if candidate in self.valid_card_names:
                        result.extend([self.valid_card_names[candidate]] * count)
                        i += span
                        matched = True
                        break

            if not matched:
                i += 1  # Skip unrecognized token

        return result
    


