"""CLI sub-command: scope — filter env file to a named scope."""
from __future__ import annotations
import argparse
import sys
from envguard.parser import parse_env_file, EnvParseError
from envguard.scoper import scope_env


def cmd_scope(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    extra = args.extra.split(",") if args.extra else []
    result = scope_env(env, args.scope, strip_prefix=not args.keep_prefix, extra_keys=extra)

    if args.verbose:
        print(result.summary())
        print()

    for k, v in result.env.items():
        if args.redact and any(s in k.upper() for s in ("SECRET", "PASSWORD", "TOKEN", "KEY")):
            print(f"{k}=***")
        else:
            print(f"{k}={v}")

    return 0


def register_scope_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("scope", help="Filter env file to a named scope prefix")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("scope", help="Scope name (prefix before underscore, e.g. PROD)")
    p.add_argument("--keep-prefix", action="store_true", help="Do not strip scope prefix from keys")
    p.add_argument("--extra", default="", help="Comma-separated extra keys to always include")
    p.add_argument("--redact", action="store_true", help="Redact sensitive values")
    p.add_argument("--verbose", "-v", action="store_true", help="Print summary header")
    p.set_defaults(func=cmd_scope)
