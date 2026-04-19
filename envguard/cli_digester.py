"""CLI commands for digest: compute and check env file digests."""
from __future__ import annotations

import argparse
import sys

from envguard.parser import parse_env_file
from envguard.digester import digest_env, compare_digests, save_digest, load_digest


def cmd_digest(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except Exception as e:
        print(f"Error reading env file: {e}", file=sys.stderr)
        return 1

    result = digest_env(env, algorithm=args.algorithm)
    save_digest(result, args.output)
    print(f"Digest saved to {args.output} ({len(result.digests)} keys, {args.algorithm})")
    return 0


def cmd_digest_check(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except Exception as e:
        print(f"Error reading env file: {e}", file=sys.stderr)
        return 1

    try:
        old = load_digest(args.digest_file)
    except Exception as e:
        print(f"Error reading digest file: {e}", file=sys.stderr)
        return 1

    new = digest_env(env, algorithm=old.algorithm)
    cmp = compare_digests(old, new)

    if cmp.has_drift:
        print(f"Drift detected: {cmp.summary()}")
        if cmp.changed:
            for k, (o, n) in cmp.changed.items():
                print(f"  ~ {k}  (hash changed)")
        if cmp.added:
            for k in cmp.added:
                print(f"  + {k}")
        if cmp.removed:
            for k in cmp.removed:
                print(f"  - {k}")
        return 1

    print("No drift detected.")
    return 0


def register_digest_parser(subparsers) -> None:
    p = subparsers.add_parser("digest", help="Compute a digest of an env file")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("--output", default=".env.digest", help="Output digest file")
    p.add_argument("--algorithm", default="sha256", help="Hash algorithm (default: sha256)")
    p.set_defaults(func=cmd_digest)

    q = subparsers.add_parser("digest-check", help="Check env file against a saved digest")
    q.add_argument("env_file", help="Path to .env file")
    q.add_argument("digest_file", help="Path to saved digest file")
    q.set_defaults(func=cmd_digest_check)
