from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from statistics import mean
import json
import os
import math

app = FastAPI()

# Enable CORS for all origins and POST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data bundled with deployment
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")

with open(DATA_FILE, "r") as f:
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
        uptimes = [x["uptime"] for x in rows]

        result[r] = {
            "avg_latency": mean(latencies),
            "p95_latency": percentile(latencies, 0.95),
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return result