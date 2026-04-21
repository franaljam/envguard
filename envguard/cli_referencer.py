"""cli_referencer.py – CLI sub-command: envguard reference <key> <files...>"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envguard.referencer import find_references


def cmd_reference(args: argparse.Namespace) -> int:
    """Entry-point for the *reference* sub-command.

    Exit codes:
        0 – key referenced in at least one file (or --warn-unused not set)
        1 – key not referenced anywhere (only when --warn-unused is given)
        2 – usage / file-not-found error
    """
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"error: file not found: {p}", file=sys.stderr)
        return 2

    result = find_references(args.key, paths)
    print(result.summary())

    if args.warn_unused and not result.found():
        return 1
    return 0


def register_reference_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "reference",
        help="Find .env files that reference a specific key via $KEY or ${KEY}.",
    )
    p.add_argument("key", help="The env key to search for references to.")
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to scan.",
    )
    p.add_argument(
        "--warn-unused",
        action="store_true",
        default=False,
        help="Exit with code 1 when the key is not referenced anywhere.",
    )
    p.set_defaults(func=cmd_reference)
