"""Clone a repository you don't fully trust and run its tests in a disposable microVM.

The sandbox can reach only GitHub and PyPI, has its own kernel and disk, and is destroyed afterwards.
Usage: python run_tests.py [git-url] [test-command]
"""
import os
import sys

from wbxsandbox import Sandbox

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

repo = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/pallets/itsdangerous"
tests = sys.argv[2] if len(sys.argv) > 2 else "python3 -m pytest -q"

ALLOW = ["github.com", "codeload.github.com", "objects.githubusercontent.com",
         "pypi.org", "files.pythonhosted.org"]

with Sandbox.create(template="base", timeout=900, allow=ALLOW) as sb:
    print("sandbox:", sb.id, "| network limited to", ", ".join(ALLOW))

    step = sb.run(f"git clone --depth 1 {repo} /home/user/repo", timeout=120)
    print(step.stdout or step.stderr)
    step.check()

    print("installing the project and its test dependencies ...")
    sb.run("cd /home/user/repo && export PIP_ROOT_USER_ACTION=ignore"
           " && pip install -q -U pip && pip install -q -e . pytest"
           " && (pip install -q --group tests 2>/dev/null"          # PEP 735 dependency group
           " || pip install -q -r requirements/tests.txt 2>/dev/null || true)", timeout=600).check()

    print(f"running: {tests}\n")
    result = sb.run(f"cd /home/user/repo && {tests}", timeout=600,
                    on_stdout=lambda chunk: print(chunk, end=""),
                    on_stderr=lambda chunk: print(chunk, end=""))
    print("\nexit code:", result.exit_code)

print("sandbox destroyed – nothing from the repository ran on this machine")
