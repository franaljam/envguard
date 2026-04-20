"""CLI sub-command: inspect — show per-key metadata for a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.inspector import inspect_env


def cmd_inspect(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    result = inspect_env(env)
    print(result.summary())

    if args.verbose:
        header = f"{'KEY':<30} {'LEN':>4}  {'SENS':>4}  {'EMPTY':>5}  {'SPACE':>5}  {'NUM':>3}  {'BOOL':>4}"
        print(header)
        print("-" * len(header))
        for info in result.entries:
            flags = [
                "Y" if info.is_sensitive else "N",
                "Y" if info.is_empty else "N",
                "Y" if info.has_whitespace else "N",
                "Y" if info.is_numeric else "N",
                "Y" if info.is_boolean else "N",
            ]
            print(f"{info.key:<30} {info.length:>4}  {flags[0]:>4}  {flags[1]:>5}  {flags[2]:>5}  {flags[3]:>3}  {flags[4]:>4}")

    if args.sensitive_only:
        if result.sensitive_keys:
            print("Sensitive keys: " + ", ".join(result.sensitive_keys))
        else:
            print("No sensitive keys detected.")

    return 0


def register_inspect_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "inspect",
        help="Display per-key metadata for a .env file.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument("-v", "--verbose", action="store_true", help="Show full table.")
    p.add_argument(
        "--sensitive-only",
        action="store_true",
        help="Print only sensitive keys.",
    )
    p.set_defaults(func=cmd_inspect)
