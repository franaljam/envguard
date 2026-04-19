"""CLI subcommand: score"""
from __future__ import annotations
import argparse
from envguard.parser import parse_env_file
from envguard.scorer import score_env
from envguard.reporter import _colored


def cmd_score(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error: {exc}")
        return 2

    result = score_env(env)

    for b in result.breakdowns:
        status = "OK" if b.score == b.max_score else "WARN"
        color = "green" if status == "OK" else "yellow"
        label = _colored(f"[{status}]", color)
        print(f"  {label} {b.category}: {b.score}/{b.max_score}")
        if args.verbose:
            for note in b.notes:
                print(f"       - {note}")

    grade_color = "green" if result.grade in ("A", "B") else ("yellow" if result.grade == "C" else "red")
    print("  " + _colored(result.summary(), grade_color))

    return 0


def register_score_parser(subparsers) -> None:
    p = subparsers.add_parser("score", help="Score a .env file for quality")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show per-issue notes")
    p.set_defaults(func=cmd_score)
