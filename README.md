# FPL Gameweek Player Stats

A CS50P final project that queries the Fantasy Premier League (FPL) API and
displays detailed player statistics for a chosen gameweek in a formatted
terminal table.

## Features

- Search for any Premier League player by name (partial, case-insensitive)
- Retrieve per-gameweek stats: goals, assists, bonus, xG, xA, ICT index, and more
- Validates player name and gameweek range with clear error messages
- Displays results in a clean, auto-scaled ASCII table (via `tabulate`)
- Fully testable — all core logic in pure functions, 30+ pytest tests included

## Requirements

- Python 3.10+
- Internet connection (FPL API)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python project.py
```

You will be prompted for:
1. **Player name** — e.g. `Salah`, `Haaland`, `Mo Salah`
2. **Gameweek** — an integer between 1 and 38

### Example session

```
==================================================
  FPL Gameweek Player Stats
==================================================
Enter player name: Salah
Enter gameweek (1–38): 10

Fetching FPL data…

──────────────────────────────────────────────────
  Mohamed Salah  ·  Gameweek 10
──────────────────────────────────────────────────
╭──────────────────────────────┬──────────────────╮
│ Stat                         │            Value │
├──────────────────────────────┼──────────────────┤
│ Player                       │    Mohamed Salah │
│ Web Name                     │            Salah │
│ Position                     │              MID │
│ Team                         │        Liverpool │
│ Gameweek                     │               10 │
│ Opponent                     │  Manchester City │
│ Venue                        │             Home │
│ Minutes Played               │               90 │
│ Goals Scored                 │                2 │
│ Assists                      │                1 │
│ ...                          │              ... │
│ Total FPL Points             │               18 │
╰──────────────────────────────┴──────────────────╯
```

## Running Tests

```bash
pytest test_project.py -v
```

## Project Structure

```
fpl_project/
├── project.py        # Main program + all core functions
├── test_project.py   # pytest test suite (30+ tests)
├── requirements.txt  # pip dependencies
└── README.md
```

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `https://fantasy.premierleague.com/api/bootstrap-static/` | Player list, team list, event list |
| `https://fantasy.premierleague.com/api/element-summary/{id}/` | Per-gameweek history for one player |

## Functions

| Function | Description |
|---|---|
| `fetch_bootstrap()` | Downloads the FPL master dataset |
| `find_player(name, data)` | Searches for a player by name with error handling |
| `validate_gameweek(gw, data)` | Checks GW is within the season range |
| `fetch_player_gameweek_stats(id, gw)` | Pulls per-GW history for a player |
| `format_player_stats(player, gw, data)` | Builds the display rows |
| `display_stats(rows, title)` | Renders the tabulate table |
| `prompt_player_name()` | Input helper |
| `prompt_gameweek()` | Input helper with int parsing |
