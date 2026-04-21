"""CLI sub-command: segment."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envguard.parser import parse_env_file
from envguard.segmenter import segment_env


def cmd_segment(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rules: dict[str, str] = {}
    for entry in args.rule or []:
        if ":" not in entry:
            print(f"error: invalid rule format (expected name:pattern): {entry}", file=sys.stderr)
            return 2
        name, _, pattern = entry.partition(":")
        rules[name.strip()] = pattern.strip()

    result = segment_env(env, rules, strip_prefix=args.strip_prefix)

    if args.json:
        output = {
            "segments": {k: dict(v) for k, v in result.segments.items()},
            "unmatched": dict(result.unmatched),
        }
        print(json.dumps(output, indent=2))
    else:
        print("Segments:")
        print(result.summary())
        if args.verbose:
            for name in result.segment_names():
                print(f"\n  [{name}]")
                for k, v in result.segments[name].items():
                    print(f"    {k}={v}")
            if result.unmatched:
                print("\n  [unmatched]")
                for k, v in result.unmatched.items():
                    print(f"    {k}={v}")

    return 0


def register_segment_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("segment", help="Segment env keys into named buckets")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--rule",
        metavar="NAME:PATTERN",
        action="append",
        help="Segment rule as name:regex (repeatable)",
    )
    p.add_argument("--strip-prefix", action="store_true", help="Strip matched pattern from key names")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("-v", "--verbose", action="store_true", help="Show keys per segment")
    p.set_defaults(func=cmd_segment)
