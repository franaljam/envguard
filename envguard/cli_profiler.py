"""CLI subcommand: profile — show statistics for a .env file."""
import argparse
from envguard.parser import parse_env_file
from envguard.profiler import profile_env


def cmd_profile(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error reading {args.file}: {exc}")
        return 1

    result = profile_env(env)
    print(f"File: {args.file}")
    print(result.summary())

    if args.show_sensitive and result.sensitive_keys:
        print("Sensitive keys:")
        for k in result.sensitive_keys:
            print(f"  {k}")

    return 0


def register_profile_parser(subparsers) -> None:
    p = subparsers.add_parser("profile", help="Show statistics for a .env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--show-sensitive",
        action="store_true",
        default=False,
        help="List detected sensitive key names",
    )
    p.set_defaults(func=cmd_profile)
