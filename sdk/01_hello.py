"""Create a sandbox, run a shell command and a piece of code, and clean up automatically."""
from _env import check_env
from wbxsandbox import Sandbox

check_env()

with Sandbox.create(template="base", timeout=120) as sb:
    print("sandbox:", sb.id)
    print(sb.run("uname -sr").check().stdout.strip())
    print(sb.run_code("import platform; print(platform.python_version())").check().stdout.strip())
    print(sb.run_code("console.log(6 * 7)", language="node").stdout.strip() or "(node is not in the base template)")

print("sandbox destroyed")
