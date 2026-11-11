# WBX Sandbox – examples

**Give your AI agent its own computer.** [WBX Sandbox](https://sandbox.wbx.cz) runs code in isolated Linux microVMs (Firecracker) that start in milliseconds, keep their own files and network rules, and disappear when the work is done. Connect it to Claude, ChatGPT or any MCP client, or drive it from Python.

This repository has two kinds of examples:

- **[Use cases](#use-cases)** – complete tasks you can run as they are, each mirroring something an agent typically does.
- **[SDK basics](#sdk-basics)** – one small script per feature of the Python SDK.

Servers run in the EU. Start free, no card required: **https://sandbox.wbx.cz**

---

## Connect your assistant in a minute

MCP server: `https://sandbox.wbx.cz/mcp`

| Client | How |
|---|---|
| **claude.ai / Claude desktop** | Customize → Connectors → *Add custom connector* → name `WBX Sandbox`, URL `https://sandbox.wbx.cz/mcp` → sign in and *Allow access*. In a chat: **+** → Connectors → turn on WBX Sandbox. |
| **Claude Code** | `claude mcp add --transport http wbxsandbox https://sandbox.wbx.cz/mcp`, then `/mcp` and sign in. |
| **ChatGPT** | Settings → Apps & Connectors → Advanced → *Developer mode* on → *Create*: URL `https://sandbox.wbx.cz/mcp`, authentication OAuth. |
| **Other MCP clients** | See [mcp/](mcp/) for API-key and stdio setups. |

Then just ask, for example:

> Download https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-06.parquet into a WBX sandbox, keep the data out of this chat, and tell me the busiest hours and the top pickup zones.

More tested prompts: [mcp/prompts.md](mcp/prompts.md).

## Use the Python SDK

```bash
pip install https://sandbox.wbx.cz/download/wbxsandbox-sdk.tar.gz   # Python 3.9+, no dependencies
export WBXSANDBOX_URL=https://sandbox.wbx.cz
export WBXSANDBOX_API_KEY=...        # portal → API keys
```

```python
from wbxsandbox import Sandbox

with Sandbox.create(template="base", timeout=120) as sb:
    print(sb.run("uname -sr").stdout)                    # Linux, in a fresh microVM
    print(sb.run_code("print(sum(range(100)))").stdout)  # 4950
# the sandbox is destroyed when the block ends
```

On Windows PowerShell use `$env:WBXSANDBOX_API_KEY = "..."` (or `setx` to keep it). Copy [.env.example](.env.example) if you prefer a file – never commit real keys.

---

## Use cases

| Example | What it shows |
|---|---|
| [big-dataset](use-cases/big-dataset/) | Analyse 3.8 million taxi trips (65 MB Parquet) in the sandbox; only a few kilobytes of results come back. |
| [csv-dashboard](use-cases/csv-dashboard/) | Upload a CSV, compute trends, serve a dashboard and get an HTTPS link to share. |
| [share-web-app](use-cases/share-web-app/) | Run a small live web app (a team poll) in a sandbox and share it over HTTPS. |
| [untrusted-repo](use-cases/untrusted-repo/) | Clone a repository and run its tests in a microVM that can only reach GitHub and PyPI. |
| [budget-batch](use-cases/budget-batch/) | Fan out a batch of background jobs under a hard price limit. |
| [wasm-job](use-cases/wasm-job/) | Build a WebAssembly module locally and run it as a job – no VM template, no network. |

Every use case has a README with the equivalent prompt for Claude or ChatGPT, so you can try it without writing code.

## SDK basics

| Script | Feature |
|---|---|
| [01_hello.py](sdk/01_hello.py) | Create a sandbox, run a command and code, auto-cleanup |
| [02_files.py](sdk/02_files.py) | Write, read, list and remove files |
| [03_streaming.py](sdk/03_streaming.py) | Live output, stdin and exit codes |
| [04_public_url.py](sdk/04_public_url.py) | Start a web server and get its HTTPS address |
| [05_network_rules.py](sdk/05_network_rules.py) | No network, or an allowlist of domains |
| [06_background_job.py](sdk/06_background_job.py) | Fire-and-forget job, logs, result files with SHA-256 check |
| [07_batch_dependencies.py](sdk/07_batch_dependencies.py) | Batch where job B consumes job A's result |
| [08_pause_resume.py](sdk/08_pause_resume.py) | Pause, resume and extend a sandbox |
| [09_budget_and_compute.py](sdk/09_budget_and_compute.py) | Read budget, billing currency and compute classes (read-only) |
| [10_webhook_verify.py](sdk/10_webhook_verify.py) | Verify a signed job webhook (offline) |

Run any of them with `python sdk/01_hello.py`.

## Costs and safety

- The examples create real sandboxes and jobs and are billed per second of vCPU and memory. They use short lifetimes and clean up after themselves. Current prices: https://sandbox.wbx.cz/pricing
- Price limits (`max_cost`, `max_total_cost`) are in your account's billing currency – check it with `sdk/09_budget_and_compute.py`.
- Keep API keys in environment variables or a secret store, never in code, logs or chat.
- Only run [untrusted-repo](use-cases/untrusted-repo/) and similar examples against code and sites you are allowed to test.

## Repository layout

```
use-cases/   complete tasks, each with README, prompt and script
sdk/         one script per SDK feature
mcp/         client setup and tested prompts for AI assistants
tests/       offline checks (no API key, no network) – run by CI
```

```bash
python -m unittest discover -s tests -v
```

## Links

- Website and sign-up: https://sandbox.wbx.cz
- Documentation: https://sandbox.wbx.cz/docs
- Pricing: https://sandbox.wbx.cz/pricing

Licensed under the [MIT License](LICENSE).
