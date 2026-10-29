#!/usr/bin/env python3
"""
Universal Loop Guard & Death-Spiral Breaker
Detects and terminates repetitive tool execution loops in AI coding agents.
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Optional


class LoopGuard:
    def __init__(
        self,
        state_dir: Optional[Path] = None,
        repeat_limit: int = 3,
        window_size: int = 12
    ):
        self.state_dir = state_dir or (Path.home() / ".cache" / "agent_token_shield")
        self.repeat_limit = repeat_limit
        self.window_size = window_size
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _get_history_file(self, session_id: str) -> Path:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_")) or "global"
        return self.state_dir / f"{safe_id}.calls.json"

    def compute_signature(self, tool_name: str, tool_args: dict | str) -> str:
        payload = {
            "name": tool_name,
            "args": tool_args
        }
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(serialized.encode("utf-8")).hexdigest()

    def evaluate_call(self, session_id: str, tool_name: str, tool_args: dict | str) -> tuple[bool, Optional[str]]:
        """
        Returns (is_allowed, deny_reason).
        If is_allowed is False, the call should be rejected immediately to break the loop.
        """
        sig = self.compute_signature(tool_name, tool_args)
        hist_file = self._get_history_file(session_id)

        try:
            history = json.loads(hist_file.read_text(encoding="utf-8")) if hist_file.exists() else []
        except Exception:
            history = []

        recent = history[-self.window_size:]
        same_count = recent.count(sig)

        # Update history
        history.append(sig)
        hist_file.write_text(json.dumps(history[-self.window_size:]), encoding="utf-8")

        if same_count >= (self.repeat_limit - 1):
            reason = (
                f"[TOKEN-SHIELD] Identical action detected {same_count + 1} times in recent window. "
                "Execution halted to break infinite loop and conserve tokens. "
                "Analyze why the previous attempts failed, alter approach, or report the obstacle to the user."
            )
            return False, reason

        return True, None

    def reset_session(self, session_id: str):
        hist_file = self._get_history_file(session_id)
        if hist_file.exists():
            hist_file.unlink(missing_ok=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate tool call for loops")
    parser.add_argument("--session", default="default", help="Session or conversation ID")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--args", default="{}", help="Tool arguments (JSON string)")
    parser.add_argument("--limit", type=int, default=3, help="Repeat limit")
    args = parser.parse_args()

    guard = LoopGuard(repeat_limit=args.limit)
    try:
        parsed_args = json.loads(args.args)
    except Exception:
        parsed_args = args.args

    allowed, reason = guard.evaluate_call(args.session, args.tool, parsed_args)
    if allowed:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)
    else:
        print(json.dumps({"decision": "deny", "reason": reason}))
        sys.exit(1)


if __name__ == "__main__":
    main()
