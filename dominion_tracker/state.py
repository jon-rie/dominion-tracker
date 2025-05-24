from collections import defaultdict
from typing import Dict, List

class InvalidCardMove(Exception):
    """Raised when an invalid card move is attempted."""
    pass


class PlayerState:
    def __init__(self):
        self.deck: Dict[str, int] = defaultdict(int)
        self.hand: Dict[str, int] = defaultdict(int)
        self.discard: Dict[str, int] = defaultdict(int)
        self.in_play: Dict[str, int] = defaultdict(int)

    def move_cards(self, source: Dict[str, int], target: Dict[str, int], cards: List[str], action: str = ""):
        for card in cards:
            if source[card] <= 0:
                raise InvalidCardMove(f"Tried to {action} '{card}' but it's not in source pile.")
            source[card] -= 1
            target[card] += 1

    def move_from_hand_to_played(self, cards: List[str]):
        self.move_cards(self.hand, self.in_play, cards, action="play")

    def move_from_hand_to_discard(self, cards: List[str]):
        self.move_cards(self.hand, self.discard, cards, action="discard")

    def move_from_discard_to_deck(self, cards: List[str]):
        self.move_cards(self.discard, self.deck, cards, action="shuffle")

    def move_from_deck_to_hand(self, cards: List[str]):
        self.move_cards(self.deck, self.hand, cards, action="draw")

    def move_from_played_to_discard(self, cards: List[str]):
        self.move_cards(self.in_play, self.discard, cards, action="discard")
    
    def gain_cards(self, cards: List[str]):
        for card in cards:
            self.discard[card] += 1

    def summary(self):
        return {
            "deck": dict(self.deck),
            "hand": dict(self.hand),
            "discard": dict(self.discard),
            "in_play": dict(self.in_play)   
        }

