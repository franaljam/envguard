"""CLI helpers for the transform sub-command."""
from __future__ import annotations
import sys
from typing import List

from envguard.parser import parse_env_file, EnvParseError
from envguard.transformer import transform_env, rename_keys, TransformError
from envguard.reporter import _colored


def cmd_transform(args) -> int:  # type: ignore[type-arg]
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(_colored(f"Parse error: {exc}", "red"), file=sys.stderr)
        return 1

    try:
        result = transform_env(
            env,
            strip=args.strip,
            uppercase_values=args.uppercase,
            mask=args.mask,
        )
    except TransformError as exc:
        print(_colored(f"Transform error: {exc}", "red"), file=sys.stderr)
        return 1

    out = result.transformed

    if args.prefix:
        out = rename_keys(out, args.prefix)

    changed = result.changed_keys()
    if changed:
        print(_colored(f"Modified {len(changed)} value(s).", "yellow"))

    for k, v in out.items():
        print(f"{k}={v}")

    return 0


def register_transform_parser(subparsers) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("transform", help="Transform .env variable values")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--strip", action="store_true", help="Strip whitespace from values")
    p.add_argument("--uppercase", action="store_true", help="Uppercase all values")
    p.add_argument("--mask", action="store_true", help="Mask non-empty values with ***")
    p.add_argument("--prefix", default="", help="Prefix to prepend to all keys")
    p.set_defaults(func=cmd_transform)
