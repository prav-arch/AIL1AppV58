#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path
import subprocess
from datetime import datetime, timedelta
import argparse

def get_event_time(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

INPUT_JSON = "/home/users/praveen.joe/logs/interference_splane_issues.json"
OUTPUT_JSON = "/home/users/praveen.joe/logs/interference_splane_ml_anomalies.json"

parser = argparse.ArgumentParser()
parser.add_argument('--demo', action='store_true', help='Generate demo anomalies instead of using real data')
args = parser.parse_args()

def insert_to_clickhouse(records, table, fields):
    import tempfile
    if not records:
        now = get_event_time()
        records = [{
            "event_time": now,
            "type": "none",
            "severity": "none",
            "log_line": "NO_ANOMALY_FOUND"
        }]
    with tempfile.NamedTemporaryFile("w", delete=False) as fout:
        for row in records:
            out = {field: row.get(field, "") for field in fields}
            fout.write(json.dumps(out) + "\n")
        fname = fout.name
    cmd = [
        "clickhouse-client", "--host", "localhost",
        "--database", "l1_app_db",
        "--query", f"INSERT INTO {table} ({','.join(fields)}) FORMAT JSONEachRow"
    ]
    with open(fname, "rb") as fin:
        subprocess.run(cmd, stdin=fin)
    print(f"[ClickHouse] Inserted {len(records)} records into {table}")

if args.demo:
    now = datetime.utcnow()
    demo_anomalies = [
        {
            "event_time": (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "interference",
            "severity": "high",
            "log_line": "[09:50:25] SINR drop detected for cell 101"
        },
        {
            "event_time": (now - timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "interference",
            "severity": "medium",
            "log_line": "[09:52:05] CRC error spike for RU 4"
        },
        {
            "event_time": (now - timedelta(minutes=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "s_plane_delay",
            "severity": "high",
            "log_line": "[09:53:30] F1SetupRequest took 520ms for DU 8"
        },
        {
            "event_time": (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "s_plane_delay",
            "severity": "low",
            "log_line": "[09:55:15] UEContextSetupRequest took 220ms for UE 2042"
        },
        {
            "event_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "interference",
            "severity": "high",
            "log_line": "[10:00:00] RSRP at -105 dBm for cell 103, likely interference"
        }
    ]
    print(f"[DEMO] Generated {len(demo_anomalies)} demo anomalies.")
    insert_to_clickhouse(
        demo_anomalies,
        "interference_splane",
        ["event_time", "type", "severity", "log_line"]
    )
    Path(OUTPUT_JSON).write_text(json.dumps(demo_anomalies, indent=2))
    exit(0)

with open(INPUT_JSON) as f:
    data = json.load(f)

if not isinstance(data, list) or not data:
    print(f"[ML] No anomalies found in {INPUT_JSON}. Exiting.")
    Path(OUTPUT_JSON).write_text("[]")
    insert_to_clickhouse([], "interference_splane", ["event_time", "type", "severity", "log_line"])
    exit(0)

df = pd.DataFrame(data)
if "severity" not in df.columns:
    print(f"[ML] No 'severity' column in input data. Exiting.")
    Path(OUTPUT_JSON).write_text("[]")
    insert_to_clickhouse([], "interference_splane", ["event_time", "type", "severity", "log_line"])
    exit(0)

df["is_high"] = df["severity"] == "high"
anomalies = df[df["is_high"]].to_dict(orient="records")
for a in anomalies:
    if "event_time" in a:
        try:
            dt = datetime.strptime(a["event_time"][:19], "%Y-%m-%d %H:%M:%S")
            a["event_time"] = get_event_time(dt)
        except Exception:
            a["event_time"] = get_event_time()
    else:
        a["event_time"] = get_event_time()
print(f"[ML] wrote {len(anomalies)} anomalies → {OUTPUT_JSON}")
Path(OUTPUT_JSON).write_text(json.dumps(anomalies, indent=2))
insert_to_clickhouse(anomalies, "interference_splane", ["event_time", "type", "severity", "log_line"])
