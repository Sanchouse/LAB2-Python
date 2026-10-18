import csv
import json
from pathlib import Path

from .errors import validation
from .models import Event, event_from_dict


def parser(timestamp: str, level: str, source: str, message: str, number_of_row:int, path:str) -> Event:
    """Checks each parameter for errors and returns an Event object."""
    if source.strip() == "":
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


def iter_csv(path):
    try:
        with Path(path).open(encoding="utf-8", newline="") as file:
            try:
                reader = csv.DictReader(file)
            except UnicodeDecodeError:
                validation("UNICODE ERROR", path)
            for row in reader:
                yield reader.line_num, row
    except FileNotFoundError:
        validation("MISSING FILE", path)



def iter_jsonl(path):
    try:
        with Path(path).open(encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    yield number, validation("INCORRECT READ", path)
                    continue
                except UnicodeEncodeError:
                    yield number, validation("UNICODE ERROR", path)
                    continue
                yield number, value
    except FileNotFoundError:
        validation("MISSING FILE", path)
