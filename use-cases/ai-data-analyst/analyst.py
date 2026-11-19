"""AI data analyst: ask a question about your data, a model writes Python, WBX Sandbox runs it.

The data goes into the sandbox, not into the prompt. The model only sees file names, the code it
wrote and the short output of that code, so a 50 MB file costs about as many tokens as a 5 kB one.
Charts are copied back to ./analyst-output/.

Usage:
  python analyst.py "Which products are growing?"                      # bundled demo data
  python analyst.py "Busiest hours?" trips.parquet zones.csv           # your files
  python analyst.py "Is it getting warmer?" https://example.org/x.csv  # the sandbox downloads it

Needs WBXSANDBOX_API_KEY and OPENAI_API_KEY (any OpenAI-compatible API works: set OPENAI_BASE_URL
and ANALYST_MODEL). Install: pip install wbxsandbox openai
"""
import json
import os
import shlex
import sys
from pathlib import Path
from urllib.parse import urlparse

DATA_DIR = "/home/user/data"
OUT_DIR = "/home/user/out"
MAX_STEPS = 12
MAX_OUTPUT = 6000  # characters of program output sent back to the model per step

SYSTEM = f"""You are a careful data analyst. You answer questions about data files by writing Python.
Tool run_python runs a complete script in an isolated Linux sandbox and returns its exit code, output
and the files in {OUT_DIR}. Each call is a new process: variables do not survive between calls, files do.
Installed: pandas, numpy, scipy, matplotlib, seaborn, openpyxl, pyarrow. There is no internet access.
The data is in {DATA_DIR}. Start by inspecting it (shape, columns, a few rows) before analysing.
Print only short summaries: never print whole tables. Save every chart as PNG to {OUT_DIR}
(plt.savefig, then plt.close()). When you are done, answer in plain language with the key numbers
and name the chart files you made. Say clearly if the data cannot answer the question."""

TOOLS = [{
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "Run a complete Python script in the sandbox and return exit code, output and files in "
                       + OUT_DIR,
        "parameters": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "The full Python script."}},
            "required": ["code"],
        },
    },
}]


def clip(text, limit=MAX_OUTPUT):
    """Keep the start and the end of long output; the model rarely needs the middle."""
    if len(text) <= limit:
        return text
    half = limit // 2
    return f"{text[:half]}\n... [{len(text) - limit} characters cut] ...\n{text[-half:]}"


def run_python(sb, code):
    """Run one script in the sandbox; return the text the model gets back."""
    r = sb.run_code(code, timeout=300)
    files = sorted(f["name"] for f in sb.files.list(OUT_DIR) if not f.get("is_dir"))
    parts = [f"exit code: {r.exit_code}" + (" (timed out)" if r.timed_out else "")]
    if r.stdout.strip():
        parts.append("stdout:\n" + clip(r.stdout))
    if r.stderr.strip():
        parts.append("stderr:\n" + clip(r.stderr, 3000))
    parts.append("files in out/: " + (", ".join(files) or "none"))
    return "\n".join(parts)


def analyse(question, sb, chat, data_files, log=print):
    """The agent loop. `chat(messages)` returns an OpenAI-style assistant message (dict).

    Returns (answer, stats). Kept free of network code so it can be tested with fakes.
    """
    listing = "\n".join(f"- {DATA_DIR}/{name} ({size:,} bytes)" for name, size in data_files)
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Data files:\n{listing}\n\nQuestion: {question}"}]
    stats = {"steps": 0, "chars_to_model": 0}
    for _ in range(MAX_STEPS):
        msg = chat(messages)
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        if not calls:
            return msg.get("content") or "", stats
        for call in calls:
            stats["steps"] += 1
            try:
                code = json.loads(call["function"]["arguments"])["code"]
            except (KeyError, ValueError):
                result = "error: arguments must be JSON with a 'code' string"
            else:
                log(f"\n--- step {stats['steps']}: running {len(code.splitlines())} lines of Python")
                result = run_python(sb, code)
                log(clip(result, 800))
            stats["chars_to_model"] += len(result)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return "Stopped after %d steps without a final answer." % MAX_STEPS, stats


def openai_chat(model):
    from openai import OpenAI
    client = OpenAI()  # reads OPENAI_API_KEY and OPENAI_BASE_URL

    def chat(messages):
        m = client.chat.completions.create(model=model, messages=messages, tools=TOOLS).choices[0].message
        msg = {"role": "assistant", "content": m.content or ""}
        if m.tool_calls:
            msg["tool_calls"] = [{"id": c.id, "type": "function",
                                  "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                 for c in m.tool_calls]
        return msg
    return chat


def main():
    os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
    for key in ("WBXSANDBOX_API_KEY", "OPENAI_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"Set {key} first (see README.md).")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    question = sys.argv[1]
    sources = sys.argv[2:] or [str(Path(__file__).resolve().parents[1] / "csv-dashboard" / "sales-2026.csv")]
    urls = [s for s in sources if s.startswith(("http://", "https://"))]
    paths = [Path(s) for s in sources if s not in urls]

    from wbxsandbox import Sandbox
    # No internet unless the data has to be downloaded, and then only from those hosts.
    network = {"allow": sorted({urlparse(u).hostname for u in urls})} if urls else {"internet": False}
    with Sandbox.create(template="code-interpreter", timeout=1800, **network) as sb:
        print("sandbox:", sb.id)
        sb.run(f"mkdir -p {DATA_DIR} {OUT_DIR}", timeout=10).check()
        for p in paths:
            sb.files.write(f"{DATA_DIR}/{p.name}", p.read_bytes())
        for u in urls:
            name = Path(urlparse(u).path).name or "download"
            sb.run(f"curl -sSfL -o {shlex.quote(DATA_DIR + '/' + name)} {shlex.quote(u)}", timeout=600).check()
        data_files = [(f["name"], f["size"]) for f in sb.files.list(DATA_DIR) if not f.get("is_dir")]

        answer, stats = analyse(question, sb, openai_chat(os.environ.get("ANALYST_MODEL", "gpt-5.4-mini")),
                                data_files)

        local = Path("analyst-output")
        charts = [f["name"] for f in sb.files.list(OUT_DIR) if not f.get("is_dir")]
        for name in charts:
            local.mkdir(exist_ok=True)
            (local / name).write_bytes(sb.files.read(f"{OUT_DIR}/{name}"))

    print("\n=== Answer ===\n" + answer)
    if charts:
        print("\nCharts:", ", ".join(str(local / n) for n in charts))
    data_bytes = sum(size for _, size in data_files)
    print(f"\nData in the sandbox: {data_bytes:,} bytes. "
          f"Program output sent to the model: {stats['chars_to_model']:,} characters in {stats['steps']} steps.")


if __name__ == "__main__":
    main()
