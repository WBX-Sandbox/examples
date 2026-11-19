# AI data analyst in one Python file

Ask a question about a CSV, Excel or Parquet file. A model writes Python, WBX Sandbox runs it, the model reads the short output and keeps going until it can answer. Charts come back as PNG files.

```
python analyst.py "Which products are growing and which are declining?"
```

**Why a sandbox:** the code is written by a model, so it runs in a Firecracker microVM with its own kernel, not on your machine. The sandbox has no internet access (or only the host your data comes from), and it is destroyed when the script ends.

**Why it saves tokens:** the data goes into the sandbox, not into the prompt. The model sees the file names and sizes, the code it wrote and at most a few thousand characters of output per step. A 50 MB file costs about as much as a 50 kB one. At the end the script prints how much data stayed in the sandbox and how much text went to the model.

## Run it

```bash
pip install wbxsandbox openai
export WBXSANDBOX_API_KEY=...   # https://sandbox.wbx.cz → API keys
export OPENAI_API_KEY=...

python analyst.py "Which products are growing?"                         # bundled demo data (../csv-dashboard/sales-2026.csv)
python analyst.py "What are the busiest hours?" trips.parquet zones.csv  # your files are uploaded
python analyst.py "Is it getting warmer?" https://example.org/data.csv   # the sandbox downloads it itself
```

Charts are saved to `./analyst-output/`.

Other models: any OpenAI-compatible API works. Set `OPENAI_BASE_URL` and `ANALYST_MODEL` (default `gpt-5.4-mini`).

## How it works

1. `Sandbox.create(template="code-interpreter", internet=False)` – pandas, numpy, scipy, matplotlib, seaborn, openpyxl and pyarrow are preinstalled, so nothing has to be downloaded.
2. Your files are copied to `/home/user/data`. With URLs, the sandbox is created with an allowlist of just those hosts and fetches the files with `curl`.
3. The model gets one tool, `run_python(code)`. Each call runs a full script (`sb.run_code`). The result is the exit code, clipped stdout/stderr and the list of files in `/home/user/out`.
4. When the model answers without calling the tool, the charts are downloaded and the sandbox is destroyed.

The loop itself (`analyse()`) has no network code. It takes a `chat(messages)` function, so you can plug in another model or framework. `tests/test_offline.py` runs it with a scripted model and a fake sandbox.

## Try it in Claude or ChatGPT instead

No code needed. Connect WBX Sandbox (see the [main README](../../README.md)) and ask:

> Download https://raw.githubusercontent.com/WBX-Sandbox/examples/main/use-cases/csv-dashboard/sales-2026.csv into a WBX sandbox, keep the data out of this chat, and tell me which products are growing and which are declining. Make a chart.

## Ideas for extending it

- A web UI: wrap `analyse()` in a small FastAPI app and run it in a sandbox with `sb.get_url(port)`.
- Keep the sandbox: create it with a name and `on_timeout="pause"` so follow-up questions reuse the loaded data.
- Big data: point it at a Parquet URL, like in [big-dataset](../big-dataset/).
