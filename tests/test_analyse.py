import csv
import json
import os
from dataclasses import dataclass

import pytest

import streamstats.errors as err
from streamstats.analysis import analyze_files
from streamstats.report import build_report


@dataclass(frozen=True)
class DataForTests:
    command: str
    inputs: str
    format_of_file: str
    output: str
    skip: bool


LINES_1 = [
    {"timestamp":"2026-10-07T09:06:00+00:00","level":"INFO","source":"web","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"INFO","source":"loader","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"WARNING","source":"web","message":"ok"}
]

LINES_2 = [
    {"timestamp":"2026-10-07T09:06:00+00:00","level":"DEBUG","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"ERROR","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"CRITICAL","source":"web","message":"ok"}
]

BAD_LINES_TIME_1 = [
    {"timestamp":"2027-10-07T09:06:00+00:00","level":"DEBUG","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"ERROR","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"CRITICAL","source":"web","message":"ok"}
]

BAD_LINES_TIME_2 = [
    {"timestamp":"2026-10-07T25:06:00+00:00","level":"DEBUG","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"ERROR","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"CRITICAL","source":"web","message":"ok"}
]

INC_LINES_1 = [
    {"timestamp":"2026-10-07T09:06:00+00:00","level":"INFO","source":"","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"INFO","source":"loader","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"WARNING","source":"web","message":"ok"}
]

INC_LINES_2 = [
    {"timestamp":"2026-10-07T09:06:00+00:00","level":"info","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:07:15+00:00","level":"ERROR","source":"parser","message":"ok"},
    {"timestamp":"2026-10-07T09:08:00+00:00","level":"CRITICAL","source":"web","message":"ok"}
]

FIELDS = ["timestamp", "level", "source", "message"]


def write_jsonl(path, lines):
    with open(path, "w", encoding="utf-8") as jsonl_file:
            jsonl_file.writelines(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in lines)

def write_csv(path, lines):
    with open(path, "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(lines)


def remove_file(path):
    pass

class TestAnalyse:
    def test_for_one_jsonl_without_skips(self):
        write_jsonl("tests/data1.jsonl", LINES_1)

        args = DataForTests(command='analyze', inputs=['tests/data1.jsonl'], format_of_file='jsonl', output=None, skip=False)
        stats = analyze_files(args.inputs, args.format_of_file, args.skip)
        report = build_report(stats, args.skip)

        os.remove("tests/data1.jsonl")
        assert report == {'total_events': 3, 'levels': {'INFO': 2, 'WARNING': 1}, 'sources': {'web': 2, 'loader': 1}, 'first_timestamp': '2026-10-07T09:06:00+00:00', 'last_timestamp': '2026-10-07T09:08:00+00:00'}


    def test_for_two_jsonl_with_skips(self):
        write_jsonl("tests/data1.jsonl", LINES_1)
        write_jsonl("tests/data2.jsonl", LINES_2)
                
        args = DataForTests(command='analyze', inputs=['tests/data1.jsonl', 'tests/data2.jsonl'], format_of_file='jsonl', output=None, skip=True)
        stats = analyze_files(args.inputs, args.format_of_file, args.skip)
        report = build_report(stats, args.skip)

        os.remove("tests/data1.jsonl")
        os.remove("tests/data2.jsonl")
        assert report == {'total_events': 6, 'levels': {'INFO': 2, 'WARNING': 1, 'DEBUG': 1, 'ERROR': 1, 'CRITICAL': 1}, 'sources': {'web': 3, 'loader': 1, 'parser': 2}, 'top_error_sources': [{'source': 'parser', 'count': 1}, {'source': 'web', 'count': 1}], 'first_timestamp': '2026-10-07T09:06:00+00:00', 'last_timestamp': '2026-10-07T09:08:00+00:00', 'skipped_invalid': 2}


    def test_for_one_csv_without_skips(self):
        write_csv("tests/data1.csv", LINES_1)
                
        args = DataForTests(command='analyze', inputs=['tests/data1.csv'], format_of_file='csv', output=None, skip=False)
        stats = analyze_files(args.inputs, args.format_of_file, args.skip)
        report = build_report(stats, args.skip)

        os.remove("tests/data1.csv")
        assert report == {'total_events': 3, 'levels': {'INFO': 2, 'WARNING': 1}, 'sources': {'web': 2, 'loader': 1}, 'first_timestamp': '2026-10-07T09:06:00+00:00', 'last_timestamp': '2026-10-07T09:08:00+00:00'}

    def test_for_two_csv_with_skips(self):
        write_csv("tests/data1.csv", LINES_1)
        write_csv("tests/data2.csv", LINES_2)
                
        args = DataForTests(command='analyze', inputs=['tests/data1.csv', "tests/data2.csv"], format_of_file='csv', output=None, skip=True)
        stats = analyze_files(args.inputs, args.format_of_file, args.skip)
        report = build_report(stats, args.skip)

        os.remove("tests/data1.csv")
        os.remove("tests/data2.csv")
        assert report == {'total_events': 6, 'levels': {'INFO': 2, 'WARNING': 1, 'DEBUG': 1, 'ERROR': 1, 'CRITICAL': 1}, 'sources': {'web': 3, 'loader': 1, 'parser': 2}, 'top_error_sources': [{'source': 'parser', 'count': 1}, {'source': 'web', 'count': 1}], 'first_timestamp': '2026-10-07T09:06:00+00:00', 'last_timestamp': '2026-10-07T09:08:00+00:00', 'skipped_invalid': 2}

    def test_for_csv_without_skips_and_errors(self):
        write_csv("tests/data1.csv", LINES_2)
        write_csv("tests/data2.csv", LINES_2)

        with pytest.raises(err.ErrorOrWarningLevelError):
            args = DataForTests(command='analyze', inputs=['tests/data1.csv', "tests/data2.csv"], format_of_file='csv', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.csv")
        os.remove("tests/data2.csv")

    def test_for_jsonl_without_skips_and_errors(self):
        write_jsonl("tests/data1.jsonl", LINES_1)
        write_jsonl("tests/data2.jsonl", LINES_2)
                

        with pytest.raises(err.ErrorOrWarningLevelError):
            args = DataForTests(command='analyze', inputs=['tests/data1.jsonl', 'tests/data2.jsonl'], format_of_file='jsonl', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.jsonl")
        os.remove("tests/data2.jsonl")

    def test_with_future_date(self):
        write_jsonl("tests/data1.jsonl", BAD_LINES_TIME_1)

        with pytest.raises(err.IncorrectDateError):
            args = DataForTests(command='analyze', inputs=['tests/data1.jsonl'], format_of_file='jsonl', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.jsonl")

    def test_with_incorrect_timestamp(self):
        write_csv("tests/data1.csv", BAD_LINES_TIME_2)

        with pytest.raises(err.IncorrectDateError):
            args = DataForTests(command='analyze', inputs=['tests/data1.csv'], format_of_file='csv', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.csv")

    def test_with_different_types_of_file(self):
        write_csv("tests/data1.csv", LINES_1)
        
        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.csv'], format_of_file='jsonl', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.csv")

    def test_with_unknown_type_of_file(self):
        write_jsonl("tests/data1.jsonl", LINES_2)
        
        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.jsonl'], format_of_file='json', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.jsonl")


    def test_with_empty_file(self):
        write_jsonl("tests/data1.jsonl", [])
        
        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.jsonl'], format_of_file='json', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.jsonl")

    def test_with_incorrect_source(self):
        write_jsonl("tests/data1.jsonl", INC_LINES_1)

        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.jsonl'], format_of_file='jsonl', output=None, skip=False)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.jsonl")


    def test_with_incorrect_level(self):
        write_csv("tests/data1.csv", INC_LINES_2)

        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.csv'], format_of_file='csv', output=None, skip=True)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.csv")

    def test_with_incorrect_unicode(self):
        with open("tests/data1.csv", "w", encoding="utf-16") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(LINES_1)

        with pytest.raises(err.StreamStatsError):
            args = DataForTests(command='analyze', inputs=['tests/data1.csv'], format_of_file='csv', output=None, skip=True)
            analyze_files(args.inputs, args.format_of_file, args.skip)
        os.remove("tests/data1.csv")

    