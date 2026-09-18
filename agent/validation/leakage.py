from __future__ import annotations

from datetime import datetime, timezone


class LeakageError(ValueError):
    pass


def assert_no_leak(
    feature_computed_at: datetime,
    kickoff_utc: datetime,
) -> None:
    if feature_computed_at.tzinfo is None:
        feature_computed_at = feature_computed_at.replace(tzinfo=timezone.utc)
    if kickoff_utc.tzinfo is None:
        kickoff_utc = kickoff_utc.replace(tzinfo=timezone.utc)

    if feature_computed_at >= kickoff_utc:
        raise LeakageError(
            f"Feature computed at {feature_computed_at.isoformat()} "
            f"on or after kickoff {kickoff_utc.isoformat()}"
        )


def assert_before_now(timestamp: datetime) -> None:
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    if timestamp > now:
        raise LeakageError(f"Timestamp {timestamp.isoformat()} is in the future")
