from .errors import validation
from .models import Event, event_from_dict


def parser(timestamp: str, level: str, source: str, message: str, number_of_row:int, path:str) -> Event:
    """Checks each parameter for errors and returns an Event object."""
    if source == "":
        validation("EMPTY SOURCE", number_of_row, path)
    if timestamp == None:
        validation("MISSING VALUE", "timestamp", number_of_row, path)
    if level == None:
        validation("MISSING VALUE", "level", number_of_row, path)
    if source == None:
        validation("MISSING VALUE", "source", number_of_row, path)
    if message == None:
        validation("MISSING VALUE", "message", number_of_row, path)

    event = event_from_dict(timestamp, level, source, message)

    return event