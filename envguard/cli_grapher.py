"""CLI subcommand: graph — visualise env variable dependency graph."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from envguard.parser import parse_env_file, EnvParseError
from envguard.grapher import build_graph


def cmd_graph(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = build_graph(env)
    print(f"Graph summary: {result.summary()}")

    if args.verbose:
        if result.edges:
            print("\nDependencies:")
            for key, deps in sorted(result.edges.items()):
                print(f"  {key} -> {', '.join(deps)}")
        else:
            print("No inter-variable references found.")

    if result.has_cycles():
        print("\nCycles detected:", file=sys.stderr)
        for cycle in result.cycles:
            print(f"  {' -> '.join(cycle)}", file=sys.stderr)
        return 1

    return 0


def register_graph_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("graph", help="Build variable reference dependency graph")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show dependency edges")
    p.set_defaults(func=cmd_graph)
