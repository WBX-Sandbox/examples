"""Live output while a command runs, standard input, and exit codes."""
from _env import check_env
from wbxsandbox import Sandbox

check_env()

with Sandbox.create(timeout=120, internet=False) as sb:
    result = sb.run("for i in 1 2 3; do echo step $i; sleep 0.5; done", timeout=10,
                    on_stdout=lambda chunk: print("live:", chunk, end=""))
    print("exit code:", result.exit_code)

    echoed = sb.run("tr a-z A-Z", stdin="hello from stdin\n", timeout=5).check()
    print(echoed.stdout.strip())

    failed = sb.run("exit 7", timeout=5)
    print("a failing command returns its exit code:", failed.exit_code, "| ok =", failed.ok)

    slow = sb.run("sleep 5", timeout=1)
    print("killed after the time limit:", slow.timed_out)
