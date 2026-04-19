"""CLI command for grouping env variables by prefix."""
from __future__ import annotations
import argparse
from envguard.parser import parse_env_file
from envguard.grouper import group_env


def cmd_group(args: argparse.Namespace) -> int:
    env = parse_env_file(args.file)
    prefixes = args.prefix if args.prefix else None
    result = group_env(env, prefixes=prefixes, separator=args.separator)

    if args.group:
        target = result.groups.get(args.group)
        if target is None:
            print(f"Group '{args.group}' not found.")
            return 1
        for key, value in sorted(target.items()):
            print(f"{key}={value}")
        return 0

    print(result.summary())
    if args.verbose:
        for group_name in result.group_names():
            print(f"\n[{group_name}]")
            for key, value in sorted(result.groups[group_name].items()):
                print(f"  {key}={value}")
        if result.ungrouped:
            print("\n[ungrouped]")
            for key, value in sorted(result.ungrouped.items()):
                print(f"  {key}={value}")
    return 0


def register_group_parser(subparsers) -> None:
    p = subparsers.add_parser("group", help="Group env vars by prefix")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--prefix", action="append", metavar="PREFIX",
                   help="Explicit prefix (repeatable); auto-detected if omitted")
    p.add_argument("--separator", default="_", help="Prefix separator (default: _)")
    p.add_argument("--group", metavar="NAME", help="Print only keys in this group")
    p.add_argument("--verbose", "-v", action="store_true", help="Show keys per group")
    p.set_defaults(func=cmd_group)
