"""Pause a sandbox (memory and files are kept, you don't pay while paused), resume it, extend its lifetime."""
from _env import check_env
from wbxsandbox import Sandbox

check_env()

with Sandbox.create(timeout=180, internet=False) as sb:
    sb.files.write("/home/user/state.txt", "kept across pause/resume")
    sb.run("nohup sh -c 'i=0; while true; do i=$((i+1)); echo $i > /tmp/counter; sleep 1; done' >/dev/null 2>&1 &", timeout=5)

    sb.pause()
    print("state:", sb.state)
    sb.resume()
    print("state:", sb.state)

    sb.set_timeout(300)
    print("file:", sb.files.read_text("/home/user/state.txt"))
    print("background process still counting:", sb.run("cat /tmp/counter", timeout=5).stdout.strip())
