"""CLI command: envguard link – cross-file key linking report."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.linker import link_envs


def cmd_link(args: argparse.Namespace) -> int:
    named_envs = {}
    for path in args.files:
        try:
            named_envs[path] = parse_env_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not parse {path}: {exc}", file=sys.stderr)
            return 2

    result = link_envs(named_envs)
    print(result.summary())

    if args.verbose:
        shared = result.shared_keys()
        if shared:
            print("\nShared keys:")
            for key in sorted(shared):
                entry = result.entries[key]
                status = "consistent" if entry.is_consistent else "INCONSISTENT"
                print(f"  {key} [{status}]")
                for fname, val in entry.values.items():
                    print(f"    {fname}: {val}")
        else:
            print("No shared keys found.")

    inconsistent = result.inconsistent_keys()
    if inconsistent:
        if not args.verbose:
            print("Inconsistent shared keys: " + ", ".join(sorted(inconsistent)))
        return 1
    return 0


def register_link_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "link",
        help="Cross-file key linking: find shared and inconsistent keys.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Two or more .env files to link.")
    p.add_argument("-v", "--verbose", action="store_true", help="Show per-file values.")
    p.set_defaults(func=cmd_link)
