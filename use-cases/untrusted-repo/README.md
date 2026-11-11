# Run untrusted code away from your machine

Someone sent you a repository, or an agent wants to try a package. Instead of running it on your laptop or CI runner, clone and test it in a disposable microVM:

- its own Linux kernel and disk (Firecracker microVM),
- outbound network limited to an allowlist (here GitHub and PyPI),
- destroyed when the script ends.

This reduces what the code can reach; it is not a full security review of the code. Only test code you are allowed to run.

## Try it in Claude Code or Claude

> Clone https://github.com/pallets/itsdangerous into a WBX sandbox that can only reach GitHub and PyPI, install it and run its tests. Tell me what failed, then destroy the sandbox.

## Run it with the SDK

```bash
python run_tests.py
python run_tests.py https://github.com/<owner>/<repo> "python3 -m pytest -q"
```

Test output is streamed live. Need no network at all after the install? Run the install in one sandbox step, then use a second sandbox created with `internet=False` and copy the files with `sb.files`.
