"""CLI integration for the migrator module."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from envguard.parser import parse_env_file
from envguard.migrator import migrate_env
from envguard.exporter import to_shell


def cmd_migrate(args: argparse.Namespace) -> int:
    env = parse_env_file(args.env_file)

    renames: dict = {}
    removals: list = []
    additions: dict = {}

    if args.plan:
        plan = json.loads(Path(args.plan).read_text())
        renames = plan.get("renames", {})
        removals = plan.get("removals", [])
        additions = plan.get("additions", {})

    if args.rename:
        for pair in args.rename:
            old, new = pair.split("=", 1)
            renames[old.strip()] = new.strip()

    if args.remove:
        removals.extend(args.remove)

    if args.add:
        for pair in args.add:
            key, value = pair.split("=", 1)
            additions[key.strip()] = value.strip()

    result = migrate_env(env, renames=renames, removals=removals, additions=additions)

    if args.dry_run:
        print(f"Migration summary: {result.summary()}")
        if result.renamed:
            for old, new in result.renamed:
                print(f"  rename: {old} -> {new}")
        if result.removed:
            for k in result.removed:
                print(f"  remove: {k}")
        if result.added:
            for k in result.added:
                print(f"  add:    {k}")
        return 0

    print(to_shell(result.migrated))
    return 0


def register_migrate_parser(subparsers) -> None:
    p = subparsers.add_parser("migrate", help="Apply migration operations to a .env file")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("--plan", help="JSON file describing renames/removals/additions")
    p.add_argument("--rename", nargs="+", metavar="OLD=NEW", help="Rename keys")
    p.add_argument("--remove", nargs="+", metavar="KEY", help="Remove keys")
    p.add_argument("--add", nargs="+", metavar="KEY=VALUE", help="Add new keys")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without output")
    p.set_defaults(func=cmd_migrate)
