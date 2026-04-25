"""CLI sub-command: type-diff — compare env files with type-aware reporting."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.differ_types import diff_types
from envguard.parser import parse_env_file


def cmd_type_diff(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read {args.left}: {exc}", file=sys.stderr)
        return 2

    try:
        right = parse_env_file(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read {args.right}: {exc}", file=sys.stderr)
        return 2

    result = diff_types(left, right)

    if args.verbose:
        for key in result.added:
            print(f"  [+] {key} ({right[key]!r})  type={_infer_label(right[key])}")
        for key in result.removed:
            print(f"  [-] {key} ({left[key]!r})  type={_infer_label(left[key])}")
        for change in result.type_changes():
            print(
                f"  [T] {change.key}: "
                f"{change.left_type}({change.left_value!r}) -> "
                f"{change.right_type}({change.right_value!r})"
            )
        for change in result.value_changes():
            print(
                f"  [~] {change.key}: "
                f"{change.left_value!r} -> {change.right_value!r} "
                f"(type: {change.left_type})"
            )

    print(result.summary())

    if args.types_only and not result.type_changes():
        return 0

    return 1 if result.has_changes() else 0


def _infer_label(value: str) -> str:
    from envguard.differ_types import _infer_type
    return _infer_type(value)


def register_type_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "type-diff",
        help="diff two .env files with type-aware change detection",
    )
    p.add_argument("left", help="base .env file")
    p.add_argument("right", help="target .env file")
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="show per-key details",
    )
    p.add_argument(
        "--types-only",
        action="store_true",
        help="exit 1 only when type changes are present (ignore value-only changes)",
    )
    p.set_defaults(func=cmd_type_diff)
