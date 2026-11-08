from dataclasses import dataclass
from datetime import datetime

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


def event_from_dict(timestamp, level, source, message) -> Event:
    """Create Event object from line"""
    if level not in REQUIRED_FIELDS:
        validation("MISSING FIELD")

    if level not in LEVELS:
        validation("INCORRECT LEVEL", level)

    return Event(
        timestamp=timestamp,
        level=level,
        source=source,
        message=message,
    )