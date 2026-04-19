"""CLI commands for freeze and thaw-check."""
from __future__ import annotations

import argparse
import sys

from envguard.freezer import compare_freeze, freeze_env, load_freeze, save_freeze
from envguard.parser import parse_env_file


def cmd_freeze(args: argparse.Namespace) -> int:
    env = parse_env_file(args.env_file)
    baseline = freeze_env(env)
    save_freeze(baseline, args.output)
    print(f"Frozen {len(baseline)} keys to {args.output}")
    return 0


def cmd_thaw_check(args: argparse.Namespace) -> int:
    env = parse_env_file(args.env_file)
    baseline = load_freeze(args.freeze_file)
    result = compare_freeze(env, baseline)
    print(result.summary())
    if args.verbose and not result.is_frozen():
        for k in result.thawed:
            print(f"  CHANGED : {k}")
        for k in result.added:
            print(f"  ADDED   : {k}")
        for k in result.removed:
            print(f"  REMOVED : {k}")
    return 0 if result.is_frozen() else 1


def register_freeze_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("freeze", help="Freeze current env into a checksum baseline")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("-o", "--output", default=".env.freeze", help="Output freeze file")
    p.set_defaults(func=cmd_freeze)


def register_thaw_check_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("thaw-check", help="Check env against frozen baseline")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("freeze_file", help="Path to freeze file")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_thaw_check)
