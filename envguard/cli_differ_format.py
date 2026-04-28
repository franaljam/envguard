"""CLI sub-command: format-diff — detect .env formatting differences."""
from __future__ import annotations

import argparse
import sys

from envguard.differ_format import diff_format


def cmd_format_diff(args: argparse.Namespace) -> int:
    try:
        result = diff_format(args.left, args.right)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(result.summary)

    if result.has_changes:
        if args.verbose:
            for change in result.changes:
                parts = []
                if change.quote_changed:
                    parts.append(
                        f"quote: {change.left_quote!r} -> {change.right_quote!r}"
                    )
                if change.spacing_changed:
                    parts.append(
                        f"spacing: {change.left_spacing!r} -> {change.right_spacing!r}"
                    )
                print(f"  {change.key}: {', '.join(parts)}")
        return 1
    return 0


def register_format_diff_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    p = subparsers.add_parser(
        "format-diff",
        help="Detect formatting differences (quoting, spacing) between two .env files.",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Comparison .env file")
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-key detail.",
    )
    p.set_defaults(func=cmd_format_diff)
