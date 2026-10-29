#!/usr/bin/env python3
"""
Token Shield CLI - Main Entrypoint
"""

import sys
import argparse
from pathlib import Path

# Add core to path
SHIELD_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SHIELD_ROOT / "core"))

from probe import probe_file
from loop_guard import LoopGuard
from lazy_loader import LazyLoader
from telemetry import TelemetryAuditor


def cmd_probe(args):
    ok, msg = probe_file(args.file)
    if ok:
        print(f"✓ [PASS 0-Token] {args.file}: {msg}")
        sys.exit(0)
    else:
        print(f"✗ [FAIL 0-Token] {args.file}: {msg}", file=sys.stderr)
        sys.exit(1)


def cmd_loop_check(args):
    guard = LoopGuard(repeat_limit=args.limit)
    allowed, reason = guard.evaluate_call(args.session, args.tool, args.args)
    if allowed:
        print("ALLOW")
        sys.exit(0)
    else:
        print(f"DENY: {reason}", file=sys.stderr)
        sys.exit(1)


def cmd_radar(args):
    loader = LazyLoader(args.dir)
    print(loader.generate_compact_manifest())


def cmd_stats(args):
    auditor = TelemetryAuditor()
    auditor.print_report(args.days)


def main():
    parser = argparse.ArgumentParser(
        prog="token-shield",
        description="Agent Token Shield: Cut AI Coding Agent Token Waste by 38-58%"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # probe
    p_probe = subparsers.add_parser("probe", help="Run 0-token deterministic syntax check on a file")
    p_probe.add_argument("file", help="Path to file (py, js, ts, json, sh)")
    p_probe.set_defaults(func=cmd_probe)

    # loop-check
    p_loop = subparsers.add_parser("loop-check", help="Evaluate tool call against infinite loops")
    p_loop.add_argument("--session", default="default", help="Session ID")
    p_loop.add_argument("--tool", required=True, help="Tool name")
    p_loop.add_argument("--args", default="{}", help="Tool arguments (string or JSON)")
    p_loop.add_argument("--limit", type=int, default=3, help="Max identical repeats allowed")
    p_loop.set_defaults(func=cmd_loop_check)

    # radar
    p_radar = subparsers.add_parser("radar", help="Generate compact <250 token workspace radar")
    p_radar.add_argument("--dir", default=".", help="Target workspace directory")
    p_radar.set_defaults(func=cmd_radar)

    # stats
    p_stats = subparsers.add_parser("stats", help="Display token telemetry & savings report")
    p_stats.add_argument("--days", type=int, default=7, help="Number of days to audit")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
