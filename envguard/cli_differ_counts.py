"""CLI command for count-based env diff."""
from __future__ import annotations
import argparse
import sys
from envguard.parser import parse_env_file
from envguard.differ_counts import diff_counts


def cmd_count_diff(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:
        print(f"Error reading {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:
        print(f"Error reading {args.right}: {exc}", file=sys.stderr)
        return 2

    result = diff_counts(left, right)
    print(result.summary())

    if args.verbose and result.has_changes():
        if result.left_only:
            print("  Removed keys: " + ", ".join(sorted(result.left_only)))
        if result.right_only:
            print("  Added keys:   " + ", ".join(sorted(result.right_only)))
        if result.shared:
            print(f"  Common keys:  {result.common}")

    return 1 if result.has_changes() else 0


def register_count_diff_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "count-diff",
        help="Compare key counts between two .env files.",
    )
    p.add_argument("left", help="Base .env file.")
    p.add_argument("right", help="Target .env file.")
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show added/removed key names.",
    )
    p.set_defaults(func=cmd_count_diff)
