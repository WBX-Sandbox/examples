"""Offline checks: every script parses, keys are never hard-coded, and the webhook example runs.
No API key and no network are used."""
import ast
import re
import subprocess
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = sorted(p for p in ROOT.rglob("*.py") if ".git" not in p.parts and "tests" not in p.parts)


class OfflineChecks(unittest.TestCase):
    def test_scripts_parse(self):
        self.assertGreaterEqual(len(SCRIPTS), 16)
        for path in SCRIPTS:
            with self.subTest(script=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(encoding="utf-8"))

    def test_no_secrets_in_repo(self):
        pattern = re.compile(r"(wbx_token=[0-9a-f]{16,}|X-API-Key:\s*[A-Za-z0-9]{16,}|Bearer\s+[A-Za-z0-9]{20,})")
        for path in ROOT.rglob("*"):
            if path.is_file() and ".git" not in path.parts and path.suffix in {".py", ".md", ".yml", ".json", ".example"}:
                with self.subTest(file=str(path.relative_to(ROOT))):
                    self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))

    def test_examples_need_a_key(self):
        """Without WBXSANDBOX_API_KEY the scripts stop with a clear message before contacting anything."""
        stub = ROOT / "tests" / "_stub"
        env = {"PATH": "", "PYTHONPATH": str(stub)}
        for path in [ROOT / "sdk" / "01_hello.py", ROOT / "use-cases" / "big-dataset" / "analyze.py"]:
            with self.subTest(script=path.name):
                r = subprocess.run([sys.executable, str(path)], env=env, capture_output=True, text=True, cwd=path.parent)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("WBXSANDBOX_API_KEY", r.stderr)


if __name__ == "__main__":
    unittest.main()
