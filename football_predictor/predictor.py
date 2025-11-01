"""Core prediction logic for estimating football match probabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .data_loader import MatchResult, filter_matches, head_to_head


@dataclass(frozen=True)
class PredictionRequest:
    home_team: str
    away_team: str
    over_under_line: float = 2.5


@dataclass(frozen=True)
class ProbabilityBreakdown:
    """Keeps track of individual probability contributors."""

    contributors: Dict[str, Tuple[float, int]]

    @property
    def value(self) -> float:
        positive = [(value, count) for value, count in self.contributors.values() if value >= 0 and count > 0]
        if not positive:
            return 0.0
        weighted_sum = sum(value * count for value, count in positive)
        total = sum(count for _, count in positive)
        return weighted_sum / total


@dataclass(frozen=True)
class PredictionResult:
    home_win: ProbabilityBreakdown
    draw: ProbabilityBreakdown
    away_win: ProbabilityBreakdown
    goal_goal: ProbabilityBreakdown
    halftime_home_win: ProbabilityBreakdown
    halftime_draw: ProbabilityBreakdown
    halftime_away_win: ProbabilityBreakdown
    over: ProbabilityBreakdown
    under: ProbabilityBreakdown
    sample_sizes: Dict[str, int]


class MatchPredictor:
    """Compute match probability estimations from historical results."""

    def __init__(self, matches: Iterable[MatchResult]):
        self._matches: List[MatchResult] = list(matches)
        if not self._matches:
            raise ValueError("At least one match is required to build the predictor")

    def predict(self, request: PredictionRequest) -> PredictionResult:
        home = request.home_team
        away = request.away_team
        over_line = request.over_under_line

        home_matches = filter_matches(self._matches, team=home, venue="home")
        away_matches = filter_matches(self._matches, team=away, venue="away")
        h2h_matches = head_to_head(self._matches, home, away)

        home_outcome = self._outcome_probabilities(home_matches, perspective="home")
        away_outcome = self._outcome_probabilities(away_matches, perspective="away")
        h2h_outcome = self._outcome_probabilities(h2h_matches, perspective="home")

        goal_goal_probs = self._probability_component(
            home_matches, away_matches, h2h_matches, lambda m: m.both_teams_score
        )
        halftime_probs = {
            "home": self._probability_component(
                home_matches, away_matches, h2h_matches, lambda m: m.halftime_home_win
            ),
            "draw": self._probability_component(
                home_matches, away_matches, h2h_matches, lambda m: m.halftime_draw
            ),
            "away": self._probability_component(
                home_matches, away_matches, h2h_matches, lambda m: m.halftime_away_win
            ),
        }
        over_probs = self._probability_component(
            home_matches,
            away_matches,
            h2h_matches,
            lambda m: m.total_goals > over_line,
        )
        under_probs = self._probability_component(
            home_matches,
            away_matches,
            h2h_matches,
            lambda m: m.total_goals <= over_line,
        )

        return PredictionResult(
            home_win=self._combine_outcome(home_outcome, away_outcome, h2h_outcome, "win"),
            draw=self._combine_outcome(home_outcome, away_outcome, h2h_outcome, "draw"),
            away_win=self._combine_outcome(home_outcome, away_outcome, h2h_outcome, "loss"),
            goal_goal=goal_goal_probs,
            halftime_home_win=halftime_probs["home"],
            halftime_draw=halftime_probs["draw"],
            halftime_away_win=halftime_probs["away"],
            over=over_probs,
            under=under_probs,
            sample_sizes={
                "home_matches": len(home_matches),
                "away_matches": len(away_matches),
                "head_to_head": len(h2h_matches),
            },
        )

    def _combine_outcome(
        self,
        home_outcome: Dict[str, float],
        away_outcome: Dict[str, float],
        h2h_outcome: Dict[str, float],
        key: str,
    ) -> ProbabilityBreakdown:
        contributors = {
            "home_team": home_outcome.get(key, (-1.0, 0)),
            "away_team": away_outcome.get(key, (-1.0, 0)),
            "head_to_head": h2h_outcome.get(key, (-1.0, 0)),
        }
        return ProbabilityBreakdown(contributors)

    def _outcome_probabilities(
        self, matches: List[MatchResult], *, perspective: str
    ) -> Dict[str, Tuple[float, int]]:
        if not matches:
            return {"win": (-1.0, 0), "draw": (-1.0, 0), "loss": (-1.0, 0)}

        total = len(matches)
        if perspective == "home":
            win = sum(1 for m in matches if m.home_win)
            draw = sum(1 for m in matches if m.draw)
            loss = sum(1 for m in matches if m.away_win)
        else:
            win = sum(1 for m in matches if m.away_win)
            draw = sum(1 for m in matches if m.draw)
            loss = sum(1 for m in matches if m.home_win)

        return {
            "win": (win / total, total),
            "draw": (draw / total, total),
            "loss": (loss / total, total),
        }

    def _probability_component(
        self,
        home_matches: List[MatchResult],
        away_matches: List[MatchResult],
        h2h_matches: List[MatchResult],
        predicate,
    ) -> ProbabilityBreakdown:
        contributors: Dict[str, Tuple[float, int]] = {}

        for label, sample in (
            ("home_team", home_matches),
            ("away_team", away_matches),
            ("head_to_head", h2h_matches),
        ):
            contributors[label] = self._ratio(sample, predicate)
        return ProbabilityBreakdown(contributors)

    @staticmethod
    def _ratio(matches: List[MatchResult], predicate) -> Tuple[float, int]:
        if not matches:
            return (-1.0, 0)
        total = len(matches)
        count = sum(1 for m in matches if predicate(m))
        return (count / total, total)
