"""CLI sub-command: envguard value-diff <left.env> <right.env>"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.differ_values import diff_values
from envguard.parser import parse_env_file


def cmd_value_diff(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Cannot read {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Cannot read {args.right}: {exc}", file=sys.stderr)
        return 2

    ignore: List[str] = args.ignore or []
    result = diff_values(
        left,
        right,
        ignore_keys=ignore if ignore else None,
        case_insensitive=args.case_insensitive,
    )

    if not result.has_changes():
        print(result.summary())
        return 0

    for change in result.removed():
        print(f"  - {change.key}={change.old!r}")
    for change in result.added():
        print(f"  + {change.key}={change.new!r}")
    for change in result.modified():
        print(f"  ~ {change.key}: {change.old!r} -> {change.new!r}")

    print()
    print(result.summary())
    return 1


def register_value_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p: argparse.ArgumentParser = subparsers.add_parser(
        "value-diff",
        help="Show value-level differences between two .env files.",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Target .env file")
    p.add_argument(
        "--ignore",
        metavar="KEY",
        nargs="+",
        default=[],
        help="Keys to exclude from comparison",
    )
    p.add_argument(
        "--case-insensitive",
        action="store_true",
        default=False,
        help="Treat values as equal when they differ only in case",
    )
    p.set_defaults(func=cmd_value_diff)
