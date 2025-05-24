import unittest
from dominion_tracker.engine import GameEngine, Action, ActionType
from dominion_tracker.state import InvalidCardMove


class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_starting_deck(self):
        summary = self.engine.summary()
        self.assertEqual(summary["deck"].get("Copper", 0), 7)
        self.assertEqual(summary["deck"].get("Estate", 0), 3)
        self.assertEqual(sum(summary["hand"].values()), 0)

    def test_draw_cards(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper", "Estate"]))
        summary = self.engine.summary()
        self.assertEqual(summary["hand"]["Copper"], 1)
        self.assertEqual(summary["hand"]["Estate"], 1)
        self.assertEqual(summary["deck"]["Copper"], 6)
        self.assertEqual(summary["deck"]["Estate"], 2)

    def test_play_cards(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.PLAY, ["Copper"]))
        summary = self.engine.summary()
        self.assertNotIn("Copper", summary["hand"])
        self.assertEqual(summary["played"]["Copper"], 1)

    def test_discard_played(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.PLAY, ["Copper"]))
        self.engine.apply(Action(ActionType.DISCARD_PLAYED, ["Copper"]))
        summary = self.engine.summary()
        self.assertNotIn("Copper", summary["played"])
        self.assertEqual(summary["discard"]["Copper"], 1)

    def test_discard_hand(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.DISCARD_HAND, ["Copper"]))
        summary = self.engine.summary()
        self.assertNotIn("Copper", summary["hand"])
        self.assertEqual(summary["discard"]["Copper"], 1)

    def test_shuffle_discard_into_deck(self):
        # Move some cards to discard first
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.DISCARD_HAND, ["Copper"]))
        self.engine.apply(Action(ActionType.SHUFFLE, []))
        summary = self.engine.summary()
        self.assertEqual(summary["discard"].get("Copper", 0), 0)
        self.assertEqual(summary["deck"]["Copper"], 7)

    def test_discard_whole_hand(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper", "Estate"]))
        self.engine.apply(Action(ActionType.DISCARD_WHOLE_HAND, []))
        summary = self.engine.summary()
        self.assertEqual(len(summary["hand"]), 0)
        self.assertEqual(summary["discard"]["Copper"], 1)
        self.assertEqual(summary["discard"]["Estate"], 1)

    def test_discard_whole_played(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.PLAY, ["Copper"]))
        self.engine.apply(Action(ActionType.DISCARD_WHOLE_PLAYED, []))
        summary = self.engine.summary()
        self.assertEqual(len(summary["played"]), 0)
        self.assertEqual(summary["discard"]["Copper"], 1)

    def test_gain_cards(self):
        self.engine.apply(Action(ActionType.GAIN, ["Gold", "Gold"]))
        summary = self.engine.summary()
        self.assertEqual(summary["discard"]["Gold"], 2)

    def test_trash_cards(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper"]))
        self.engine.apply(Action(ActionType.TRASH, ["Copper"]))
        summary = self.engine.summary()
        self.assertNotIn("Copper", summary["hand"])
        # trashed cards are removed from hand and not added anywhere else

    def test_end_turn(self):
        self.engine.apply(Action(ActionType.DRAW, ["Copper", "Estate"]))
        self.engine.apply(Action(ActionType.PLAY, ["Copper"]))
        self.engine.apply(Action(ActionType.END_TURN, []))
        summary = self.engine.summary()
        self.assertEqual(len(summary["hand"]), 0)
        self.assertEqual(len(summary["played"]), 0)
        self.assertEqual(summary["discard"]["Copper"], 1)
        self.assertEqual(summary["discard"]["Estate"], 1)

    def test_invalid_move_logs_warning(self):
        # Trying to play a card not in hand raises InvalidCardMove internally and logs a warning
        with self.assertLogs('dominion_tracker.engine', level='WARNING') as log:
            self.engine.apply(Action(ActionType.PLAY, ["Gold"]))  # Not in hand
            self.assertTrue(any("Invalid move" in message for message in log.output))

    def test_unknown_action_raises(self):
        class FakeActionType:
            UNKNOWN = "unknown"

        with self.assertRaises(ValueError):
            self.engine.apply(Action(FakeActionType.UNKNOWN, []))


if __name__ == "__main__":
    unittest.main()
