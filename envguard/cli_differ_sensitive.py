"""CLI sub-command: sensitive-diff — diff two .env files highlighting sensitive key changes."""
from __future__ import annotations

import argparse
import sys

from envguard.parser import parse_env_file
from envguard.differ_sensitive import diff_sensitive
from envguard.reporter import _colored


def cmd_sensitive_diff(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading {args.right}: {exc}", file=sys.stderr)
        return 2

    result = diff_sensitive(left, right)

    if not result.has_changes():
        print(_colored("No differences found.", "green"))
        return 0

    print(result.summary())
    print()

    sensitive = result.sensitive_changes()
    non_sensitive = result.non_sensitive_changes()

    if sensitive:
        print(_colored(f"Sensitive changes ({len(sensitive)}):", "red"))
        for ch in sensitive:
            _print_change(ch, args.show_values)

    if non_sensitive:
        print(_colored(f"Non-sensitive changes ({len(non_sensitive)}):", "yellow"))
        for ch in non_sensitive:
            _print_change(ch, args.show_values)

    return 1


def _print_change(ch, show_values: bool) -> None:
    if ch.added:
        tag = "[+]"
        detail = f"= {ch.right!r}" if show_values else ""
    elif ch.removed:
        tag = "[-]"
        detail = f"= {ch.left!r}" if show_values else ""
    else:
        if show_values:
            detail = f"{ch.left!r} -> {ch.right!r}"
        else:
            detail = "(value changed)"
        tag = "[~]"
    print(f"  {tag} {ch.key} {detail}".rstrip())


def register_sensitive_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "sensitive-diff",
        help="Diff two .env files and highlight changes to sensitive keys.",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Target .env file")
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Print actual values in the diff output.",
    )
    p.set_defaults(func=cmd_sensitive_diff)
