"""Fan out a batch of background jobs under a hard total price limit.

The platform checks the worst case before anything starts: if the batch could cost more than
the limit, it is refused and nothing is billed.
Usage: python batch.py <max-total-cost>   (in your account's billing currency, e.g. 2.00)
"""
import os
import sys

from wbxsandbox import SandboxError, get_budget, run_batch

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

currency = get_budget().get("currency", "?")
if len(sys.argv) < 2:
    raise SystemExit(f"Usage: python batch.py <max-total-cost in {currency}>")
limit = sys.argv[1]

# Five independent jobs: each simulates one forecast scenario and saves its result file.
JOB = ("mkdir -p output && python3 -c \"import random,statistics; random.seed({seed}); "
       "runs=[sum(random.gauss(1.0,0.2) for _ in range(250)) for _ in range(20000)]; "
       "open('output/result.txt','w').write(f'scenario {seed}: mean={{statistics.mean(runs):.2f}} "
       "p95={{sorted(runs)[int(len(runs)*0.95)]:.2f}}')\"")
jobs = [{"command": JOB.format(seed=s), "timeout_seconds": 120, "internet": False,
         "artifacts": ["output/result.txt"]} for s in range(1, 6)]

print(f"1) Same batch with a deliberately tiny limit (0.0001 {currency}):")
try:
    run_batch(jobs, max_concurrency=5, max_total_cost="0.0001")
    print("   accepted (your plan's rates are lower than expected)")
except SandboxError as e:
    print("   refused before start:", e)

print(f"\n2) With your limit ({limit} {currency}):")
batch = run_batch(jobs, max_concurrency=5, max_total_cost=limit, name="budget-batch-example")
batch.wait(timeout=600)
summary = batch.summary()
print("   status:", summary.get("status"), "| cost:", summary.get("cost"), currency)
for job in batch.jobs():
    print("  ", job.download("output/result.txt").decode())
