"""CLI sub-command: compress — remove redundant keys from a .env file."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envguard.parser import parse_env_file
from envguard.compressor import compress_env


def cmd_compress(args: argparse.Namespace) -> None:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    explicit: Optional[List[str]] = (
        [k.strip() for k in args.remove.split(",")] if args.remove else None
    )

    result = compress_env(
        env,
        remove_duplicates=not args.no_dedup,
        remove_interpolated=not args.no_interp,
        explicit_keys=explicit,
    )

    print(result.summary())

    if args.show:
        print()
        for k, v in result.compressed.items():
            print(f"{k}={v}")

    sys.exit(1 if result.changed() else 0)


def register_compress_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "compress",
        help="Remove redundant or derivable keys from a .env file.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--no-dedup",
        action="store_true",
        default=False,
        help="Disable removal of keys with duplicate values.",
    )
    p.add_argument(
        "--no-interp",
        action="store_true",
        default=False,
        help="Disable removal of keys that are pure variable references.",
    )
    p.add_argument(
        "--remove",
        default="",
        metavar="KEY1,KEY2",
        help="Comma-separated list of keys to explicitly remove.",
    )
    p.add_argument(
        "--show",
        action="store_true",
        default=False,
        help="Print the compressed env to stdout.",
    )
    p.set_defaults(func=cmd_compress)
