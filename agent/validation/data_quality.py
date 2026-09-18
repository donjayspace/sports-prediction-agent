from __future__ import annotations

from typing import Iterable, Mapping

from agent.ai.schemas import ResearchRequest


class DataQualityError(ValueError):
    pass


def validate_research_request(req: ResearchRequest) -> None:
    if req.home_team == req.away_team:
        raise DataQualityError("Home and away teams must differ")
    if not req.league.strip():
        raise DataQualityError("League must be provided")
    if not req.kickoff_utc.strip():
        raise DataQualityError("Kickoff time must be provided")


def validate_feature_vector(features: Mapping[str, float]) -> None:
    missing = [k for k, v in features.items() if v is None]  # type: ignore[comparison-overlap]
    if missing:
        raise DataQualityError(f"Missing feature values: {missing}")

    for name, value in features.items():
        if not isinstance(value, (int, float)):
            raise DataQualityError(f"Feature {name} is not numeric: {type(value)}")
        if value != value:  # NaN check
            raise DataQualityError(f"Feature {name} is NaN")


def validate_no_future_leak(
    kickoff_iso: str,
    feature_timestamps: Iterable[str],
) -> None:
    for ts in feature_timestamps:
        if ts > kickoff_iso:
            raise DataQualityError(
                f"Feature timestamp {ts} is after kickoff {kickoff_iso}"
            )
