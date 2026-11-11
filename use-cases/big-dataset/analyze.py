"""Analyse a dataset that is far too big for a chat: 3.8 million NYC taxi trips (65 MB Parquet).

The sandbox downloads the file itself and computes there; only a small summary comes back.
Usage: python analyze.py [parquet-url]
"""
import json
import os
import sys

from wbxsandbox import Sandbox

os.environ.setdefault("WBXSANDBOX_URL", "https://sandbox.wbx.cz")
if not os.environ.get("WBXSANDBOX_API_KEY"):
    raise SystemExit("Set WBXSANDBOX_API_KEY first (see the repository README).")

DATA_URL = sys.argv[1] if len(sys.argv) > 1 else \
    "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-06.parquet"
ZONES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Runs inside the sandbox. pyarrow reads the file one row group at a time, so 512 MB of RAM is enough.
ANALYSIS = r'''
import csv, json, os, sys, collections
import pyarrow.parquet as pq, pyarrow.compute as pc

pf = pq.ParquetFile("/data/trips.parquet")
hours, zones = collections.Counter(), collections.Counter()
tips = collections.defaultdict(lambda: [0.0, 0])
rows = 0
for i in range(pf.num_row_groups):
    t = pf.read_row_group(i, columns=["tpep_pickup_datetime", "PULocationID", "payment_type", "tip_amount"])
    rows += t.num_rows
    for r in pc.value_counts(pc.hour(t["tpep_pickup_datetime"])).to_pylist():
        hours[r["values"]] += r["counts"]
    for r in pc.value_counts(t["PULocationID"]).to_pylist():
        zones[r["values"]] += r["counts"]
    for p, tip in zip(t["payment_type"].to_pylist(), t["tip_amount"].to_pylist()):
        if p is not None and tip is not None:
            tips[p][0] += tip; tips[p][1] += 1

names = {int(r["LocationID"]): r["Zone"] for r in csv.DictReader(open("/data/zones.csv"))}
pay = {0: "Flex fare", 1: "Credit card", 2: "Cash", 3: "No charge", 4: "Dispute", 5: "Unknown", 6: "Voided"}
print(json.dumps({
    "file_bytes": os.path.getsize("/data/trips.parquet"),
    "rows": rows,
    "busiest_hours": hours.most_common(3),
    "avg_tip_by_payment": {pay.get(k, str(k)): round(s / n, 2) for k, (s, n) in sorted(tips.items())},
    "top_pickup_zones": [(names.get(z, str(z)), c) for z, c in zones.most_common(10)],
}))
'''

with Sandbox.create(template="base", timeout=900,
                    allow=["d37ci6vzurychx.cloudfront.net", "pypi.org", "files.pythonhosted.org"]) as sb:
    print("sandbox:", sb.id)
    sb.run("mkdir -p /data && cd /data"
           f" && curl -sSfL -o trips.parquet {DATA_URL}"
           f" && curl -sSfL -o zones.csv {ZONES_URL}"
           " && pip install -q pyarrow", timeout=600).check()

    result = sb.run_code(ANALYSIS, timeout=600).check()
    summary = json.loads(result.stdout)

print(f"\nTrips analysed: {summary['rows']:,}")
print("Busiest hours:", ", ".join(f"{h}:00 ({n:,})" for h, n in summary["busiest_hours"]))
print("Average tip by payment type:", summary["avg_tip_by_payment"])
print("Top pickup zones:")
for zone, count in summary["top_pickup_zones"]:
    print(f"  {zone:<32} {count:>9,}")

print(f"\nData processed in the sandbox: {summary['file_bytes'] / 1e6:.1f} MB")
print(f"Returned to this machine:      {len(result.stdout) / 1e3:.1f} KB")
