#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "         Agent Token Shield - Installer v1.0.0            "
echo "=========================================================="

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
GEMINI_DIR="${HOME}/.gemini"
HOOKS_CONFIG="${GEMINI_DIR}/config/hooks.json"
SKILLS_DIR="${GEMINI_DIR}/skills"

mkdir -p "${BIN_DIR}"

# 1. Symlink CLI to ~/.local/bin
echo "[-] Installing 'token-shield' CLI to ${BIN_DIR}..."
ln -sf "${INSTALL_DIR}/bin/token-shield" "${BIN_DIR}/token-shield"
chmod +x "${INSTALL_DIR}/bin/token-shield" "${INSTALL_DIR}/cli.py" "${INSTALL_DIR}/core/"*.py

# 2. Install Skill
if [ -d "${GEMINI_DIR}" ]; then
    echo "[-] Installing token-shield skill to ${SKILLS_DIR}..."
    mkdir -p "${SKILLS_DIR}"
    ln -sf "${INSTALL_DIR}/skills/token-shield" "${SKILLS_DIR}/token-shield"
fi

# 3. Register Hooks in hooks.json if Gemini / Antigravity is detected
if [ -f "${HOOKS_CONFIG}" ]; then
    echo "[-] Registering lifecycle hooks into ${HOOKS_CONFIG}..."
    python3 - << EOF
import json
from pathlib import Path

hooks_file = Path("${HOOKS_CONFIG}")
install_dir = "${INSTALL_DIR}"

try:
    data = json.loads(hooks_file.read_text(encoding="utf-8")) if hooks_file.exists() else {}
except Exception:
    data = {}

# Merge token-shield hooks
hook_cmd = f"python3 {install_dir}/adapters/antigravity/antigravity_hook.py"

data["token-shield"] = {
    "SessionStart": [
        {"type": "command", "command": f"{hook_cmd} session-start", "timeout": 15}
    ],
    "PreInvocation": [
        {"type": "command", "command": f"{hook_cmd} pre-invocation", "timeout": 5}
    ],
    "PreToolUse": [
        {
            "matcher": "write_file|edit_file|run_command",
            "hooks": [
                {"type": "command", "command": f"{hook_cmd} pre-tool", "timeout": 5}
            ]
        }
    ]
}

hooks_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("     Hooks registered successfully.")
EOF
fi

echo ""
echo " Installation completed successfully!"
echo "  Run 'token-shield stats' to inspect your token usage."
echo "  Run 'token-shield probe <file>' to test 0-token local syntax validation."
echo "=========================================================="
