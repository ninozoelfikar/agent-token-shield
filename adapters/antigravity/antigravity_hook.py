#!/usr/bin/env python3
"""
Antigravity / Gemini CLI Lifecycle Hook Adapter for Agent Token Shield.
Connects Antigravity's SessionStart, PreInvocation, and PreToolUse hooks
to Token Shield's LoopGuard and LazyLoader.
"""

import sys
import json
from pathlib import Path

# Add project root to path
SHIELD_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SHIELD_ROOT / "core"))

from loop_guard import LoopGuard
from lazy_loader import LazyLoader

GATED_TOOLS = {"write_file", "edit_file", "run_command"}


def out(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.flush()


def read_stdin() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def session_start():
    data = read_stdin()
    cwd = Path.cwd()
    loader = LazyLoader(cwd)
    radar = loader.generate_compact_manifest()
    
    ctx = (
        f"{radar}\n\n"
        "⚡ [TOKEN SHIELD ACTIVE]\n"
        "1. Work in modular fashion: use existing tools and templates.\n"
        "2. Deterministic validation: test syntax locally before reporting.\n"
        "3. Loop breaker: identical repetitive calls will be rejected."
    )
    out({"injectSteps": [{"systemMessage": {"systemMessage": ctx}}]})


def pre_invocation():
    # Keep pre-invocation minimal (~50 tokens) to preserve cache hit
    reminder = "⚡ Token Shield: proceed concisely, avoid repeating failed steps, use modular tools."
    out({"injectSteps": [{"systemMessage": {"systemMessage": reminder}}]})


def pre_tool():
    data = read_stdin()
    conv_id = data.get("conversationId", "default")
    tool = data.get("toolCall") or {}
    name = tool.get("name", "")

    if name not in GATED_TOOLS:
        out({"decision": "ask"})
        return

    args = tool.get("args") or {}
    guard = LoopGuard()
    allowed, reason = guard.evaluate_call(conv_id, name, args)

    if not allowed:
        out({"decision": "deny", "reason": reason})
        return

    out({"decision": "ask"})


def main():
    if len(sys.argv) < 2:
        out({"decision": "ask"})
        return

    mode = sys.argv[1]
    if mode == "session-start":
        session_start()
    elif mode == "pre-invocation":
        pre_invocation()
    elif mode == "pre-tool":
        pre_tool()
    else:
        out({"decision": "ask"})


if __name__ == "__main__":
    main()
