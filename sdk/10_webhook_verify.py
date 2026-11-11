"""Verify the X-WBX-Signature header of a job webhook. Runs offline – no API key, no network."""
import hashlib
import hmac
import json
import time

from wbxsandbox import verify_webhook

secret = "example-secret-for-this-demo-only"   # real one: wbxsandbox.webhook_secret()
body = json.dumps({"event": "job.finished", "job_id": "job_example", "status": "completed"}).encode()

t = int(time.time())
mac = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
signature = f"t={t},v1={mac}"

print("genuine payload accepted:", verify_webhook(secret, body, signature))
print("tampered payload accepted:", verify_webhook(secret, body.replace(b"completed", b"failed"), signature))
