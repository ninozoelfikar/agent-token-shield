#!/usr/bin/env bash
set -e

echo "[-] Uninstalling Agent Token Shield..."
BIN_DIR="${HOME}/.local/bin"
GEMINI_DIR="${HOME}/.gemini"
HOOKS_CONFIG="${GEMINI_DIR}/config/hooks.json"
SKILLS_DIR="${GEMINI_DIR}/skills"

rm -f "${BIN_DIR}/token-shield"
rm -rf "${SKILLS_DIR}/token-shield"

if [ -f "${HOOKS_CONFIG}" ]; then
    python3 - << EOF
import json
from pathlib import Path

hooks_file = Path("${HOOKS_CONFIG}")
try:
    data = json.loads(hooks_file.read_text(encoding="utf-8"))
    if "token-shield" in data:
        del data["token-shield"]
        hooks_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("    ✓ Cleaned hooks from hooks.json")
except Exception:
    pass
EOF
fi

echo "✓ Agent Token Shield uninstalled cleanly."
