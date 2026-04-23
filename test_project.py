import pytest
from unittest.mock import patch

from project import find_player, validate_gameweek, format_player_stats


BOOTSTRAP = {
    "elements": [
        {"id": 1, "first_name": "Mohamed", "second_name": "Salah", "web_name": "Salah", "team": 10, "element_type": 3},
        {"id": 2, "first_name": "Erling", "second_name": "Haaland", "web_name": "Haaland", "team": 13, "element_type": 4},
    ],
    "events": [{"id": i} for i in range(1, 39)],
    "teams": [
        {"id": 10, "name": "Liverpool"},
        {"id": 13, "name": "Manchester City"},
    ],
}

GW_STATS = {
    "round": 10, "opponent_team": 13, "was_home": True,
    "minutes": 90, "goals_scored": 2, "assists": 1,
    "clean_sheets": 0, "goals_conceded": 2, "own_goals": 0,
    "penalties_saved": 0, "penalties_missed": 0, "yellow_cards": 0,
    "red_cards": 0, "saves": 0, "bonus": 3, "bps": 42,
    "influence": "58.4", "creativity": "32.1", "threat": "76.0",
    "ict_index": "16.6", "expected_goals": "1.85", "expected_assists": "0.42",
    "expected_goal_involvements": "2.27", "expected_goals_conceded": "1.10",
    "total_points": 18,
}


def test_find_player():
    assert find_player("Salah", BOOTSTRAP)["id"] == 1
    assert find_player("salah", BOOTSTRAP)["id"] == 1
    assert find_player("  Haaland  ", BOOTSTRAP)["id"] == 2
    with pytest.raises(ValueError, match="No player found"):
        find_player("Ronaldo", BOOTSTRAP)
    with pytest.raises(ValueError, match="matched multiple players"):
        find_player("a", BOOTSTRAP)


def test_validate_gameweek():
    validate_gameweek(1, BOOTSTRAP)
    validate_gameweek(38, BOOTSTRAP)
    with pytest.raises(ValueError, match="between 1 and 38"):
        validate_gameweek(0, BOOTSTRAP)
    with pytest.raises(ValueError, match="between 1 and 38"):
        validate_gameweek(39, BOOTSTRAP)


def test_format_player_stats():
    player = BOOTSTRAP["elements"][0]
    rows = format_player_stats(player, GW_STATS, BOOTSTRAP)
    row_dict = {r[0]: r[1] for r in rows}
    assert row_dict["Player"] == "Mohamed Salah"
    assert row_dict["Position"] == "MID"
    assert row_dict["Team"] == "Liverpool"
    assert row_dict["Opponent"] == "Manchester City"
    assert row_dict["Goals Scored"] == 2
    assert row_dict["Total FPL Points"] == 18
