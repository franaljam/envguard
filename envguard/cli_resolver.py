"""CLI command for resolving .env variable references."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.resolver import resolve_env


def cmd_resolve(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"[error] File not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    defaults: dict = {}
    for item in args.default or []:
        if "=" in item:
            k, v = item.split("=", 1)
            defaults[k.strip()] = v.strip()
        else:
            print(f"[warn] Ignoring malformed default '{item}'", file=sys.stderr)

    result = resolve_env(
        env,
        fallback_to_os=not args.no_os,
        defaults=defaults,
        strict=args.strict,
    )

    if args.verbose:
        for entry in result.entries.values():
            if entry.original != entry.resolved:
                print(f"  {entry.key}: {entry.original!r} -> {entry.resolved!r}")
                if entry.sources:
                    print(f"    sources: {', '.join(entry.sources)}")

    print(result.summary())

    if result.unresolved:
        print("Unresolved references:", ", ".join(result.unresolved), file=sys.stderr)
        return 1

    return 0


def register_resolve_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("resolve", help="Resolve variable references in a .env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--default",
        metavar="KEY=VALUE",
        action="append",
        help="Fallback default value (repeatable)",
    )
    p.add_argument(
        "--no-os",
        action="store_true",
        help="Do not fall back to OS environment variables",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any reference is unresolved",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Show resolved values")
    p.set_defaults(func=cmd_resolve)
