"""CLI sub-command: tag — display tags for keys in a .env file."""
import argparse
from envguard.parser import parse_env_file
from envguard.tagger import tag_env


def cmd_tag(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error reading file: {exc}")
        return 1

    result = tag_env(env)

    if args.filter_tag:
        keys = result.keys_with_tag(args.filter_tag)
        if not keys:
            print(f"No keys tagged '{args.filter_tag}'.")
            return 0
        for k in sorted(keys):
            print(f"{k}: {', '.join(sorted(result.tags[k]))}")
        return 0

    print(result.summary())
    return 0


def register_tag_parser(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Tag .env keys with metadata labels")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--filter-tag",
        dest="filter_tag",
        default=None,
        metavar="TAG",
        help="Only show keys with this tag (e.g. secret, config, feature-flag)",
    )
    p.set_defaults(func=cmd_tag)
