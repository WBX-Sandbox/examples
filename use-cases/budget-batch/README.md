# A batch of jobs under a hard price limit

Agents that fan out work can burn money fast. Give the batch a total price limit: the platform computes the worst case (all jobs, full time limits) before anything starts and refuses the batch if it could exceed the limit. Nothing is billed for a refused batch.

## Try it in Claude or ChatGPT

> In WBX Sandbox, run 5 background jobs in parallel, each simulating a forecast scenario with a different random seed, with a total price limit of 1.00. First show me what happens with a limit of 0.0001.

## Run it with the SDK

```bash
python batch.py 2.00   # limit in your account's billing currency
```

The script reads your billing currency with `get_budget()`, shows a refused batch with a tiny limit, then runs the real one and downloads each job's result file. You only pay for the time the jobs actually ran.
