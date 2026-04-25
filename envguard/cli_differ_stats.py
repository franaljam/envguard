"""CLI command: envguard stats — show statistical diff between two .env files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.differ_stats import diff_stats


def cmd_stats(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read {args.right}: {exc}", file=sys.stderr)
        return 2

    result = diff_stats(left, right)

    print(f"Summary: {result.summary()}")
    print(f"Total keys compared: {result.total_keys}")

    if args.verbose:
        if result.added:
            print("\nAdded:")
            for k in result.added:
                print(f"  + {k}")
        if result.removed:
            print("\nRemoved:")
            for k in result.removed:
                print(f"  - {k}")
        if result.changed:
            print("\nChanged (key: left_len -> right_len):")
            for e in result.changed:
                sign = f"+{e.delta}" if e.delta >= 0 else str(e.delta)
                print(f"  ~ {e.key}: {e.left_len} -> {e.right_len} ({sign})")

    return 1 if result.has_changes else 0


def register_stats_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "stats",
        help="Show statistical diff metrics between two .env files",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Target .env file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show per-key details")
    p.set_defaults(func=cmd_stats)
