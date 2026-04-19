"""CLI command for classifying .env keys."""
from __future__ import annotations
import argparse
from envguard.parser import parse_env_file
from envguard.classifier import classify_env


def cmd_classify(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    result = classify_env(env)

    for cat in result.category_names():
        keys = result.keys_in(cat)
        print(f"[{cat}] ({len(keys)} key(s))")
        if args.verbose:
            for k in sorted(keys):
                print(f"  {k}")

    if result.uncategorized:
        print(f"[uncategorized] ({len(result.uncategorized)} key(s))")
        if args.verbose:
            for k in sorted(result.uncategorized):
                print(f"  {k}")

    return 0


def register_classify_parser(subparsers) -> None:
    p = subparsers.add_parser("classify", help="Classify .env keys into semantic categories")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show individual keys per category")
    p.set_defaults(func=cmd_classify)
