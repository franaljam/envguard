"""CLI command: envguard encoding-diff — compare encoding characteristics."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.differ_encoding import diff_encoding


def cmd_encoding_diff(args: argparse.Namespace) -> int:
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

    result = diff_encoding(left, right)

    if not result.has_changes():
        print("No encoding differences detected.")
        return 0

    print(result.summary())

    if args.verbose:
        print()
        for change in result.changes:
            _print_change(change)

    return 1


def _print_change(change) -> None:
    print(f"  Key : {change.key}")
    if change.left_value is not None:
        print(f"    left  escapes    : {change.left_escapes or 'none'}")
        print(f"    left  non-ascii  : {change.left_non_ascii}")
    if change.right_value is not None:
        print(f"    right escapes    : {change.right_escapes or 'none'}")
        print(f"    right non-ascii  : {change.right_non_ascii}")


def register_encoding_diff_parser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "encoding-diff",
        help="Compare encoding characteristics (escape sequences, non-ASCII) between two .env files.",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Target .env file")
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-key encoding details.",
    )
    p.set_defaults(func=cmd_encoding_diff)
