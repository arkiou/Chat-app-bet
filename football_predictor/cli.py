"""Command line interface for the football predictor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .data_loader import load_matches_from_csv
from .predictor import MatchPredictor, PredictionRequest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate win/draw/loss, goal-goal, halftime and over/under probabilities "
            "for an upcoming football match based on historical data."
        )
    )
    parser.add_argument("data", type=Path, help="Path to the matches CSV file")
    parser.add_argument("home", help="Name of the home team")
    parser.add_argument("away", help="Name of the away team")
    parser.add_argument(
        "--line",
        type=float,
        default=2.5,
        help="Over/under goal line (default: 2.5)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    matches = load_matches_from_csv(args.data)
    predictor = MatchPredictor(matches)
    prediction = predictor.predict(
        PredictionRequest(
            home_team=args.home,
            away_team=args.away,
            over_under_line=args.line,
        )
    )

    output: Dict[str, Any] = {
        "home_team": args.home,
        "away_team": args.away,
        "over_under_line": args.line,
        "probabilities": {
            "home_win": _to_serializable(prediction.home_win),
            "draw": _to_serializable(prediction.draw),
            "away_win": _to_serializable(prediction.away_win),
            "goal_goal": _to_serializable(prediction.goal_goal),
            "halftime_home_win": _to_serializable(prediction.halftime_home_win),
            "halftime_draw": _to_serializable(prediction.halftime_draw),
            "halftime_away_win": _to_serializable(prediction.halftime_away_win),
            "over": _to_serializable(prediction.over),
            "under": _to_serializable(prediction.under),
        },
        "sample_sizes": prediction.sample_sizes,
    }

    if args.pretty:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(output, ensure_ascii=False))
    return 0


def _to_serializable(breakdown) -> Dict[str, Any]:
    return {
        "value": round(breakdown.value, 4),
        "contributors": {
            key: {
                "value": (round(value, 4) if value >= 0 else None),
                "sample_size": count,
            }
            for key, (value, count) in breakdown.contributors.items()
        },
    }


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
