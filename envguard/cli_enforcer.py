"""CLI sub-command: enforce – run rule-based enforcement against a .env file.

Usage examples::

    envguard enforce .env --rules rules.json
    envguard enforce .env --rules rules.yaml --warn-only
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envguard.parser import parse_env_file
from envguard.schema_loader import load_schema  # reuse JSON/YAML loader helper
from envguard.enforcer import enforce_env


def cmd_enforce(args: Namespace) -> int:
    """Execute the *enforce* command; return an exit code."""
    # --- load env -----------------------------------------------------------
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Cannot read env file: {exc}", file=sys.stderr)
        return 2

    # --- load rules ---------------------------------------------------------
    try:
        # load_schema returns a list of FieldSchema objects; for rules we
        # accept raw dicts from a plain JSON/YAML list file.
        import json, pathlib

        rules_path = pathlib.Path(args.rules)
        if not rules_path.exists():
            print(f"[error] Rules file not found: {args.rules}", file=sys.stderr)
            return 2

        suffix = rules_path.suffix.lower()
        if suffix == ".json":
            rules = json.loads(rules_path.read_text())
        elif suffix in (".yaml", ".yml"):
            try:
                import yaml
                rules = yaml.safe_load(rules_path.read_text())
            except ImportError:
                print("[error] PyYAML is required for YAML rules files.", file=sys.stderr)
                return 2
        else:
            print(f"[error] Unsupported rules format: {suffix}", file=sys.stderr)
            return 2
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Cannot load rules: {exc}", file=sys.stderr)
        return 2

    # --- enforce ------------------------------------------------------------
    result = enforce_env(env, rules)

    for v in result.errors():
        print(f"  [error]   {v.key}: {v.message}")
    for v in result.warnings():
        print(f"  [warning] {v.key}: {v.message}")

    print(result.summary())

    if args.warn_only:
        return 0
    return 1 if result.has_errors else 0


def register_enforce_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "enforce",
        help="Enforce rule-based constraints against a .env file.",
    )
    p.add_argument("env_file", metavar="ENV_FILE", help="Path to the .env file.")
    p.add_argument(
        "--rules",
        required=True,
        metavar="RULES_FILE",
        help="JSON or YAML file containing enforcement rules.",
    )
    p.add_argument(
        "--warn-only",
        action="store_true",
        default=False,
        help="Exit 0 even when errors are found (treat all as warnings).",
    )
    p.set_defaults(func=cmd_enforce)
