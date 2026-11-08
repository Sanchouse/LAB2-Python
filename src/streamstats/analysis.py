from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .errors import validation
from .models import ERROR_LEVELS, Event
from .parsers import iter_csv, iter_jsonl, parser


@dataclass
class Stats:
    """Сollects statistics on input files"""
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
        """Return top-5 error sources"""
        ordered = sorted(self.error_sources.items(), key=lambda item: (-item[1], item[0]))
        return [{"source": name, "count": count} for name, count in ordered[:n]]


def parse_timestamp(timestamp: Any) -> datetime:
    """Checks the correctness of the time and converts it into a datetime object"""
    timestamp = datetime.fromisoformat(timestamp.strip())
    if timestamp > datetime.now(timezone.utc):
        raise ValueError
    return timestamp


def analyze_files(inputs: list, format_of_file: str, skip: bool, logger=None) -> Stats:
    """Reads each input file one by one."""
    stats = Stats()
    for i in range(len(inputs)):
        if format_of_file != "csv" and format_of_file != "jsonl":
            validation("UNKNOWN TYPE", format_of_file)
        if format_of_file != inputs[i].split(".")[-1]:
            validation("DIFFERENT TYPES", format_of_file, inputs[i].split(".")[-1])
        if format_of_file == "csv":
            
            reader = iter_csv(inputs[i])
            for number_of_row, row in reader:
                if row == "ERROR":
                    if not skip:
                        raise validation("INCORRECT DATA")
                    else:
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"Incorrect line {number_of_row} if file {inputs[i]}.")
                    continue
                try:
                    timestamp = parse_timestamp(row.get("timestamp"))
                except ValueError:
                    if skip:
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"Incorrect line {number_of_row} if file {inputs[i]}.")
                        continue
                    validation("INCORRECT TIME")
                if row.get("level") not in ERROR_LEVELS:
                    
                    stats = stats + parser(timestamp, row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                else:
                    if not skip:
                        validation(f"{row.get("level")}", inputs[i], number_of_row, i+1)
                    else:
                        stats = stats + parser(timestamp, row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"File {inputs[i]} [{i+1}] has {row.get("level")} in row {number_of_row}.")
                
                

        if format_of_file == "jsonl":
            reader = iter_jsonl(inputs[i])
            for number_of_row, row in reader:
                if row == "ERROR":
                    if not skip:
                        raise validation("INCORRECT DATA")
                    else:
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"Incorrect line {number_of_row} if file {inputs[i]}.")
                    continue
                try:
                    timestamp = parse_timestamp(row.get("timestamp"))
                except ValueError:
                    if skip:
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"Incorrect line {number_of_row} if file {inputs[i]}.")
                        continue
                    validation("INCORRECT TIME")
                if row.get("level") not in ERROR_LEVELS:
                    stats = stats + parser(timestamp, row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                else:
                    if not skip:
                        validation(f"{row.get("level")}", inputs[i], number_of_row, i+1)
                    else:
                        stats = stats + parser(timestamp, row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"File {inputs[i]} [{i+1}] has {row.get("level")} in row {number_of_row}.")

    return stats
