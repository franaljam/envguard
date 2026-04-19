"""CLI command: snapshot-diff — compare two saved snapshots."""
from __future__ import annotations

import argparse
import sys

from envguard.snapshot import load_snapshot
from envguard.differ_summary import diff_snapshots


def cmd_snapshot_diff(args: argparse.Namespace) -> int:
    try:
        base = load_snapshot(args.base)
        head = load_snapshot(args.head)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        return 2

    result = diff_snapshots(base, head, ignore_values=args.ignore_values)

    print(f"Comparing '{result.base_label}' → '{result.head_label}'")

    if not result.has_changes:
        print("No changes detected.")
        return 0

    if result.added:
        print(f"\nAdded ({len(result.added)}):")
        for entry in result.added:
            print(f"  + {entry.key}={entry.new_value}")

    if result.removed:
        print(f"\nRemoved ({len(result.removed)}):")
        for entry in result.removed:
            print(f"  - {entry.key}={entry.old_value}")

    if result.modified:
        print(f"\nModified ({len(result.modified)}):")
        for entry in result.modified:
            print(f"  ~ {entry.key}: '{entry.old_value}' → '{entry.new_value}'")

    return 1


def register_snapshot_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "snapshot-diff",
        help="Diff two saved env snapshots.",
    )
    p.add_argument("base", help="Path to base snapshot JSON file.")
    p.add_argument("head", help="Path to head snapshot JSON file.")
    p.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only compare keys, ignore value changes.",
    )
    p.set_defaults(func=cmd_snapshot_diff)
