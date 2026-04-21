"""CLI sub-command: envguard strip — remove keys from a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.stripper import strip_env
from envguard.stringer import to_dotenv


def cmd_strip(args: argparse.Namespace) -> int:
    """Execute the strip sub-command."""
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = strip_env(
        env,
        keys=args.key or [],
        prefixes=args.prefix or [],
        patterns=args.pattern or [],
        invert=args.invert,
    )

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(to_dotenv(result.stripped))
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    else:
        print(to_dotenv(result.stripped))

    if not args.quiet:
        print(result.summary(), file=sys.stderr)

    return 1 if result.changed() else 0


def register_strip_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "strip",
        help="Remove keys from a .env file by name, prefix, or pattern.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument("-k", "--key", action="append", metavar="KEY",
                   help="Exact key to strip (repeatable).")
    p.add_argument("-p", "--prefix", action="append", metavar="PREFIX",
                   help="Strip keys starting with PREFIX (repeatable).")
    p.add_argument("-r", "--pattern", action="append", metavar="REGEX",
                   help="Strip keys matching REGEX (repeatable).")
    p.add_argument("--invert", action="store_true",
                   help="Keep only matched keys instead of removing them.")
    p.add_argument("-o", "--output", metavar="FILE",
                   help="Write result to FILE instead of stdout.")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress summary message.")
    p.set_defaults(func=cmd_strip)
