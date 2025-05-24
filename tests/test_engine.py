import unittest
from dominion_tracker.engine import GameEngine, Action, ActionType


class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_draw(self):
        self.engine.state.deck["Copper"] = 7
        self.engine.state.deck["Estate"] = 3
        action = Action(ActionType.DRAW, ["Copper", "Copper", "Estate"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.hand["Copper"], 2)
        self.assertEqual(self.engine.state.hand["Estate"], 1)
        self.assertEqual(self.engine.state.deck["Copper"], 5)
        self.assertEqual(self.engine.state.deck["Estate"], 2)

    def test_play(self):
        # Move cards to hand first
        self.engine.state.hand["Copper"] = 3
        action = Action(ActionType.PLAY, ["Copper", "Copper"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.hand["Copper"], 1)
        self.assertEqual(self.engine.state.in_play["Copper"], 2)

    def test_discard_hand(self):
        self.engine.state.hand["Estate"] = 2
        action = Action(ActionType.DISCARD_HAND, ["Estate"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.hand["Estate"], 1)
        self.assertEqual(self.engine.state.discard["Estate"], 1)

    def test_discard_played(self):
        self.engine.state.in_play["Copper"] = 2
        action = Action(ActionType.DISCARD_PLAYED, ["Copper"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.in_play["Copper"], 1)
        self.assertEqual(self.engine.state.discard["Copper"], 1)

    def test_shuffle(self):
        self.engine.state.discard["Estate"] = 2
        action = Action(ActionType.SHUFFLE, ["Estate", "Estate"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.discard["Estate"], 0)
        self.assertEqual(self.engine.state.deck["Estate"], 2)

    def test_gain(self):
        action = Action(ActionType.GAIN, ["Village"])
        self.engine.apply(action)
        self.assertEqual(self.engine.state.discard["Village"], 1)

    def test_invalid_move(self):
        # Trying to play a card not in hand
        action = Action(ActionType.PLAY, ["Silver"])
        with self.assertLogs(level='INFO') as cm:
            self.engine.apply(action)
        # Check that the state has not changed for Silver
        self.assertEqual(self.engine.state.hand.get("Silver", 0), 0)
        self.assertEqual(self.engine.state.in_play.get("Silver", 0), 0)


if __name__ == "__main__":
    unittest.main()
