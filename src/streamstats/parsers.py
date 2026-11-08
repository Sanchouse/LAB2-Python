import csv
import json
from pathlib import Path

from .errors import validation
from .models import Event, event_from_dict


def parser(timestamp: str, level: str, source: str, message: str, number_of_row:int, path:str) -> Event:
    """Checks each parameter for errors and returns an Event object."""

    if timestamp == None:
        validation("MISSING VALUE", "timestamp", number_of_row, path)
    if level == None:
        validation("MISSING VALUE", "level", number_of_row, path)
    if source == None:
        validation("MISSING VALUE", "source", number_of_row, path)
    if message == None:
        validation("MISSING VALUE", "message", number_of_row, path)

    if source.strip() == "":
        validation("EMPTY SOURCE", number_of_row, path)

    event = event_from_dict(timestamp, level, source, message)

    return event


def iter_csv(path):
    """Reader of csv rows"""
    try:
        with Path(path).open(encoding="utf-8", newline="") as file:
            reader = csv.reader(file, delimiter=',')
            for number_of_row, row in enumerate(reader):
                if number_of_row == 0:
                    if row != ['timestamp','level','source','message']:
                        validation("INCORRECT COLUMNS", path)
                else:
                    if len(row) == 4:
                        row = {"timestamp": row[0], "level": row[1], "source": row[2], "message": row[3]}
                    elif len(row)==0:
                        continue
                    else:
                        row = "ERROR"
                    yield number_of_row, row
    except FileNotFoundError:
        validation("MISSING FILE", path)
    except UnicodeDecodeError:
        validation("UNICODE ERROR", path)
    except UnboundLocalError:
        validation("INCORECT DATA")



def iter_jsonl(path):
    """Reader of jsonl rows"""
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
    except UnicodeDecodeError:
        validation("UNICODE ERROR", path)
    except UnboundLocalError:
        validation("INCORECT DATA")