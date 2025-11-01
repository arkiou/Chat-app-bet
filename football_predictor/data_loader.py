"""Utilities for loading match history data from CSV files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class MatchResult:
    """Represents a single football match result."""

    date: datetime
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    home_ht_goals: int
    away_ht_goals: int
    competition: str | None = None

    @property
    def total_goals(self) -> int:
        return self.home_goals + self.away_goals

    @property
    def total_ht_goals(self) -> int:
        return self.home_ht_goals + self.away_ht_goals

    @property
    def home_win(self) -> bool:
        return self.home_goals > self.away_goals

    @property
    def draw(self) -> bool:
        return self.home_goals == self.away_goals

    @property
    def away_win(self) -> bool:
        return self.away_goals > self.home_goals

    @property
    def both_teams_score(self) -> bool:
        return self.home_goals > 0 and self.away_goals > 0

    @property
    def halftime_home_win(self) -> bool:
        return self.home_ht_goals > self.away_ht_goals

    @property
    def halftime_draw(self) -> bool:
        return self.home_ht_goals == self.away_ht_goals

    @property
    def halftime_away_win(self) -> bool:
        return self.away_ht_goals > self.home_ht_goals


def _parse_int(value: str, *, field: str) -> int:
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid integer for {field!r}: {value!r}") from exc


def load_matches_from_csv(path: str | Path) -> List[MatchResult]:
    """Load match history data from a CSV file.

    The CSV is expected to have the following columns:

    ``date`` (YYYY-MM-DD), ``home_team``, ``away_team``, ``home_goals``,
    ``away_goals``, ``home_ht_goals``, ``away_ht_goals`` and an optional
    ``competition`` column.
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    results: List[MatchResult] = []
    with file_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required_fields = {
            "date",
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
            "home_ht_goals",
            "away_ht_goals",
        }
        missing = required_fields - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )

        for row in reader:
            competition = row.get("competition")
            results.append(
                MatchResult(
                    date=datetime.strptime(row["date"], "%Y-%m-%d"),
                    home_team=row["home_team"].strip(),
                    away_team=row["away_team"].strip(),
                    home_goals=_parse_int(row["home_goals"], field="home_goals"),
                    away_goals=_parse_int(row["away_goals"], field="away_goals"),
                    home_ht_goals=_parse_int(
                        row["home_ht_goals"], field="home_ht_goals"
                    ),
                    away_ht_goals=_parse_int(
                        row["away_ht_goals"], field="away_ht_goals"
                    ),
                    competition=competition.strip() if competition else None,
                )
            )
    return results


def filter_matches(matches: Iterable[MatchResult], *, team: str, venue: str) -> List[MatchResult]:
    """Filter matches for a specific team and venue.

    Parameters
    ----------
    matches:
        Iterable of :class:`MatchResult`.
    team:
        Team name to filter.
    venue:
        ``"home"`` for matches where the team played at home,
        ``"away"`` for matches where the team played away.
    """

    team_lower = team.lower()
    if venue == "home":
        return [m for m in matches if m.home_team.lower() == team_lower]
    if venue == "away":
        return [m for m in matches if m.away_team.lower() == team_lower]
    raise ValueError("venue must be either 'home' or 'away'")


def head_to_head(matches: Iterable[MatchResult], team_a: str, team_b: str) -> List[MatchResult]:
    team_a_lower = team_a.lower()
    team_b_lower = team_b.lower()
    return [
        m
        for m in matches
        if {
            m.home_team.lower(),
            m.away_team.lower(),
        }
        == {team_a_lower, team_b_lower}
    ]
