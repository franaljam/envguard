"""CLI subcommand: plan — preview env changes without applying them."""
from __future__ import annotations
import argparse
import sys
from envguard.parser import parse_env_file
from envguard.planner import plan_env


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    set_keys: dict[str, str] = {}
    for item in args.set or []:
        if "=" not in item:
            print(f"Invalid --set value (expected KEY=VALUE): {item}", file=sys.stderr)
            return 1
        k, v = item.split("=", 1)
        set_keys[k] = v

    rename_keys: dict[str, str] = {}
    for item in args.rename or []:
        if ":" not in item:
            print(f"Invalid --rename value (expected OLD:NEW): {item}", file=sys.stderr)
            return 1
        old, new = item.split(":", 1)
        rename_keys[old] = new

    result = plan_env(
        env,
        set_keys=set_keys or None,
        delete_keys=args.delete or None,
        rename_keys=rename_keys or None,
    )

    print(result.summary())

    if args.preview:
        print("\nPreview:")
        for k, v in sorted(result.preview.items()):
            print(f"  {k}={v}")

    return 0 if result.changed() else 0


def register_plan_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("plan", help="Preview changes to an env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--set", metavar="KEY=VALUE", action="append", help="Set a key")
    p.add_argument("--delete", metavar="KEY", action="append", help="Delete a key")
    p.add_argument("--rename", metavar="OLD:NEW", action="append", help="Rename a key")
    p.add_argument("--preview", action="store_true", help="Print resulting env")
    p.set_defaults(func=cmd_plan)
