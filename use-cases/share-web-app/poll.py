"""Run a small live web app – a team lunch poll – in a sandbox and share it over HTTPS.

Usage: python poll.py ["Option A,Option B,Option C"]
"""
import json
import os
import sys
import time

from wbxsandbox import Sandbox

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

options = (sys.argv[1] if len(sys.argv) > 1 else "Pizza Place,Sushi Bar,Burger Joint,Thai Kitchen").split(",")

APP = r'''
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
OPTIONS = json.load(open("/home/user/options.json"))
votes, lock = {}, threading.Lock()          # one vote per browser (cookie id)
PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Where's lunch today?</title><style>body{font:16px system-ui;max-width:520px;margin:40px auto;padding:0 16px}
button{display:flex;justify-content:space-between;width:100%;padding:12px;margin:8px 0;border:1px solid #dde3e7;
border-radius:6px;background:#fff;font:inherit;cursor:pointer}button.me{border-color:#2457c5}</style>
<h1>Where's lunch today?</h1><div id=o></div><p id=n></p><script>
const id=localStorage.id||(localStorage.id=crypto.randomUUID());
async function load(v){const r=await fetch(v===undefined?'state?id='+id:'vote?id='+id+'&o='+v,{method:v===undefined?'GET':'POST'});
const s=await r.json();o.innerHTML=s.options.map((x,i)=>`<button class="${s.mine===i?'me':''}" onclick="load(${i})">
<span>${x}</span><span>${s.counts[i]}</span></button>`).join('');n.textContent=s.total+' votes';}
load();setInterval(load,2000);</script>"""
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def reply(self, body, ctype="application/json"):
        self.send_response(200); self.send_header("Content-Type", ctype); self.end_headers(); self.wfile.write(body.encode())
    def state(self, me):
        counts = [list(votes.values()).count(i) for i in range(len(OPTIONS))]
        return json.dumps({"options": OPTIONS, "counts": counts, "total": len(votes), "mine": votes.get(me)})
    def do_GET(self):
        if self.path.startswith("/state"): self.reply(self.state(self.path.split("id=")[-1]))
        else: self.reply(PAGE, "text/html; charset=utf-8")
    def do_POST(self):
        q = dict(p.split("=") for p in self.path.split("?", 1)[1].split("&"))
        with lock:
            if 0 <= int(q["o"]) < len(OPTIONS): votes[q["id"]] = int(q["o"])
        self.reply(self.state(q["id"]))
ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
'''

with Sandbox.create(template="base", timeout=3600, internet=False) as sb:
    sb.files.write("/home/user/options.json", json.dumps(options))
    sb.files.write("/home/user/poll.py", APP)
    sb.run("nohup python3 /home/user/poll.py >/tmp/poll.log 2>&1 &", timeout=5).check()
    time.sleep(1)
    print("Share this link with your team:", sb.get_url(8000)["url_with_token"])
    print("The poll runs for up to an hour; votes live only in this sandbox.")
    input("Press Enter to close the poll and destroy the sandbox... ")
