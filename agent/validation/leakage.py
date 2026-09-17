from datetime import datetime


def assert_point_in_time(event_time: datetime, prediction_time: datetime, source_time: datetime | None) -> None:
    """Prevent post-prediction information from entering a forecast snapshot."""
    if prediction_time >= event_time:
        raise ValueError("prediction_time must be before event_time")
    if source_time is not None and source_time > prediction_time:
        raise ValueError("source contains information published after prediction_time")
