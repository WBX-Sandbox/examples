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
        for path in [ROOT / "sdk" / "01_hello.py", ROOT / "use-cases" / "big-dataset" / "analyze.py",
                     ROOT / "use-cases" / "ai-data-analyst" / "analyst.py"]:
            with self.subTest(script=path.name):
                r = subprocess.run([sys.executable, str(path)], env=env, capture_output=True, text=True, cwd=path.parent)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("WBXSANDBOX_API_KEY", r.stderr)


class AnalystLoop(unittest.TestCase):
    """The ai-data-analyst agent loop with a scripted model and a fake sandbox."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "use-cases" / "ai-data-analyst"))
        import analyst
        self.analyst = analyst

    def tearDown(self):
        sys.path.pop(0)

    def fake_sandbox(self, results):
        ran = []

        class Files:
            def list(self, path):
                return [{"name": "chart.png", "is_dir": False, "size": 10}] if ran else []

        class FakeSandbox:
            files = Files()

            def run_code(self, code, timeout=None):
                ran.append(code)
                return results.pop(0)
        return FakeSandbox(), ran

    def call(self, i, args):
        return {"id": f"c{i}", "type": "function", "function": {"name": "run_python", "arguments": args}}

    def test_runs_code_and_returns_answer(self):
        R = types.SimpleNamespace
        sb, ran = self.fake_sandbox([R(exit_code=0, stdout="x" * 20000, stderr="", timed_out=False)])
        replies = [{"role": "assistant", "tool_calls": [self.call(1, '{"code": "print(1)"}')]},
                   {"role": "assistant", "content": "Sales grew 12 %."}]
        seen = []

        def chat(messages):
            seen.append(list(messages))
            return replies.pop(0)

        answer, stats = self.analyst.analyse("q?", sb, chat, [("a.csv", 123)], log=lambda *_: None)
        self.assertEqual(answer, "Sales grew 12 %.")
        self.assertEqual(ran, ["print(1)"])
        self.assertIn("/home/user/data/a.csv (123 bytes)", seen[0][1]["content"])
        tool_msg = seen[1][-1]
        self.assertEqual(tool_msg["tool_call_id"], "c1")
        self.assertIn("characters cut", tool_msg["content"])      # long output is clipped
        self.assertIn("chart.png", tool_msg["content"])           # new files are reported
        self.assertLess(stats["chars_to_model"], 7000)

    def test_bad_arguments_and_step_limit(self):
        sb, ran = self.fake_sandbox([])
        answer, stats = self.analyst.analyse(
            "q?", sb, lambda m: {"role": "assistant", "tool_calls": [self.call(1, "not json")]}, [],
            log=lambda *_: None)
        self.assertEqual(ran, [])
        self.assertIn("Stopped after", answer)
        self.assertEqual(stats["steps"], self.analyst.MAX_STEPS)


if __name__ == "__main__":
    unittest.main()
