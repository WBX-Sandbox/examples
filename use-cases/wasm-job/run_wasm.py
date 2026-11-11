"""Run a WebAssembly (WASI preview1) module as a WBX job: no VM template, no network, fast start.

Build the module first:
    cd wasm-hello && cargo build --release --target wasm32-wasip1
"""
import os
from pathlib import Path

from wbxsandbox import run_job

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

module = Path(__file__).parent / "wasm-hello/target/wasm32-wasip1/release/wasm-hello.wasm"
if not module.exists():
    raise SystemExit(f"Build the module first: {module.parent.parent.parent} → cargo build --release --target wasm32-wasip1")
print(f"module: {module.name}, {module.stat().st_size:,} bytes")

job = run_job(wasm_module=module.read_bytes(), wasm_args=["WBX"],
              wasm_stdin="WebAssembly jobs need\nno VM template\nand no network.\n", wasm_memory_mb=64)
job.wait(timeout=120)
print(job.log_text().strip())

receipt = job.receipt()
print(f"run time {receipt['duration_ms']} ms · cost {receipt['cost']['amount']} {receipt['cost']['currency']}")
print("isolation:", receipt["security"]["isolation"])
