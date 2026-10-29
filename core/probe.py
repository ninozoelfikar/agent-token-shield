#!/usr/bin/env python3
"""
Zero-Token Deterministic Syntax Probe
Validates code syntax locally in milliseconds without consuming LLM tokens.
Supported languages: Python, Node.js/JavaScript, JSON, Bash shell scripts.
"""

import sys
import os
import ast
import json
import subprocess
from pathlib import Path


def probe_python(file_path: Path) -> tuple[bool, str]:
    try:
        content = file_path.read_text(encoding="utf-8")
        ast.parse(content, filename=str(file_path))
        return True, "Python syntax OK"
    except SyntaxError as e:
        return False, f"Python SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}"
    except Exception as e:
        return False, f"Python check error: {str(e)}"


def probe_node(file_path: Path) -> tuple[bool, str]:
    try:
        res = subprocess.run(
            ["node", "--check", str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0:
            return True, "Node.js syntax OK"
        return False, f"Node.js SyntaxError: {res.stderr.strip()}"
    except FileNotFoundError:
        return True, "Node.js not installed, skipped probe"
    except subprocess.TimeoutExpired:
        return False, "Node.js check timed out (>5s)"
    except Exception as e:
        return False, f"Node check error: {str(e)}"


def probe_json(file_path: Path) -> tuple[bool, str]:
    try:
        content = file_path.read_text(encoding="utf-8")
        json.loads(content)
        return True, "JSON syntax OK"
    except json.JSONDecodeError as e:
        return False, f"JSON SyntaxError: {e.msg} at line {e.lineno}, column {e.colno}"
    except Exception as e:
        return False, f"JSON read error: {str(e)}"


def probe_bash(file_path: Path) -> tuple[bool, str]:
    try:
        res = subprocess.run(
            ["bash", "-n", str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0:
            return True, "Bash syntax OK"
        return False, f"Bash SyntaxError: {res.stderr.strip()}"
    except FileNotFoundError:
        return True, "Bash not installed, skipped probe"
    except Exception as e:
        return False, f"Bash check error: {str(e)}"


def probe_file(file_path: str | Path) -> tuple[bool, str]:
    path = Path(file_path)
    if not path.exists():
        return False, f"File not found: {file_path}"
    if not path.is_file():
        return False, f"Path is not a regular file: {file_path}"

    ext = path.suffix.lower()
    if ext == ".py":
        return probe_python(path)
    elif ext in (".js", ".mjs", ".cjs", ".ts"):
        return probe_node(path)
    elif ext in (".json", ".jsonl"):
        return probe_json(path)
    elif ext in (".sh", ".bash"):
        return probe_bash(path)
    else:
        return True, f"Unsupported extension {ext}, skipped probe (neutral)"


def main():
    if len(sys.argv) < 2:
        print("Usage: probe.py <path-to-file>", file=sys.stderr)
        sys.exit(2)

    target = sys.argv[1]
    ok, msg = probe_file(target)
    if ok:
        print(f"✓ [PASS 0-Token] {target}: {msg}")
        sys.exit(0)
    else:
        print(f"✗ [FAIL 0-Token] {target}: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
