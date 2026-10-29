"""
Generic Middleware for AI Agent Frameworks (LangGraph, CrewAI, AutoGen, Custom)
Wraps agent tool execution with Token Shield loop prevention and local syntax probe.
"""

from typing import Callable, Any, Optional
from pathlib import Path
import sys

# Import core
SHIELD_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SHIELD_ROOT / "core"))

from loop_guard import LoopGuard
from probe import probe_file


class TokenShieldMiddleware:
    def __init__(self, repeat_limit: int = 3, window_size: int = 12):
        self.guard = LoopGuard(repeat_limit=repeat_limit, window_size=window_size)

    def intercept_tool(self, session_id: str, tool_name: str, tool_args: Any, execute_fn: Callable, *args, **kwargs):
        """
        Intercepts tool call before execution.
        Raises RuntimeError if loop is detected.
        """
        allowed, reason = self.guard.evaluate_call(session_id, tool_name, tool_args)
        if not allowed:
            raise RuntimeError(reason)

        # Execute tool
        result = execute_fn(*args, **kwargs)

        # If tool wrote a file, auto-probe syntax
        if tool_name in ("write_file", "edit_file", "create_file") and isinstance(tool_args, dict):
            file_path = tool_args.get("Path") or tool_args.get("path") or tool_args.get("file")
            if file_path:
                ok, probe_msg = probe_file(file_path)
                if not ok:
                    # Append warning to result so agent fixes it immediately without another query
                    if isinstance(result, str):
                        result += f"\n[TOKEN-SHIELD PROBE ERROR]: {probe_msg}"
                    elif isinstance(result, dict):
                        result["probe_error"] = probe_msg

        return result
