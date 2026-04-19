"""CLI sub-command: promote keys between .env files."""
from __future__ import annotations
import argparse
from envguard.parser import parse_env_file
from envguard.promoter import promote_env
from envguard.reporter import _colored


def cmd_promote(args: argparse.Namespace) -> int:
    try:
        source = parse_env_file(args.source)
        target = parse_env_file(args.target)
    except Exception as exc:
        print(_colored(f"Error: {exc}", "red"))
        return 1

    keys = args.keys.split(",") if args.keys else None

    result = promote_env(
        source,
        target,
        source_env=args.source,
        target_env=args.target,
        keys=keys,
        overwrite=args.overwrite,
    )

    print(result.summary())

    if args.verbose:
        for k, v in result.promoted.items():
            print(_colored(f"  + {k}={v}", "green"))
        for k, v in result.overwritten.items():
            print(_colored(f"  ~ {k}={v}", "yellow"))
        for k in result.skipped:
            print(f"  = {k} (skipped)")

    if args.output:
        lines = [f"{k}={v}" for k, v in result.merged.items()]
        with open(args.output, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"Written to {args.output}")

    return 0 if result.changed() else 0


def register_promote_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("promote", help="Promote env vars from source to target")
    p.add_argument("source", help="Source .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument("--keys", default=None, help="Comma-separated keys to promote")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys")
    p.add_argument("--output", default=None, help="Write merged result to file")
    p.add_argument("--verbose", action="store_true", help="Show per-key changes")
    p.set_defaults(func=cmd_promote)
