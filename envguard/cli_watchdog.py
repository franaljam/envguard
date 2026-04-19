"""CLI subcommand: watch — monitor a .env file for changes."""
from __future__ import annotations

import argparse
import sys

from envguard.watchdog import WatchEvent, watch_env


def _on_change(event: WatchEvent) -> None:
    print(f"[envguard] Change detected in {event.path}")
    if event.changed_keys:
        print("  Modified keys: " + ", ".join(event.changed_keys))
    else:
        print("  (key list unavailable)")


def cmd_watch(args: argparse.Namespace) -> None:
    print(f"Watching {args.file} for {args.duration}s (poll every {args.interval}s) …")
    try:
        result = watch_env(
            args.file,
            duration=args.duration,
            interval=args.interval,
            on_change=_on_change,
        )
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    print(result.summary())
    sys.exit(1 if result.total_events() > 0 else 0)


def register_watch_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("watch", help="Monitor a .env file for changes")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="How long to watch in seconds (default: 10)",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Poll interval in seconds (default: 1)",
    )
    p.set_defaults(func=cmd_watch)
