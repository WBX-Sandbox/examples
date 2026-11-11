"""A batch where job B waits for job A and receives A's result file (checked by SHA-256)."""
from _env import check_env
from wbxsandbox import batch_input, run_batch

check_env()

produce = {
    "command": "mkdir -p output && python3 -c \"print(sum(range(1_000_000)))\" > output/value.txt",
    "timeout_seconds": 60, "internet": False,
    "artifacts": ["output/value.txt"], "required_artifacts": ["output/value.txt"],
}
consume = {
    "command": "mkdir -p output && echo \"A computed $(cat input/value.txt)\" | tee output/result.txt",
    "timeout_seconds": 60, "internet": False, "depends_on": [0],
    "inputs": [batch_input(0, "output/value.txt", "value.txt")],
    "artifacts": ["output/result.txt"], "required_artifacts": ["output/result.txt"],
}

batch = run_batch([produce, consume], max_concurrency=2, name="sdk-example-dependencies")
batch.wait(timeout=300)

summary = batch.summary()
print("batch status:", summary.get("status"))
for job in batch.jobs():
    print(" ", job.id, job.status, "|", job.log_text().strip())
