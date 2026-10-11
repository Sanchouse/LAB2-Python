import argparse
import json
import logging
import sys

from .analysis import analyze_files
from .report import build_report

parser = argparse.ArgumentParser(
    prog="python -m streamstats",
    description="Запись логов"
)

commands = parser.add_subparsers(
    dest="command",
    required=True
)

analyze_parser = commands.add_parser(
    "analyze",
    help=""
)

analyze_parser.add_argument(
    "inputs",
    nargs="+",
    metavar="INPUT",
    help="Один или несколько файлов",
)

analyze_parser.add_argument(
    "--format",
    required=True,
    metavar="{csv,jsonl}",
    help="Формат входных файлов"
)

analyze_parser.add_argument(
    "--output",
    required=False,
    help="куда сохранить JSON-отчёт; если не указан, отчёт печатается в stdout"
)

analyze_parser.add_argument(
    "--skip-invalid",
    required=False,
    action="store_true",
    help="пропускать ошибочные строки (WARNING в лог, число пропусков в отчёт)"
)


def main():
    logger = logging.getLogger("streamstats.analysis")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(handler)

    try:
        args = parser.parse_args()
        stats = analyze_files(args.inputs, args.format, args.skip_invalid, logger)
        
        if args.skip_invalid:
            report = build_report(stats, skips=True)
        else:
            report = build_report(stats, skips=False)
        if args.output == None:
            with open("../data/REPORT.json", "w", encoding="utf-8") as json_file:
                json.dump(report, json_file, indent=4)
        else:
            with open(f"../data/{args.output}", "w", encoding="utf-8") as json_file:
                json.dump(report, json_file, indent=4)
        return 0
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 2
    except TypeError as e:
        sys.stderr.write(f"{e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())