from collections import defaultdict,Counter
from typing import Dict, List

class InvalidCardMove(Exception):
    """Raised when an invalid card move is attempted."""
    pass


class PlayerState:
    def __init__(self):
        self.deck: Dict[str, int] = defaultdict(int)
        self.hand: Dict[str, int] = defaultdict(int)
        self.discard: Dict[str, int] = defaultdict(int)
        self.played: Dict[str, int] = defaultdict(int)

    def move_cards(self, source: Dict[str, int], target: Dict[str, int], cards: List[str], action: str = ""):
        for card in cards:
            if source[card] <= 0:
                raise InvalidCardMove(f"Tried to {action} '{card}' but it's not in source pile.")
            source[card] -= 1
            if source[card] == 0:
                del source[card]
            target[card] += 1

    def move_from_hand_to_played(self, cards: List[str]):
        self.move_cards(self.hand, self.played, cards, action="play")

    def move_from_hand_to_discard(self, cards: List[str]):
        self.move_cards(self.hand, self.discard, cards, action="discard")

    def move_from_discard_to_deck(self, cards: List[str]):
        self.move_cards(self.discard, self.deck, cards, action="shuffle")

    def move_from_deck_to_hand(self, cards: List[str]):
        self.move_cards(self.deck, self.hand, cards, action="draw")
    
    def move_from_hand_to_deck(self, cards: List[str]):
        self.move_cards(self.hand, self.deck, cards, action="return to deck")

    def move_from_played_to_discard(self, cards: List[str]):
        self.move_cards(self.played, self.discard, cards, action="discard")
    
    def move_whole_discard_to_deck(self):
        discard = list([k for k,v in self.discard.items() for _ in range(v)])
        self.move_from_discard_to_deck(discard)
    
    def move_whole_hand_to_discard(self):
        hand = list([k for k,v in self.hand.items() for _ in range(v)])
        self.move_from_hand_to_discard(hand)
    
    def move_whole_played_to_discard(self):
        played = list([k for k,v in self.played.items() for _ in range(v)])
        self.move_from_played_to_discard(played)
    
    def gain_cards(self, cards: List[str]):
        # Cards are gained from outside the tracked piles
        synthetic_source = Counter(cards)
        self.move_cards(synthetic_source, self.discard, cards, action="gain")

    def trash_cards(self, cards: List[str]):
        # Cards are trashed out of the game; destination is ignored
        synthetic_trash = defaultdict(int)
        self.move_cards(self.hand, synthetic_trash, cards, action="trash")

    def summary(self):
        return {
            "deck": dict(self.deck),
            "hand": dict(self.hand),
            "discard": dict(self.discard),
            "played": dict(self.played)   
        }
    
    def total_cards(self):
        total = Counter()
        for pile in [self.deck, self.hand, self.discard, self.played]:
            total.update(pile)
        return dict(total)
    
    def __repr__(self):
        return f"Deck: {dict(self.deck)}, Hand: {dict(self.hand)}, Discard: {dict(self.discard)}, In Play: {dict(self.played)}"


