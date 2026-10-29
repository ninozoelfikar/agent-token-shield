#!/usr/bin/env python3
"""
Context Lazy Loader & Lean Index Generator
Compacts multi-module project context into a high-density, <250 token radar index,
preventing monolithic context dump at session start.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any


class LazyLoader:
    def __init__(self, root_dir: Path | str):
        self.root_dir = Path(root_dir).resolve()

    def discover_modules(self) -> List[Dict[str, Any]]:
        modules = []
        # Check subdirectories
        for entry in self.root_dir.iterdir():
            if entry.name.startswith(".") or entry.name in ("node_modules", "dist", "build", "venv", ".venv", "__pycache__"):
                continue
            if entry.is_dir():
                # Check for indicators (package.json, pyproject.toml, README.md, etc.)
                summary = self._summarize_dir(entry)
                modules.append({
                    "name": entry.name,
                    "path": str(entry.relative_to(self.root_dir)),
                    "type": summary.get("type", "directory"),
                    "brief": summary.get("brief", "Module directory")
                })
        return modules

    def _summarize_dir(self, dir_path: Path) -> Dict[str, str]:
        pkg_json = dir_path / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                return {
                    "type": "nodejs",
                    "brief": data.get("description") or f"Node package {data.get('name', dir_path.name)}"
                }
            except Exception:
                pass

        pyproject = dir_path / "pyproject.toml"
        if pyproject.exists():
            return {"type": "python", "brief": "Python project/package"}

        readme = dir_path / "README.md"
        if readme.exists():
            try:
                lines = [l.strip() for l in readme.read_text(encoding="utf-8").splitlines() if l.strip()]
                first_desc = lines[1] if len(lines) > 1 and not lines[1].startswith("#") else (lines[0] if lines else "")
                return {"type": "docs", "brief": first_desc[:60]}
            except Exception:
                pass

        return {"type": "dir", "brief": f"{len(list(dir_path.iterdir()))} items"}

    def generate_compact_manifest(self) -> str:
        modules = self.discover_modules()
        if not modules:
            return f"[TOKEN-SHIELD] Workspace: {self.root_dir.name} (Single-module repository)"

        lines = [f"[TOKEN-SHIELD RADAR • {self.root_dir.name}]"]
        for m in modules[:15]:
            lines.append(f"• {m['name']} ({m['type']}): {m['brief']}")
        
        lines.append("─────────────────────────────────────────────────────────────────")
        lines.append("⚡ RULE: Lazy-load mode active. Do not read full files until explicitly required.")
        return "\n".join(lines)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    loader = LazyLoader(target)
    manifest = loader.generate_compact_manifest()
    print(manifest)


if __name__ == "__main__":
    main()
