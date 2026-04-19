"""CLI sub-command: resolve aliases in an env file."""
from __future__ import annotations
import argparse
import sys
from envguard.parser import parse_env_file, EnvParseError
from envguard.aliases import resolve_aliases


def cmd_aliases(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    # Build alias map from repeated --alias ALIAS=CANONICAL arguments
    alias_map: dict[str, str] = {}
    for entry in args.alias or []:
        if "=" not in entry:
            print(f"Invalid alias format (expected ALIAS=CANONICAL): {entry}", file=sys.stderr)
            return 1
        alias, _, canonical = entry.partition("=")
        alias_map[alias.strip()] = canonical.strip()

    result = resolve_aliases(env, alias_map, keep_alias=args.keep)

    print(result.summary())

    if args.verbose:
        print("\nResolved env:")
        for k, v in result.env.items():
            print(f"  {k}={v}")

    return 1 if result.has_unresolved() else 0


def register_aliases_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("aliases", help="Resolve alias keys to canonical names")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--alias",
        action="append",
        metavar="ALIAS=CANONICAL",
        help="Alias mapping (repeatable)",
    )
    p.add_argument(
        "--keep",
        action="store_true",
        help="Keep alias key alongside canonical key",
    )
    p.add_argument("--verbose", action="store_true", help="Print resolved env")
    p.set_defaults(func=cmd_aliases)
