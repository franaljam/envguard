"""CLI sub-command: patch — apply key-value overrides and deletions to a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.patcher import patch_env
from envguard.stringer import to_dotenv


def cmd_patch(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    set_keys = {}
    for item in args.set or []:
        if "=" not in item:
            print(f"error: --set value must be KEY=VALUE, got: {item!r}", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        set_keys[k] = v

    result = patch_env(
        env,
        set_keys=set_keys or None,
        delete_keys=args.delete or None,
    )

    if args.summary:
        print(result.summary())

    if args.output:
        try:
            with open(args.output, "w") as fh:
                fh.write(to_dotenv(result.env))
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    else:
        print(to_dotenv(result.env))

    return 1 if result.changed() else 0


def register_patch_parser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "patch",
        help="Apply key-value overrides or deletions to a .env file.",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        help="Set a key to a value (repeatable)",
    )
    p.add_argument(
        "--delete",
        metavar="KEY",
        action="append",
        help="Delete a key (repeatable)",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write patched env to FILE instead of stdout",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a human-readable summary of changes",
    )
    p.set_defaults(func=cmd_patch)
