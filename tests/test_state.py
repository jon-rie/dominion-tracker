import unittest
from collections import defaultdict
from dominion_tracker.state import PlayerState, InvalidCardMove


class TestPlayerState(unittest.TestCase):

    def setUp(self):
        self.state = PlayerState()
        self.state.deck = defaultdict(int, {"Copper": 3, "Estate": 2})
        self.state.hand = defaultdict(int, {"Copper": 1, "Estate": 1})
        self.state.discard = defaultdict(int, {})
        self.state.played = defaultdict(int, {})

    def test_draw_cards(self):
        self.state.move_from_deck_to_hand(["Copper", "Estate"])
        self.assertEqual(self.state.hand["Copper"], 2)
        self.assertEqual(self.state.hand["Estate"], 2)
        self.assertEqual(self.state.deck["Copper"], 2)
        self.assertEqual(self.state.deck["Estate"], 1)

    def test_play_cards(self):
        self.state.move_from_hand_to_played(["Copper"])
        self.assertNotIn("Copper", self.state.hand)
        self.assertEqual(self.state.played["Copper"], 1)

    def test_discard_cards(self):
        self.state.move_from_hand_to_discard(["Estate"])
        self.assertNotIn("Estate", self.state.hand)
        self.assertEqual(self.state.discard["Estate"], 1)

    def test_shuffle(self):
        self.state.discard["Silver"] = 2
        self.state.move_from_discard_to_deck(["Silver", "Silver"])
        self.assertEqual(self.state.deck["Silver"], 2)
        self.assertNotIn("Silver", self.state.discard)

    def test_gain_cards(self):
        self.state.gain_cards(["Gold", "Gold", "Silver"])
        self.assertEqual(self.state.discard["Gold"], 2)
        self.assertEqual(self.state.discard["Silver"], 1)
    
    def test_move_whole_discard_to_deck(self):
        self.state.discard = defaultdict(int, {"Copper": 2, "Estate": 1})
        self.state.move_whole_discard_to_deck()
        self.assertEqual(self.state.deck["Copper"], 5)  # 3 original + 2 moved
        self.assertEqual(self.state.deck["Estate"], 3)  # 2 original + 1 moved
        self.assertEqual(len(self.state.discard), 0)

    def test_move_whole_hand_to_discard(self):
        self.state.hand = defaultdict(int, {"Copper": 1, "Estate": 2})
        self.state.move_whole_hand_to_discard()
        self.assertEqual(self.state.discard["Copper"], 1)
        self.assertEqual(self.state.discard["Estate"], 2)
        self.assertEqual(len(self.state.hand), 0)

    def test_move_whole_played_to_discard(self):
        self.state.played = defaultdict(int, {"Silver": 3})
        self.state.move_whole_played_to_discard()
        self.assertEqual(self.state.discard["Silver"], 3)
        self.assertEqual(len(self.state.played), 0)


    def test_trash_cards(self):
        self.state.hand["Silver"] = 1
        self.state.trash_cards(["Silver"])
        self.assertNotIn("Silver", self.state.hand)

    def test_invalid_move_raises(self):
        with self.assertRaises(InvalidCardMove):
            self.state.move_from_hand_to_played(["Province"])  # not in hand

    def test_summary(self):
        summary = self.state.summary()
        self.assertIn("deck", summary)
        self.assertIn("hand", summary)
        self.assertIn("discard", summary)
        self.assertIn("played", summary)

    def test_total_cards(self):
        self.state.played["Silver"] = 1
        self.state.discard["Gold"] = 2
        total = self.state.total_cards()
        self.assertEqual(total["Copper"], 4)
        self.assertEqual(total["Estate"], 3)
        self.assertEqual(total["Silver"], 1)
        self.assertEqual(total["Gold"], 2)


if __name__ == "__main__":
    unittest.main()
