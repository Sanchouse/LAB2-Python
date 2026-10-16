import csv
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from pathlib import Path
from io import StringIO

from .errors import validation
from .models import ERROR_LEVELS, Event
from .parsers import parser


@dataclass
class Stats:
    total_events: int = 0
    levels: Counter = field(default_factory=Counter)
    sources: Counter = field(default_factory=Counter)
    error_sources: Counter = field(default_factory=Counter)
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    skipped: int = 0

    def __add__(self, other: Event):
        self.total_events += 1
        self.levels[other.level] += 1
        self.sources[other.source] += 1
        if other.level in ERROR_LEVELS:
            self.error_sources[other.source] += 1
        if not self.first_timestamp:
            self.first_timestamp = other.timestamp
            self.last_timestamp = other.timestamp
        elif other.timestamp < self.first_timestamp:
            self.first_timestamp = other.timestamp
        elif other.timestamp > self.last_timestamp:
            self.last_timestamp = other.timestamp
        return self

    def top_error_sources(self, n: int=5) -> list[dict]:
        ordered = sorted(self.error_sources.items(), key=lambda item: (-item[1], item[0]))
        return [{"source": name, "count": count} for name, count in ordered[:n]]


def iter_csv(stats:Stats, path:str, skip:bool, number_of_file:int, logger:Logger):
    try:
        with Path(path).open(encoding="utf-8", newline="") as file:
            for number_of_row, row in enumerate(csv.DictReader(file), start=1):
                try:
                    if row["level"] not in ERROR_LEVELS:
                        stats = stats + parser(row["timestamp"], row["level"], row["source"], row["message"], number_of_row, path)
                    else:
                        if not skip:
                            validation(f"{row["level"]}", path, number_of_row, number_of_file)
                        else:
                            stats = stats + parser(row["timestamp"], row["level"], row["source"], row["message"], number_of_row, path)
                            stats.skipped += 1
                            if logger:
                                logger.warning(f"File {path} [{number_of_file}] has {row["level"]} in row {number_of_row}.")
                except KeyError:
                    validation("INCORRECT FIELDS")
    except FileNotFoundError:
        validation("MISSING FILE", path)
    except UnicodeDecodeError:
        validation("UNICODE ERROR", path)


def iter_jsonl(stats:Stats, path:str, skip:bool, number_of_file:int, logger=None):
    try:
        with Path(path).open(encoding="utf-8", newline="") as file:
            for number_of_row, row in enumerate(file):
                try:
                    row = row.strip()
                    if not row:
                        validation("EMPTY ROW", number_of_row+1)
                    try:
                        value = json.loads(row)
                    except json.JSONDecodeError:
                        validation("INCORRECT READ", path)
                    if value["level"] not in ERROR_LEVELS:
                        stats = stats + parser(value["timestamp"], value["level"], value["source"], value["message"], number_of_row, path)
                    else:
                        if not skip:
                            validation(f"{value["level"]}", path, number_of_row, number_of_file)
                        else:
                            stats = stats + parser(value["timestamp"], value["level"], value["source"], value["message"], number_of_row, path)
                            stats.skipped += 1
                            if logger:
                                logger.warning(f"File {path} [{number_of_file}] has {value["level"]} in row {number_of_row}.")
                except KeyError:
                    validation("INCORRECT FIELDS")
    except FileNotFoundError:
        validation("MISSING FILE", path)
    except UnicodeDecodeError:
        validation("UNICODE ERROR", path)


def analyze_files(inputs: list, format_of_file: str, skip: bool, logger=None):
    stats = Stats()
    for i in range(len(inputs)):
        if format_of_file != "csv" and format_of_file != "jsonl":
            validation("UNKNOWN TYPE", format_of_file)
        if format_of_file != inputs[i].split(".")[-1]:
            validation("DIFFERENT TYPES", format_of_file, inputs[i].split(".")[-1])
        if format_of_file == "csv":
            iter_csv(stats, inputs[i], skip, i, logger)
        if format_of_file == "jsonl":
            iter_jsonl(stats, inputs[i], skip, i, logger)

    return stats
