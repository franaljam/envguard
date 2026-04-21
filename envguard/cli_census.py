"""CLI sub-command: envguard census <file>"""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.census import census_env
from envguard.parser import parse_env_file, EnvParseError


def cmd_census(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = census_env(env)
    print(result.summary())

    if args.verbose:
        if result.empty:
            print("\nEmpty keys:")
            for k in result.empty:
                print(f"  {k}")

        if result.sensitive:
            print("\nSensitive keys:")
            for k in result.sensitive:
                print(f"  {k}")

        if result.boolean:
            print("\nBoolean keys:")
            for k in result.boolean:
                print(f"  {k}")

        if result.numeric:
            print("\nNumeric keys:")
            for k in result.numeric:
                print(f"  {k}")

        if result.by_prefix:
            print("\nPrefix groups:")
            for pfx, keys in sorted(result.by_prefix.items()):
                print(f"  [{pfx}] {', '.join(sorted(keys))}")

    return 0


def register_census_parser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "census",
        help="Count and categorise keys in a .env file",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-category key lists",
    )
    p.set_defaults(func=cmd_census)
