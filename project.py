"""
FPL Gameweek Player Stats
Fetches and displays Fantasy Premier League player statistics for a given gameweek.
"""

import sys
import requests
from tabulate import tabulate

# ── API endpoints ──────────────────────────────────────────────────────────────
BASE_URL = "https://fantasy.premierleague.com/api"
BOOTSTRAP_URL = f"{BASE_URL}/bootstrap-static/"
PLAYER_URL = f"{BASE_URL}/element-summary/{{player_id}}/"

# ── Position / team helpers ────────────────────────────────────────────────────
POSITION_MAP = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────


def main():
    print("=" * 50)
    print("  FPL Gameweek Player Stats")
    print("=" * 50)

    player_name = prompt_player_name()
    gameweek = prompt_gameweek()

    print("\nFetching FPL data…")
    bootstrap = fetch_bootstrap()

    # Validate gameweek range
    try:
        validate_gameweek(gameweek, bootstrap)
    except ValueError as exc:
        sys.exit(f"Error: {exc}")

    # Find player
    try:
        player = find_player(player_name, bootstrap)
    except ValueError as exc:
        sys.exit(f"Error: {exc}")

    # Fetch per-GW stats
    gw_stats = fetch_player_gameweek_stats(player["id"], gameweek)

    if gw_stats is None:
        full_name = f"{player['first_name']} {player['second_name']}"
        sys.exit(
            f"No data found for {full_name} in Gameweek {gameweek}. "
            "The gameweek may not have been played yet, or the player did not feature."
        )

    rows = format_player_stats(player, gw_stats, bootstrap)
    full_name = f"{player['first_name']} {player['second_name']}"
    display_stats(rows, title=f"{full_name}  ·  Gameweek {gameweek}")


def fetch_bootstrap():
    """
    Fetch the FPL bootstrap-static endpoint.

    Returns the parsed JSON dict on success.
    Raises SystemExit with a friendly message on network / HTTP errors.
    """
    try:
        response = requests.get(BOOTSTRAP_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        sys.exit(
            "Error: Could not connect to the FPL API. Check your internet connection.")
    except requests.exceptions.Timeout:
        sys.exit("Error: The FPL API request timed out. Please try again.")
    except requests.exceptions.HTTPError as exc:
        sys.exit(f"Error: HTTP {exc.response.status_code} from FPL API.")


def find_player(name, bootstrap_data):
    """
    Search for a player by name (case-insensitive, partial match on web_name,
    first_name, or second_name).

    Parameters
    ----------
    name : str
        The player name to search for (e.g. "Salah", "Mo Salah").
    bootstrap_data : dict
        Parsed bootstrap-static JSON.

    Returns
    -------
    dict
        The matching player element dict.

    Raises
    ------
    ValueError
        If no player is found or the search is ambiguous (multiple matches).
    """
    name_lower = name.strip().lower()
    elements = bootstrap_data.get("elements", [])

    matches = [
        p for p in elements
        if (
            name_lower in p.get("web_name", "").lower()
            or name_lower in p.get("first_name", "").lower()
            or name_lower in p.get("second_name", "").lower()
            or name_lower in f"{p.get('first_name', '')} {p.get('second_name', '')}".lower()
        )
    ]

    if not matches:
        raise ValueError(
            f"No player found matching '{name}'. Check the spelling and try again.")

    if len(matches) > 1:
        names = ", ".join(
            f"{p['first_name']} {p['second_name']} ({p.get('web_name', '')})"
            for p in matches[:10]
        )
        raise ValueError(
            f"'{name}' matched multiple players: {names}. "
            "Please be more specific."
        )

    return matches[0]


def validate_gameweek(gameweek, bootstrap_data):
    """
    Validate that *gameweek* is an integer in the range [1, total_events].

    Parameters
    ----------
    gameweek : int
        The gameweek number to validate.
    bootstrap_data : dict
        Parsed bootstrap-static JSON (used to determine the season's total GWs).

    Raises
    ------
    ValueError
        If the gameweek is out of the valid range.
    """
    events = bootstrap_data.get("events", [])
    total = len(events)
    if total == 0:
        total = 38  # fallback for a standard PL season

    if not (1 <= gameweek <= total):
        raise ValueError(
            f"Gameweek must be between 1 and {total}. You entered {gameweek}."
        )


def fetch_player_gameweek_stats(player_id, gameweek):
    """
    Fetch per-gameweek stats for a specific player.

    Parameters
    ----------
    player_id : int
        The FPL element ID of the player.
    gameweek : int
        The gameweek to retrieve stats for.

    Returns
    -------
    dict or None
        The history dict for the requested gameweek, or None if the gameweek
        has not yet been played.

    Raises
    ------
    SystemExit
        On network / HTTP errors.
    """
    url = PLAYER_URL.format(player_id=player_id)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        sys.exit(
            "Error: Could not connect to the FPL API. Check your internet connection.")
    except requests.exceptions.Timeout:
        sys.exit("Error: The FPL API request timed out. Please try again.")
    except requests.exceptions.HTTPError as exc:
        sys.exit(
            f"Error: HTTP {exc.response.status_code} when fetching player data.")

    history = data.get("history", [])
    for entry in history:
        if entry.get("round") == gameweek:
            return entry

    return None  # GW not yet played


def format_player_stats(player, gw_stats, bootstrap_data):
    """
    Transform raw player and gameweek dicts into a list of [label, value] rows
    ready for tabulation.

    Parameters
    ----------
    player : dict
        Player element dict from bootstrap-static.
    gw_stats : dict
        Gameweek history entry from the element-summary endpoint.
    bootstrap_data : dict
        Full bootstrap-static dict (used to resolve team names).

    Returns
    -------
    list[list]
        A list of [label, value] pairs.
    """
    teams = {t["id"]: t["name"] for t in bootstrap_data.get("teams", [])}
    opponent_id = gw_stats.get("opponent_team")
    opponent = teams.get(opponent_id, str(opponent_id))
    position = POSITION_MAP.get(player.get("element_type"), "UNK")
    was_home = gw_stats.get("was_home", False)
    venue = "Home" if was_home else "Away"

    rows = [
        ["Player",
            f"{player.get('first_name', '')} {player.get('second_name', '')}"],
        ["Web Name",            player.get("web_name", "")],
        ["Position",            position],
        ["Team",                teams.get(
            player.get("team"), str(player.get("team")))],
        ["Gameweek",            gw_stats.get("round", "")],
        ["Opponent",            opponent],
        ["Venue",               venue],
        ["Minutes Played",      gw_stats.get("minutes", 0)],
        ["Goals Scored",        gw_stats.get("goals_scored", 0)],
        ["Assists",             gw_stats.get("assists", 0)],
        ["Clean Sheets",        gw_stats.get("clean_sheets", 0)],
        ["Goals Conceded",      gw_stats.get("goals_conceded", 0)],
        ["Own Goals",           gw_stats.get("own_goals", 0)],
        ["Penalties Saved",     gw_stats.get("penalties_saved", 0)],
        ["Penalties Missed",    gw_stats.get("penalties_missed", 0)],
        ["Yellow Cards",        gw_stats.get("yellow_cards", 0)],
        ["Red Cards",           gw_stats.get("red_cards", 0)],
        ["Saves",               gw_stats.get("saves", 0)],
        ["Bonus Points",        gw_stats.get("bonus", 0)],
        ["BPS",                 gw_stats.get("bps", 0)],
        ["Influence",           gw_stats.get("influence", "N/A")],
        ["Creativity",          gw_stats.get("creativity", "N/A")],
        ["Threat",              gw_stats.get("threat", "N/A")],
        ["ICT Index",           gw_stats.get("ict_index", "N/A")],
        ["xG",                  gw_stats.get("expected_goals", "N/A")],
        ["xA",                  gw_stats.get("expected_assists", "N/A")],
        ["xGI",                 gw_stats.get(
            "expected_goal_involvements", "N/A")],
        ["xGC",                 gw_stats.get(
            "expected_goals_conceded", "N/A")],
        ["Total FPL Points",    gw_stats.get("total_points", 0)],
    ]
    return rows


def display_stats(rows, title=""):
    """
    Print a formatted table of player stats to the terminal.

    Parameters
    ----------
    rows : list[list]
        Two-column [label, value] rows as returned by format_player_stats.
    title : str, optional
        Optional heading printed above the table.
    """
    if title:
        print(f"\n{'─' * 50}")
        print(f"  {title}")
        print(f"{'─' * 50}")

    print(
        tabulate(
            rows,
            headers=["Stat", "Value"],
            tablefmt="rounded_outline",
            colalign=("left", "right"),
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# Input helpers
# ──────────────────────────────────────────────────────────────────────────────

def prompt_player_name():
    """Prompt the user for a player name, stripping whitespace."""
    name = input("Enter player name: ").strip()
    if not name:
        sys.exit("Error: Player name cannot be empty.")
    return name


def prompt_gameweek():
    """Prompt the user for a gameweek number and parse it as an integer."""
    raw = input("Enter gameweek (1–38): ").strip()
    try:
        gw = int(raw)
    except ValueError:
        sys.exit(f"Error: '{raw}' is not a valid gameweek number.")
    return gw


if __name__ == "__main__":
    main()
