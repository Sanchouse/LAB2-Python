from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .errors import validation

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
ERROR_LEVELS = ("ERROR", "CRITICAL")
REQUIRED_FIELDS = ("timestamp", "level", "source", "message")


@dataclass(frozen=True)
class Event:
    """Class for working with data"""
    timestamp: datetime
    level: str
    source: str
    message: str


def parse_timestamp(timestamp: Any) -> datetime:
    """Checks the correctness of the time and converts it into a datetime object"""
    try:
        timestamp = datetime.fromisoformat(timestamp.strip())
        if timestamp > datetime.now(timezone.utc):
                validation("FUTURE")
    except ValueError:
        validation("INCORRECT TIME")
    return timestamp


def event_from_dict(timestamp, level, source, message) -> Event:
    """Create Event object from line"""
    if level not in REQUIRED_FIELDS:
        validation("MISSING FIELD")

    if level not in LEVELS:
        validation("INCORRECT LEVEL", level)

    return Event(
        timestamp=parse_timestamp(timestamp),
        level=level,
        source=source,
        message=message,
    )