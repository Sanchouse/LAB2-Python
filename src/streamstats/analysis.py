from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

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


"""def iter_csv(stats:Stats, path:str, skip:bool, number_of_file:int, logger:Logger) -> None:
    "Reads the csv file."
    try:
        with Path(path).open(encoding="utf-8", newline="") as file:
            for number_of_row, row in enumerate(csv.DictReader(file), start=1):
                try:
                    
                except KeyError:
                    validation("INCORRECT FIELDS")
    except FileNotFoundError:
        validation("MISSING FILE", path)
    except UnicodeDecodeError:
        validation("UNICODE ERROR", path)


def iter_jsonl(stats:Stats, path:str, skip:bool, number_of_file:int, logger=None) -> None:
    """"Reads the JSONL file."""""
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
        validation("UNICODE ERROR", path)"""


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
                if row.get("level") not in ERROR_LEVELS:
                    stats = stats + parser(row.get("timestamp"), row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                else:
                    if not skip:
                        validation(f"{row.get("level")}", inputs[i], number_of_row, i+1)
                    else:
                        stats = stats + parser(row.get("timestamp"), row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"File {inputs[i]} [{i+1}] has {row.get("level")} in row {number_of_row}.")
        if format_of_file == "jsonl":
            reader = iter_jsonl(inputs[i])
            for number_of_row, row in reader:
                if row.get("level") not in ERROR_LEVELS:
                    stats = stats + parser(row.get("timestamp"), row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                else:
                    if not skip:
                        validation(f"{row.get("level")}", inputs[i], number_of_row, i+1)
                    else:
                        stats = stats + parser(row.get("timestamp"), row.get("level"), row.get("source"), row.get("message"), number_of_row, inputs[i])
                        stats.skipped += 1
                        if logger:
                            logger.warning(f"File {inputs[i]} [{i+1}] has {row.get("level")} in row {number_of_row}.")

    return stats
