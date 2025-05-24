import unittest
from dominion_tracker.parser import Parser
from dominion_tracker.engine import Action

class TestParser(unittest.TestCase):
    def test_parse_game_log(self):
        parser = Parser(player_id="O")
        actions = []

        with open("sample_logs/game_log.txt") as f:
            for line in f:
                action = parser.parse_line(line)
                if action:
                    actions.append(action)

        # Check that at least some actions were parsed
        self.assertTrue(len(actions) > 0, "No actions parsed from game_log.txt")

        # Check all actions belong to player O (if you store player info in Action)
        # Assuming Action has attribute player_id; adjust if different
        for action in actions:
            # If your Action class does not include player info, skip this check
            if hasattr(action, "player_id"):
                self.assertEqual(action.player_id, "O")

if __name__ == "__main__":
    unittest.main()
