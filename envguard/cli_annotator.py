"""CLI sub-command: annotate – attach inline comments to .env keys."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envguard.parser import parse_env_file
from envguard.annotator import annotate_env


def cmd_annotate(args: argparse.Namespace) -> int:
    """Entry point for the *annotate* sub-command."""
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"[error] file not found: {env_path}", file=sys.stderr)
        return 2

    ann_path = Path(args.annotations)
    if not ann_path.exists():
        print(f"[error] annotations file not found: {ann_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # noqa: BLE001
        print(f"[error] could not parse env file: {exc}", file=sys.stderr)
        return 2

    try:
        with ann_path.open() as fh:
            annotations: dict[str, str] = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"[error] invalid JSON in annotations file: {exc}", file=sys.stderr)
        return 2

    result = annotate_env(env, annotations, skip_unannotated=args.skip_unannotated)

    if args.output:
        out_path = Path(args.output)
        lines = [f"{k}={v}" for k, v in result.annotated.items()]
        out_path.write_text("\n".join(lines) + "\n")
        print(f"Annotated env written to {out_path}")
    else:
        for k, v in result.annotated.items():
            print(f"{k}={v}")

    print(result.summary())
    return 0


def register_annotate_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "annotate",
        help="Attach inline comments to .env keys from a JSON annotations file.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "annotations",
        help="Path to a JSON file mapping key -> comment string.",
    )
    p.add_argument(
        "--skip-unannotated",
        action="store_true",
        default=False,
        help="Omit keys that have no annotation from the output.",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write annotated result to FILE instead of stdout.",
    )
    p.set_defaults(func=cmd_annotate)
