"""CLI command: envguard trace — find usages of env keys in source files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.tracer import trace_env


def cmd_trace(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2

    extensions = args.ext.split(",") if args.ext else None
    result = trace_env(env, args.paths, extensions=extensions)

    if args.verbose:
        for entry in result.entries:
            print(f"{entry.key}  {entry.file}:{entry.line}  {entry.context}")
    else:
        print(result.summary())

    missing = [k for k in env if k not in result.found_keys()]
    if missing and args.warn_unused:
        print("\nUnused keys:", file=sys.stderr)
        for k in sorted(missing):
            print(f"  {k}", file=sys.stderr)

    return 1 if (args.warn_unused and missing) else 0


def register_trace_parser(subparsers) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "trace", help="Trace env variable usages in source files"
    )
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("paths", nargs="+", help="Source paths or directories to search")
    p.add_argument("--ext", default="", help="Comma-separated file extensions, e.g. .py,.sh")
    p.add_argument("--verbose", action="store_true", help="Show each individual match")
    p.add_argument("--warn-unused", action="store_true", help="Exit 1 if any keys have no usages")
    p.set_defaults(func=cmd_trace)
