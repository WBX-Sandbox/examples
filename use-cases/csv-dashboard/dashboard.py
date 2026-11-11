"""Upload a CSV, find growing and declining products, and share a dashboard over HTTPS.

Usage: python dashboard.py [file.csv]   (columns: date, product, quantity, unit_price)
"""
import os
import sys
import time
from pathlib import Path

from wbxsandbox import Sandbox

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("sales-2026.csv"))

# Runs inside the sandbox: standard library only, writes a self-contained page (no CDN).
BUILD = r'''
import csv, collections, html
rev = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open("/home/user/data.csv")):
    rev[r["product"]][r["date"][:7]] += int(r["quantity"]) * float(r["unit_price"])
months = sorted({m for p in rev.values() for m in p})
first, last = months[:3], months[-3:]
rows = []
for p, by in rev.items():
    a, b = sum(by[m] for m in first), sum(by[m] for m in last)
    rows.append((p, a, b, (b / a - 1) * 100 if a else 0))
rows.sort(key=lambda r: -r[3])

def bars(values, w=560, h=180):
    top = max(values) or 1; bw = w / len(values)
    return "".join(f'<rect x="{i*bw+4:.0f}" y="{h-v/top*h:.0f}" width="{bw-8:.0f}" height="{v/top*h:.0f}" rx="2"/>'
                   for i, v in enumerate(values))

cards = "".join(
    f'<section><h2>{html.escape(p)} <span class="{"up" if g >= 5 else "down" if g <= -5 else ""}">{g:+.0f}%</span></h2>'
    f'<svg viewBox="0 0 560 180">{bars([rev[p][m] for m in months])}</svg>'
    f'<p>{months[0]} – {months[-1]} · last 3 months {b:,.0f} vs first 3 months {a:,.0f}</p></section>'
    for p, a, b, g in rows)
open("/home/user/site/index.html", "w").write(f"""<!doctype html><meta charset="utf-8">
<title>Product trends</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font:15px system-ui,sans-serif;margin:32px;background:#f4f6f8;color:#111a24}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}}
section{{background:#fff;border:1px solid #dde3e7;border-radius:6px;padding:16px}}
h2{{font-size:17px;margin:0 0 8px}} svg{{width:100%;fill:#2457c5}} p{{color:#5d6b77;margin:8px 0 0}}
.up{{color:#16794a}} .down{{color:#b42318}}</style>
<h1>Product trends</h1><main>{cards}</main>""")
for p, a, b, g in rows:
    print(f"{p:<20} {g:+6.1f}%")
'''

with Sandbox.create(template="base", timeout=1800, internet=False) as sb:
    sb.files.write("/home/user/data.csv", csv_path.read_bytes())
    sb.run("mkdir -p /home/user/site", timeout=5).check()
    print("Revenue change, last 3 months vs first 3 months:")
    print(sb.run_code(BUILD, timeout=60).check().stdout)

    sb.run("cd /home/user/site && nohup python3 -m http.server 8000 --bind 0.0.0.0 >/tmp/web.log 2>&1 &",
           timeout=5).check()
    time.sleep(1)
    print("Dashboard (share this link):", sb.get_url(8000)["url_with_token"])
    input("Press Enter to stop the dashboard and destroy the sandbox... ")
