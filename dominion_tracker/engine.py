from enum import Enum, auto
from typing import List, Dict
from dominion_tracker.state import PlayerState, InvalidCardMove
import logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    DRAW = auto()
    PLAY = auto()
    DISCARD_PLAYED = auto()
    DISCARD_HAND = auto()
    SHUFFLE = auto()
    GAIN = auto()
    # Later: TRASH, REVEAL, etc.


class Action:
    def __init__(self, type: ActionType, cards: List[str]):
        self.type = type
        self.cards = cards

    def __repr__(self):
        return f"Action(type={self.type}, cards={self.cards})"


class GameEngine:
    def __init__(self):
        self.state = PlayerState()

    def apply(self, action: Action):
        """Applies a parsed action to the player's state."""
        try:
            if action.type == ActionType.DRAW:
                self.state.move_from_deck_to_hand(action.cards)

            elif action.type == ActionType.PLAY:
                self.state.move_from_hand_to_played(action.cards)

            elif action.type == ActionType.DISCARD_PLAYED:
                self.state.move_from_played_to_discard(action.cards)

            elif action.type == ActionType.DISCARD_HAND:
                self.state.move_from_hand_to_discard(action.cards)

            elif action.type == ActionType.SHUFFLE:
                self.state.move_from_discard_to_deck(action.cards)

            elif action.type == ActionType.GAIN:
                self.state.gain_cards(action.cards)

            else:
                raise ValueError(f"Unknown action type: {action.type}")

        except InvalidCardMove as e:
            logger.info(f"Invalid move: {e}")

    def summary(self) -> Dict[str, Dict[str, int]]:
        return self.state.summary()

    def __str__(self):
        return str(self.state)
