from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from statistics import mean
import json, os, math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(DATA_FILE) as f:
    DATA = json.load(f)

def percentile(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] * (c - k) + values[c] * (k - f)

@app.post("/api")
def analytics(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for r in regions:
        rows = [x for x in DATA if x["region"] == r]
        latencies = [x["latency_ms"] for x in rows]
        uptimes = [x["uptime_pct"] for x in rows]

        result[r] = {
            "avg_latency": round(mean(latencies), 2),
            "p95_latency": round(percentile(latencies, 0.95), 2),
            "avg_uptime": round(mean(uptimes), 2),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return result
