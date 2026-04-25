"""CLI sub-command: semantic-diff — compare two .env files semantically."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.differ_semantic import diff_semantic
from envguard.parser import parse_env_file


_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"


def _c(color: str, text: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def cmd_semantic_diff(args: argparse.Namespace) -> int:
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

    result = diff_semantic(left, right)
    use_color = not args.no_color

    if not result.has_changes():
        print("No semantic differences found.")
        return 0

    for key in result.left_only:
        print(_c(_RED, f"- {key} (removed)", use_color))

    for key in result.right_only:
        print(_c(_GREEN, f"+ {key} (added)", use_color))

    for change in result.changes:
        label = "trivial" if change.semantically_equal else "meaningful"
        type_note = ""
        if change.type_changed:
            type_note = f" [{change.left_type} -> {change.right_type}]"
        color = _YELLOW if change.semantically_equal else _RED
        print(
            _c(
                color,
                f"~ {change.key}: {change.left!r} -> {change.right!r}"
                f"  ({label}{type_note})",
                use_color,
            )
        )

    print()
    print(_c(_CYAN, result.summary(), use_color))

    if args.strict:
        return 1 if result.meaningful_changes() else 0
    return 1


def register_semantic_diff_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "semantic-diff",
        help="Compare two .env files with semantic awareness.",
    )
    p.add_argument("left", help="Base .env file.")
    p.add_argument("right", help="Target .env file.")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 only on meaningful (non-trivial) changes.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    p.set_defaults(func=cmd_semantic_diff)
