#!/usr/bin/env python3
"""
Unit Tests for Agent Token Shield
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

SHIELD_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SHIELD_ROOT / "core"))

from probe import probe_file
from loop_guard import LoopGuard
from lazy_loader import LazyLoader


class TestTokenShield(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_probe_valid_python(self):
        py_file = self.root / "valid.py"
        py_file.write_text("x = 10\ndef foo():\n    return x * 2\n")
        ok, msg = probe_file(py_file)
        self.assertTrue(ok)
        self.assertIn("Python syntax OK", msg)

    def test_probe_invalid_python(self):
        py_file = self.root / "invalid.py"
        py_file.write_text("x = 10\ndef foo(\n    return x\n")
        ok, msg = probe_file(py_file)
        self.assertFalse(ok)
        self.assertIn("SyntaxError", msg)

    def test_probe_valid_json(self):
        json_file = self.root / "valid.json"
        json_file.write_text('{"name": "test", "active": true}')
        ok, msg = probe_file(json_file)
        self.assertTrue(ok)
        self.assertIn("JSON syntax OK", msg)

    def test_probe_invalid_json(self):
        json_file = self.root / "invalid.json"
        json_file.write_text('{"name": "test", "active": true,}')
        ok, msg = probe_file(json_file)
        self.assertFalse(ok)
        self.assertIn("JSON SyntaxError", msg)

    def test_loop_guard_detection(self):
        guard_dir = self.root / "cache"
        guard = LoopGuard(state_dir=guard_dir, repeat_limit=3, window_size=5)

        tool = "edit_file"
        args = {"path": "main.py", "target": "foo", "replacement": "bar"}

        # Attempt 1: Allow
        ok1, _ = guard.evaluate_call("sess1", tool, args)
        self.assertTrue(ok1)

        # Attempt 2: Allow
        ok2, _ = guard.evaluate_call("sess1", tool, args)
        self.assertTrue(ok2)

        # Attempt 3: Deny (Hit repeat limit 3)
        ok3, reason = guard.evaluate_call("sess1", tool, args)
        self.assertFalse(ok3)
        self.assertIn("Identical action detected", reason)

    def test_lazy_loader_manifest(self):
        # Create mock module
        mod_a = self.root / "auth-service"
        mod_a.mkdir()
        (mod_a / "package.json").write_text('{"name": "auth-service", "description": "Authentication microservice"}')

        loader = LazyLoader(self.root)
        manifest = loader.generate_compact_manifest()
        self.assertIn("TOKEN-SHIELD RADAR", manifest)
        self.assertIn("auth-service", manifest)
        self.assertIn("Authentication microservice", manifest)


if __name__ == "__main__":
    unittest.main()
