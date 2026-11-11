"""A background job: submit it, let it run without an open connection, then read logs and result files."""
from _env import check_env, cost_limit
from wbxsandbox import run_job

check_env()

job = run_job(
    command="mkdir -p output && python3 -c \"import math; open('output/primes.txt','w').write('\\n'.join(str(n) for n in range(2, 50000) if all(n % d for d in range(2, math.isqrt(n) + 1))))\" && wc -l output/primes.txt",
    timeout_seconds=120,
    internet=False,
    artifacts=["output/primes.txt"],
    required_artifacts=["output/primes.txt"],
    **cost_limit(),
)
print("submitted:", job.id, "(returns immediately; get_job(id) works from anywhere later)")

job.wait(timeout=300)
print("status:", job.summary()["status"])
print("log:", job.log_text().strip())

data = job.download("output/primes.txt", "primes.txt")   # SHA-256 is checked
print("downloaded primes.txt:", len(data), "bytes")

receipt = job.receipt()
print(f"run time {receipt['duration_ms']} ms, cost {receipt['cost']['amount']} {receipt['cost']['currency']}")
