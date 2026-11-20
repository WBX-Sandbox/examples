"""Metrics: CPU, memory, network and disk of a sandbox measured from the host – history and a live stream."""
import time

from _env import check_env
from wbxsandbox import Sandbox, features

check_env()

if not features().get("metrics_history"):
    raise SystemExit("Metrics are not enabled for your account.")

with Sandbox.create(timeout=300) as sb:
    # some work to measure: a CPU-bound loop in the background
    sb.run("nohup python3 -c 'while True: sum(i*i for i in range(10**6))' >/dev/null 2>&1 &", timeout=5)
    time.sleep(25)  # samples are taken every 10 seconds

    h = sb.metrics_history()
    for s in h["samples"]:
        print(f"{s['t']}: CPU {s['cpu_pct']:.0f} %, memory {s['mem_mb']} MB")

    # live: first the stored samples (since=0), then a new one every 10 s; stop after three new ones
    seen = 0
    for ev in sb.metrics_stream(since=0):
        if ev["event"] == "sample":
            seen += 1
            print("live:", ev["data"]["cpu_pct"], "% CPU")
            if seen >= len(h["samples"]) + 3:
                break
        elif ev["event"] == "end":
            break
