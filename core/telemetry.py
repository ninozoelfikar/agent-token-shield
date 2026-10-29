#!/usr/bin/env python3
"""
Token Telemetry & Efficiency Auditor
Parses local conversation transcripts to measure token usage, cache-hit ratios,
and verify real-world savings.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any


class TelemetryAuditor:
    def __init__(self, brain_dir: Path | str | None = None):
        self.brain_dir = Path(brain_dir) if brain_dir else (Path.home() / ".gemini" / "antigravity-cli" / "brain")

    def analyze_range(self, days: int = 30) -> Dict[str, Any]:
        if not self.brain_dir.exists():
            return {"error": f"Brain log directory not found at {self.brain_dir}"}

        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).date()
        daily: Dict[str, Dict[str, Any]] = {}

        for entry in self.brain_dir.iterdir():
            if not entry.is_dir():
                continue
            log_file = entry / ".system_generated" / "logs" / "transcript.jsonl"
            if not log_file.is_file():
                continue

            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        created_at = data.get("created_at")
                        if not created_at:
                            continue

                        try:
                            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                            d_obj = dt.date()
                        except Exception:
                            continue

                        if d_obj < cutoff_date:
                            continue

                        date_str = str(d_obj)
                        inp = data.get("input_tokens") or 0
                        cache = data.get("cache_read_tokens") or 0
                        out = data.get("output_tokens") or 0

                        if inp or cache or out:
                            if date_str not in daily:
                                daily[date_str] = {
                                    "fresh_input": 0,
                                    "cache_read": 0,
                                    "output": 0,
                                    "total": 0,
                                    "calls": 0,
                                    "sessions": set()
                                }
                            daily[date_str]["fresh_input"] += inp
                            daily[date_str]["cache_read"] += cache
                            daily[date_str]["output"] += out
                            daily[date_str]["total"] += (inp + cache + out)
                            daily[date_str]["calls"] += 1
                            daily[date_str]["sessions"].add(entry.name)
            except Exception:
                pass

        total_inp = sum(v["fresh_input"] for v in daily.values())
        total_cache = sum(v["cache_read"] for v in daily.values())
        total_out = sum(v["output"] for v in daily.values())
        grand_total = sum(v["total"] for v in daily.values())
        total_calls = sum(v["calls"] for v in daily.values())
        all_sessions = set()
        for v in daily.values():
            all_sessions.update(v["sessions"])

        cache_ratio = (total_cache / grand_total * 100) if grand_total > 0 else 0.0

        return {
            "days_analyzed": days,
            "active_days": len(daily),
            "total_sessions": len(all_sessions),
            "total_calls": total_calls,
            "fresh_input_tokens": total_inp,
            "cache_read_tokens": total_cache,
            "output_tokens": total_out,
            "grand_total_tokens": grand_total,
            "cache_hit_ratio_percent": round(cache_ratio, 2),
            "daily_breakdown": {
                k: {
                    "fresh_input": v["fresh_input"],
                    "cache_read": v["cache_read"],
                    "output": v["output"],
                    "total": v["total"],
                    "calls": v["calls"],
                    "sessions": len(v["sessions"])
                }
                for k, v in sorted(daily.items())
            }
        }

    def print_report(self, days: int = 30):
        stats = self.analyze_range(days)
        if "error" in stats:
            print(f"Error: {stats['error']}", file=sys.stderr)
            return

        print("=" * 65)
        print(f"       TOKEN SHIELD TELEMETRY REPORT (Last {days} Days)")
        print("=" * 65)
        print(f"Active Working Days : {stats['active_days']} days")
        print(f"Total Work Sessions : {stats['total_sessions']} sessions")
        print(f"Total Model Calls   : {stats['total_calls']:,} calls")
        print("-" * 65)
        print(f"Fresh Input Tokens  : {stats['fresh_input_tokens']:,}")
        print(f"Cache Read Tokens   : {stats['cache_read_tokens']:,}")
        print(f"Output Tokens       : {stats['output_tokens']:,}")
        print(f"GRAND TOTAL TOKENS  : {stats['grand_total_tokens']:,}")
        print(f"CACHE HIT RATIO     : {stats['cache_hit_ratio_percent']}%")
        print("=" * 65)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit token consumption")
    parser.add_argument("--days", type=int, default=7, help="Number of days to audit")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    auditor = TelemetryAuditor()
    if args.json:
        res = auditor.analyze_range(args.days)
        # convert sets
        print(json.dumps(res, indent=2))
    else:
        auditor.print_report(args.days)


if __name__ == "__main__":
    main()
