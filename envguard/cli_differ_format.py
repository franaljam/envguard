"""CLI sub-command: envguard format-diff

Compares formatting conventions (quoting, spacing, trailing whitespace)
between two .env files.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Dict

from envguard.differ_format import diff_format


def _parse_raw_lines(path: str) -> Dict[str, str]:
    """Read a .env file and return {key: raw_line} for non-blank, non-comment lines."""
    raw: Dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                stripped = line.rstrip("\n")
                if not stripped.strip() or stripped.strip().startswith("#"):
                    continue
                m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', stripped)
                if m:
                    raw[m.group(1)] = stripped
    except FileNotFoundError:
        print(f"[error] File not found: {path}", file=sys.stderr)
        sys.exit(2)
    return raw


def cmd_format_diff(args: argparse.Namespace) -> None:
    left_lines = _parse_raw_lines(args.left)
    right_lines = _parse_raw_lines(args.right)

    result = diff_format(left_lines, right_lines)

    if not result.has_changes():
        print("No formatting differences found.")
        sys.exit(0)

    print(result.summary())

    if args.verbose:
        print()
        for change in result.changes:
            print(f"  [{change.key}]")
            print(f"    left : {change.left_raw}")
            print(f"    right: {change.right_raw}")

    sys.exit(1)


def register_format_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "format-diff",
        help="Detect formatting differences (quoting, spacing) between two .env files.",
    )
    p.add_argument("left", help="Base .env file.")
    p.add_argument("right", help="Comparison .env file.")
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show raw lines for changed keys.",
    )
    p.set_defaults(func=cmd_format_diff)
