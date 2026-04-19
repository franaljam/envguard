"""CLI command for comparing two .env files side by side."""
import argparse
import sys
from envguard.parser import parse_env_file
from envguard.comparator import compare_envs


def cmd_compare(args: argparse.Namespace) -> int:
    try:
        left = parse_env_file(args.left)
        right = parse_env_file(args.right)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(left, right, ignore_values=args.ignore_values)

    if result.is_equal():
        print("Environments are identical.")
        return 0

    if result.changed():
        print("Changed:")
        for c in result.changed():
            print(f"  {c.key}: {c.left!r} -> {c.right!r}")

    if result.left_only():
        print(f"Only in {args.left}:")
        for c in result.left_only():
            print(f"  {c.key}={c.left}")

    if result.right_only():
        print(f"Only in {args.right}:")
        for c in result.right_only():
            print(f"  {c.key}={c.right}")

    print(result.summary())
    return 1


def register_compare_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "compare",
        help="Compare two .env files side by side.",
    )
    p.add_argument("left", help="First .env file.")
    p.add_argument("right", help="Second .env file.")
    p.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only compare keys, ignore value differences.",
    )
    p.set_defaults(func=cmd_compare)
