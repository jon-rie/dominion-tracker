import pytest
from unittest.mock import mock_open, patch
from dominion_tracker.engine import Action, ActionType
from dominion_tracker.parser import Parser, read_events, singularize


MOCK_CSV = "Name\nCopper\nEstate\nSilver\nVillage\nThrone Room\n"

@pytest.fixture
def mocked_parser():
    with patch("builtins.open", mock_open(read_data=MOCK_CSV)):
        parser = Parser("P1", card_csv_path="fake.csv")
    return parser


def test_singularize_cases():
    assert singularize("parties") == "party"
    assert singularize("coppers") == "copper"
    assert singularize("kiss") == "kiss"


def test_extract_single_and_multi_word_cards(mocked_parser):
    text = "P1 draws a copper and a throne room."
    cards = mocked_parser.extract_cards(text)
    assert cards == ["Copper", "Throne Room"]


def test_parse_event_draw(mocked_parser):
    event = "P1 draws 2 coppers and an estate"
    action = mocked_parser.parse_event(event)
    assert action.type == ActionType.DRAW
    assert action.cards == ["Copper", "Copper", "Estate"]


def test_parse_event_play(mocked_parser):
    event = "P1 plays a throne room and a village"
    action = mocked_parser.parse_event(event)
    assert action.type == ActionType.PLAY
    assert action.cards == ["Throne Room", "Village"]


def test_parse_event_gain(mocked_parser):
    event = "P1 gains a silver"
    action = mocked_parser.parse_event(event)
    assert action.type == ActionType.GAIN
    assert action.cards == ["Silver"]


def test_parse_event_shuffle(mocked_parser):
    event = "P1 shuffles their deck"
    action = mocked_parser.parse_event(event)
    assert action.type == ActionType.SHUFFLE
    assert action.cards == []


def test_parse_event_trash(mocked_parser):
    event = "P1 trashes 1 copper"
    action = mocked_parser.parse_event(event)
    assert action.type == ActionType.TRASH
    assert action.cards == ["Copper"]


def test_parse_event_none(mocked_parser):
    event = "P2 draws a copper"  # Not for P1
    action = mocked_parser.parse_event(event)
    assert action is None
