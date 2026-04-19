"""CLI subcommand: rename keys in a .env file."""
import argparse
import sys
from envguard.parser import parse_env_file, EnvParseError
from envguard.renamer import rename_env


def cmd_rename(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"Error parsing file: {exc}", file=sys.stderr)
        return 1

    if not args.rename:
        print("No renames specified. Use --rename OLD NEW.", file=sys.stderr)
        return 1

    if len(args.rename) % 2 != 0:
        print("--rename requires pairs: OLD NEW [OLD NEW ...]", file=sys.stderr)
        return 1

    pairs = list(zip(args.rename[::2], args.rename[1::2]))
    renames = dict(pairs)

    result = rename_env(env, renames)

    if args.dry_run:
        print("[dry-run] Changes that would be applied:")
        print(result.summary())
        return 0

    if not result.changed():
        print("Nothing to rename.")
        return 0

    output_path = args.output or args.file
    with open(output_path, "w") as fh:
        for key, value in result.renamed.items():
            fh.write(f"{key}={value}\n")

    print(result.summary())
    if result.skipped:
        print(f"Skipped (not found): {', '.join(result.skipped)}")
    return 0


def register_rename_parser(subparsers) -> None:
    p = subparsers.add_parser("rename", help="Rename keys in a .env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--rename",
        nargs="+",
        metavar="KEY",
        help="Pairs of OLD NEW key names to rename",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Write result to this file (default: overwrite input)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    p.set_defaults(func=cmd_rename)
