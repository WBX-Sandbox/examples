# WebAssembly jobs

Compile a program to WebAssembly (WASI preview1) on any OS, then run it on WBX as a job. There is no VM template to boot and no network: the module runs in its own unprivileged process with memory and CPU limits.

Note the isolation level: a WebAssembly job is isolated by the WASI runtime and Linux process controls, which is **lighter than a microVM**. The execution receipt says so (`"isolation": "wasm-process"`). Use a regular sandbox or job when you need a full VM boundary.

## Build and run

```bash
rustup target add wasm32-wasip1
cd wasm-hello && cargo build --release --target wasm32-wasip1 && cd ..
python run_wasm.py
```

Output from our run (11 Nov 2026):

```
Hello, WBX! (running as a WebAssembly job on WBX Sandbox)
stdin: 3 lines, 9 words, 53 characters
run time 36 ms · cost 0.000007 CZK
isolation: wasm-process
```

Any language that targets WASI preview1 works (Rust, C/C++ with wasi-sdk, Zig, TinyGo). Modules up to 8 MB can be sent inline; larger ones can be passed as an input file of a previous job.
