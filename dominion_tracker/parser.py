import re
from typing import List, Optional
from dominion_tracker.engine import Action, ActionType

def read_events(file_path, player_ids) -> list[str]:
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

# Basic singularization helper (can be expanded or replaced by a lib like inflect)
def singularize(card_name: str) -> str:
    if card_name.endswith("ies"):
        return card_name[:-3] + "y"  # e.g. "parties" -> "party"
    if card_name.endswith("s") and not card_name.endswith("ss"):
        return card_name[:-1]       # e.g. "coppers" -> "copper"
    return card_name

class Parser:
    def __init__(self, player_id: str):
        self.player_id = player_id

    def parse_event(self, event: str) -> Optional[Action]:
        """Parse a full event string into an Action for the specified player, or None."""
        
        # Quick skip if event not about the player
        if not event.startswith(self.player_id):
            return None

        # Normalize spacing and lower case for easier matching
        text = event.lower()

        # Extract cards (simple heuristic): words after keywords like 'draws', 'plays', 'discards', 'gains'
        # Cards are usually like "3 coppers", "an estate", "a village"
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
        
        if "ends" in text:
            return Action(ActionType.END_TURN, [])

        # Could add more rules here (trash, reveal, etc.)

        return None


    def extract_cards(self,text: str) -> List[str]:
        """Extract cards from event text with counts and singularized names."""
        # Clean up currency and punctuation, lower case for consistency
        clean_text = re.sub(r"\(\+\$.*?\)", "", text.lower())
        clean_text = clean_text.replace(",", " ").replace(".", " ")

        tokens = clean_text.split()

        cards = []
        skip_words = {"a", "an", "and", "cards", "card", "their", "starts", "with", "turn", "draws", "plays", "discards", "gains", "buys", self.player_id.lower()}

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token in skip_words:
                i += 1
                continue

            # Check if token is a number (count)
            if token.isdigit():
                count = int(token)
                # Next token should be card name
                if i + 1 < len(tokens):
                    card_name = singularize(tokens[i + 1])
                    cards.extend([card_name.capitalize()] * count)
                    i += 2
                    continue
                else:
                    i += 1
                    continue

            # Handle "a" or "an" + card_name (means count=1)
            if token in {"a", "an"} and i + 1 < len(tokens):
                card_name = singularize(tokens[i + 1])
                cards.append(card_name.capitalize())
                i += 2
                continue

            # If just a card name without count
            if token not in skip_words:
                card_name = singularize(token)
                cards.append(card_name.capitalize())
                i += 1
                continue

            i += 1

        return cards
    


