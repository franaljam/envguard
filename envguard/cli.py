"""CLI entry point for envguard."""
import sys
import argparse
from pathlib import Path

from envguard.parser import parse_env_file, EnvParseError
from envguard.differ import diff_envs
from envguard.validator import validate_env
from envguard.reporter import format_diff_report, format_validation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Validate and diff .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    diff_cmd = sub.add_parser("diff", help="Diff two .env files")
    diff_cmd.add_argument("base", help="Base .env file")
    diff_cmd.add_argument("target", help="Target .env file")
    diff_cmd.add_argument(
        "--ignore-values", action="store_true", help="Only compare keys, not values"
    )
    diff_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")

    validate_cmd = sub.add_parser("validate", help="Validate a .env file against a schema")
    validate_cmd.add_argument("env", help=".env file to validate")
    validate_cmd.add_argument("schema", help="Schema .env file (defines required keys)")
    validate_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")

    return parser


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        base = parse_env_file(Path(args.base))
        target = parse_env_file(Path(args.target))
    except EnvParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(base, target, ignore_values=args.ignore_values)
    print(format_diff_report(result, color=not args.no_color))
    return 0 if not result.has_differences() else 1


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(Path(args.env))
        schema = parse_env_file(Path(args.schema))
    except EnvParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = validate_env(env, schema)
    print(format_validation_report(result, color=not args.no_color))
    return 0 if result.is_valid() else 1


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diff":
        return cmd_diff(args)
    if args.command == "validate":
        return cmd_validate(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
