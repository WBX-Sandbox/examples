"""Network rules per sandbox: no network at all, or only an allowlist of destinations.

A refused connection here is a quick check of the rule you set, not a full security audit.
"""
from _env import check_env
from wbxsandbox import Sandbox

check_env()

PROBE = "curl -sf -o /dev/null -m 5 {url} && echo reachable || echo blocked"

with Sandbox.create(timeout=120, internet=False) as sb:
    print("no network  → pypi.org:", sb.run(PROBE.format(url="https://pypi.org"), timeout=15).stdout.strip())

with Sandbox.create(timeout=120, allow=["pypi.org", "files.pythonhosted.org"]) as sb:
    print("allowlist   → pypi.org:", sb.run(PROBE.format(url="https://pypi.org"), timeout=15).stdout.strip())
    print("allowlist   → example.com:", sb.run(PROBE.format(url="https://example.com"), timeout=15).stdout.strip())
