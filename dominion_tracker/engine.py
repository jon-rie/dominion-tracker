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
    DISCARD_WHOLE_HAND = auto()
    DISCARD_WHOLE_PLAYED = auto()
    END_TURN = auto()
    TRASH = auto()


class Action:
    def __init__(self, type: ActionType, cards: List[str]):
        self.type = type
        self.cards = cards

    def __repr__(self):
        return f"Action(type={self.type}, cards={self.cards})"


class GameEngine:
    def __init__(self, starting_deck: Dict[str, int] = None) -> None:
        self.state = PlayerState()
        if starting_deck is None:
            starting_deck = {"Copper": 7, "Estate": 3}
        for card, count in starting_deck.items():
            self.state.deck[card] = count
           

    def apply(self, action: Action) -> None:

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
                self.state.move_whole_discard_to_deck()
            
            elif action.type == ActionType.DISCARD_WHOLE_HAND:
                self.state.move_whole_hand_to_discard()

            elif action.type == ActionType.DISCARD_WHOLE_PLAYED:
                self.state.move_whole_played_to_discard()

            elif action.type == ActionType.GAIN:
                self.state.gain_cards(action.cards)

            elif action.type == ActionType.END_TURN:
                self.state.move_whole_played_to_discard()
                self.state.move_whole_hand_to_discard()
            
            elif action.type == ActionType.TRASH:
                self.state.trash_cards(action.cards)

            else:
                logger.error(f"Unknown action type: {action.type}")
                raise ValueError(f"Unknown action type: {action.type}")

        except InvalidCardMove as e:
            logger.warning(f"Invalid move: {e}")

    def summary(self) -> Dict[str, Dict[str, int]]:
        return self.state.summary()

    def __str__(self) -> str:
        return str(self.state)
