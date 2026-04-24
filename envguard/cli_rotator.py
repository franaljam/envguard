"""CLI sub-command: rotate — apply key rotations to a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.rotator import rotate_env
from envguard.stringer import to_dotenv


def cmd_rotate(args: argparse.Namespace) -> int:
    """Execute the rotate sub-command.

    Exit codes:
        0 — no keys were rotated
        1 — one or more keys were rotated
        2 — file not found or parse error
    """
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    replacements: dict[str, str] = {}
    for item in args.set or []:
        if "=" not in item:
            print(f"error: invalid --set value (expected KEY=VALUE): {item}", file=sys.stderr)
            return 2
        key, _, value = item.partition("=")
        replacements[key.strip()] = value

    result = rotate_env(
        env,
        replacements,
        sensitive_only=not args.all_keys,
        exclude=args.exclude or [],
    )

    print(result.summary())

    if args.output:
        text = to_dotenv(result.rotated, sort=args.sort)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Written to {args.output}")

    return 1 if result.changed() else 0


def register_rotate_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "rotate",
        help="Rotate sensitive key values in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        help="Key/value pair to rotate (repeatable).",
    )
    p.add_argument(
        "--exclude",
        metavar="KEY",
        action="append",
        help="Keys to exclude from rotation (repeatable).",
    )
    p.add_argument(
        "--all-keys",
        action="store_true",
        default=False,
        help="Rotate any key, not just sensitive ones.",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        help="Write the rotated env to this file.",
    )
    p.add_argument(
        "--sort",
        action="store_true",
        default=False,
        help="Sort keys alphabetically in the output file.",
    )
    p.set_defaults(func=cmd_rotate)
