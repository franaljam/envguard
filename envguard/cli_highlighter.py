"""CLI sub-command: highlight — mark env keys matching given criteria."""
from __future__ import annotations

import argparse
import sys

from envguard.parser import parse_env_file, EnvParseError
from envguard.highlighter import highlight_env


def cmd_highlight(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = highlight_env(
        env,
        prefixes=args.prefix or None,
        patterns=args.pattern or None,
        exact=args.key or None,
    )

    print(result.summary())

    if args.verbose and result.highlighted:
        for k in result.highlighted:
            print(f"  {k} = {env[k]}")

    return 1 if result.count() > 0 else 0


def register_highlight_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "highlight",
        help="Highlight env keys matching prefixes, patterns, or exact names.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--prefix", metavar="PREFIX", action="append",
        help="Highlight keys starting with PREFIX (repeatable).",
    )
    p.add_argument(
        "--pattern", metavar="REGEX", action="append",
        help="Highlight keys matching REGEX (repeatable).",
    )
    p.add_argument(
        "--key", metavar="KEY", action="append",
        help="Highlight exact KEY (repeatable).",
    )
    p.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print key=value pairs for highlighted keys.",
    )
    p.set_defaults(func=cmd_highlight)
