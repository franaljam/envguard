"""CLI sub-command: envguard length-diff <left> <right>"""
from __future__ import annotations

import argparse
import sys

from envguard.differ_length import diff_lengths
from envguard.parser import parse_env_file


def cmd_length_diff(args: argparse.Namespace) -> int:
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

    result = diff_lengths(left, right, min_delta=args.min_delta)

    print(result.summary())

    if args.verbose and result.has_changes():
        for c in result.changes:
            l_str = str(c.left_length) if c.left_length is not None else "—"
            r_str = str(c.right_length) if c.right_length is not None else "—"
        delta_str = ""
        if c.delta is not None:
            sign = "+" if c.delta >= 0 else ""
            delta_str = f"  (delta: {sign}{c.delta})"
        print(f"  {c.direction:10s}  {c.key}: {l_str} → {r_str}{delta_str}")

    return 1 if result.has_changes() else 0


def register_length_diff_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "length-diff",
        help="Compare value lengths between two .env files.",
    )
    p.add_argument("left", help="Baseline .env file.")
    p.add_argument("right", help="Target .env file.")
    p.add_argument(
        "--min-delta",
        type=int,
        default=0,
        metavar="N",
        help="Only report changes where |delta| >= N (default: 0).",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-key length details.",
    )
    p.set_defaults(func=cmd_length_diff)
