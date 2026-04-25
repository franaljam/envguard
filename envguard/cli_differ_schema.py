"""CLI command: envguard schema-diff — schema-aware env diff."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from envguard.parser import parse_env_file
from envguard.differ_schema import diff_schema
from envguard.schema_loader import load_schema


def cmd_schema_diff(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:
        print(f"error: cannot read {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:
        print(f"error: cannot read {args.right}: {exc}", file=sys.stderr)
        return 2

    schema_fields = {}
    if args.schema:
        try:
            schema_result = load_schema(args.schema)
            schema_fields = {f.name: f for f in schema_result.fields}
        except Exception as exc:
            print(f"error: cannot load schema {args.schema}: {exc}", file=sys.stderr)
            return 2

    result = diff_schema(left, right, schema_fields=schema_fields)
    print(result.summary())

    if args.verbose:
        for entry in result.entries:
            if entry.value_changed or entry.validity_changed:
                lv = entry.left_value if entry.left_value is not None else "<missing>"
                rv = entry.right_value if entry.right_value is not None else "<missing>"
                flags = []
                if not entry.left_valid:
                    flags.append("left-invalid")
                if not entry.right_valid:
                    flags.append("right-invalid")
                flag_str = f"  [{', '.join(flags)}]" if flags else ""
                print(f"  {entry.key}: {lv!r} -> {rv!r}{flag_str}")

    regressions = result.validity_regressions()
    if regressions and not args.no_fail_on_regression:
        print(
            f"\n{len(regressions)} validity regression(s) detected.",
            file=sys.stderr,
        )
        return 1

    return 1 if result.has_changes() else 0


def register_schema_diff_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "schema-diff",
        help="Schema-aware diff of two .env files",
    )
    p.add_argument("left", help="Base .env file")
    p.add_argument("right", help="Target .env file")
    p.add_argument("--schema", metavar="FILE", help="Schema file (JSON or YAML)")
    p.add_argument("--verbose", "-v", action="store_true", help="Show per-key changes")
    p.add_argument(
        "--no-fail-on-regression",
        action="store_true",
        help="Do not exit 1 on validity regressions",
    )
    p.set_defaults(func=cmd_schema_diff)
