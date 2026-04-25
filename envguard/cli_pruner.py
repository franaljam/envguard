"""CLI sub-command: prune — remove keys from a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.pruner import prune_env


def cmd_prune(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    keys: List[str] = args.key or []
    prefixes: List[str] = args.prefix or []
    patterns: List[str] = args.pattern or []

    result = prune_env(
        env,
        keys=keys or None,
        prefixes=prefixes or None,
        patterns=patterns or None,
        empty_only=args.empty_only,
    )

    print(result.summary())

    if args.verbose and result.removed:
        for k in result.removed:
            print(f"  - {k}")

    return 1 if result.changed() else 0


def register_prune_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "prune",
        help="Remove keys from a .env file by name, prefix, or pattern.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--key", metavar="KEY", action="append",
        help="Exact key to remove (repeatable).",
    )
    p.add_argument(
        "--prefix", metavar="PREFIX", action="append",
        help="Remove all keys with this prefix (repeatable).",
    )
    p.add_argument(
        "--pattern", metavar="GLOB", action="append",
        help="Remove keys matching this glob pattern (repeatable).",
    )
    p.add_argument(
        "--empty-only", action="store_true",
        help="Only remove a key when its value is empty.",
    )
    p.add_argument(
        "--verbose", "-v", action="store_true",
        help="List each removed key.",
    )
    p.set_defaults(func=cmd_prune)
