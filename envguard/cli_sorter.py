"""CLI sub-command: sort"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from envguard.parser import parse_env_file
from envguard.sorter import sort_env


def cmd_sort(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error reading {args.file}: {exc}", file=sys.stderr)
        return 2

    groups = args.group or []
    result = sort_env(env, reverse=args.reverse, groups=groups)

    if not result.changed():
        print("Already sorted.")
        return 0

    lines = [f"{k}={result.sorted_env[k]}" for k in result.order]
    output = "\n".join(lines) + "\n"

    if args.inplace:
        Path(args.file).write_text(output)
        print(f"Sorted {len(result.order)} keys in {args.file}")
    else:
        print(output, end="")

    return 0


def register_sort_parser(subparsers) -> None:
    p = subparsers.add_parser("sort", help="Sort .env file keys")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--reverse", action="store_true", help="Sort descending")
    p.add_argument("--inplace", "-i", action="store_true", help="Write sorted file back")
    p.add_argument("--group", action="append", metavar="PREFIX",
                   help="Key prefix group (can repeat); grouped keys sort first")
    p.set_defaults(func=cmd_sort)
