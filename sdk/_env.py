"""Shared setup for the SDK examples: default endpoint and a clear error without an API key."""
import os


def check_env():
    os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
    if not os.environ.get("WBXSANDBOX_API_KEY", "").strip():
        raise SystemExit("Set WBXSANDBOX_API_KEY first (portal → API keys). See README.md.")


def cost_limit():
    """Optional price limit for jobs from WBX_MAX_COST, in your account's billing currency."""
    value = os.environ.get("WBX_MAX_COST", "").strip()
    return {"max_cost": value} if value else {}
