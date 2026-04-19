"""CLI subcommand: key-diff — show added, removed, and renamed keys between two .env files."""
from __future__ import annotations
import argparse
from envguard.parser import parse_env_file
from envguard.differ_keys import diff_keys


def cmd_key_diff(args: argparse.Namespace) -> int:
    try:
        base = parse_env_file(args.base)
        target = parse_env_file(args.target)
    except Exception as exc:
        print(f"Error: {exc}")
        return 2

    result = diff_keys(
        base,
        target,
        detect_renames=not args.no_renames,
        rename_threshold=args.rename_threshold,
    )

    if result.renamed:
        print("Renamed keys:")
        for old, new in result.renamed:
            print(f"  {old} -> {new}")

    if result.added:
        print("Added keys:")
        for k in result.added:
            print(f"  + {k}")

    if result.removed:
        print("Removed keys:")
        for k in result.removed:
            print(f"  - {k}")

    print()
    print(result.summary())
    return 1 if result.has_changes() else 0


def register_key_diff_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("key-diff", help="Show added, removed, and renamed keys")
    p.add_argument("base", help="Base .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument(
        "--no-renames",
        action="store_true",
        default=False,
        help="Disable rename detection",
    )
    p.add_argument(
        "--rename-threshold",
        type=float,
        default=0.7,
        metavar="FLOAT",
        help="Similarity threshold for rename detection (default: 0.7)",
    )
    p.set_defaults(func=cmd_key_diff)
