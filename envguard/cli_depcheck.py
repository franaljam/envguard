"""CLI subcommand: depcheck — detect broken variable references in a .env file."""
from __future__ import annotations
import argparse
import sys

from envguard.parser import parse_env_file
from envguard.depcheck import check_dependencies


def cmd_depcheck(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    result = check_dependencies(env)

    if args.verbose:
        for key, refs in result.dependencies.items():
            if refs:
                print(f"  {key} references: {', '.join(refs)}")

    print(result.summary())

    if result.has_broken():
        return 1
    return 0


def register_depcheck_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "depcheck",
        help="Detect broken variable references in a .env file",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all resolved references too",
    )
    p.set_defaults(func=lambda a: sys.exit(cmd_depcheck(a)))
