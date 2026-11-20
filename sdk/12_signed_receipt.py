"""Signed execution receipt: what ran, on which template build, with which inputs and results – signed by WBX.

Needs the optional package for checking signatures: pip install "wbxsandbox[verify]"."""
from _env import check_env, cost_limit
from wbxsandbox import receipt_keys, run_job, verify_receipt

check_env()

job = run_job(command="sha256sum /etc/os-release", timeout_seconds=60, internet=False, **cost_limit())
job.wait(timeout=300)

signed = job.signed_receipt()          # keep or send this envelope; anyone can verify it
# in production pin the key you trust instead of fetching it from the same server
key = next(k["public_key"] for k in receipt_keys() if k["key_id"] == signed["key_id"])
checked = verify_receipt(signed, public_key=key)
r = checked["execution_receipt"]
print("signed at:", checked["signed_at"], "with key", checked["key_id"])
print("command SHA-256:", r.get("command_sha"))
print("template:", r.get("template"), "image", (r.get("template_build") or {}).get("image_digest"))
