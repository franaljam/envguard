"""CLI commands for env pinning and drift detection."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envguard.parser import parse_env_file
from envguard.pinner import save_pinfile, check_drift
from envguard.reporter import _colored


def cmd_pin(args: Namespace) -> int:
    env = parse_env_file(args.env_file)
    save_pinfile(env, args.output)
    print(f"Pinned {len(env)} variable(s) to {args.output}")
    return 0


def cmd_drift(args: Namespace) -> int:
    env = parse_env_file(args.env_file)
    result = check_drift(env, args.pinfile)

    if not result.has_drift():
        print(_colored("green", "No drift detected."))
        return 0

    print(_colored("red", "Drift detected!"))
    for key in result.drifted:
        print(f"  {_colored('yellow', '~ changed')}: {key}")
    for key in result.new_keys:
        print(f"  {_colored('green', '+ new')}: {key}")
    for key in result.removed_keys:
        print(f"  {_colored('red', '- removed')}: {key}")
    return 1


def register_pin_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser("pin", help="Pin current env values to a lockfile")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("--output", default=".env.lock", help="Output lockfile path (default: .env.lock)")
    p.set_defaults(func=cmd_pin)


def register_drift_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser("drift", help="Check env for drift against a pinfile")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("pinfile", help="Path to lockfile produced by 'pin'")
    p.set_defaults(func=cmd_drift)
