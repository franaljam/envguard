"""CLI sub-command: envguard duplicates — report duplicate keys in a .env file."""
from __future__ import annotations
import argparse
import sys
from envguard.duplicates import find_duplicates


def cmd_duplicates(args: argparse.Namespace) -> int:
    try:
        result = find_duplicates(args.file)
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    print(result.summary())
    return 1 if result.has_duplicates() else 0


def register_duplicates_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "duplicates",
        help="Detect duplicate keys in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file to inspect.")
    p.set_defaults(func=cmd_duplicates)
