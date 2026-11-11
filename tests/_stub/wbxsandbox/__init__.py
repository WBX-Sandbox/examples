"""Minimal stand-in for the SDK so offline tests can import the examples without installing it.
Any real call fails loudly – the tests only check behaviour before the first API call."""


def _unavailable(*args, **kwargs):
    raise RuntimeError("stub SDK: no network in offline tests")


Sandbox = type("Sandbox", (), {"create": staticmethod(_unavailable)})
SandboxError = RuntimeError
run_job = run_batch = get_budget = batch_input = compute_preferences = runtimes = _unavailable
