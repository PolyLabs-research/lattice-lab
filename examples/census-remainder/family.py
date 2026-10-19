"""
Every symmetric square rule within distance 4 (all 2^15 unions of the D4 orbits of the
translations with coordinates in [-4, 4]): at odd m, which are confined to the cubes although
no known mechanism predicts it, and what the chance model expects.

    uv run --no-sync python examples/census-remainder/family.py <m>

Writes family-<m>.json.
"""

import json
import sys
import time
from pathlib import Path

import atlas3
import remainder
from calibrate import ORBITS, orbit
from remainder import census

HERE = Path(__file__).resolve().parent
m = int(sys.argv[1])
N = 2 ** census.eigen.field(m)[1] - 1
t = time.time()
mean = var = 0.0
population, forced, hits = 0, [], []
for bits in range(1, 2 ** len(ORBITS)):
    pick = [o for i, o in enumerate(ORBITS) if bits >> i & 1]
    f = frozenset().union(*(orbit(*o) for o in pick))
    predicted, _ = atlas3.predict(f, m)
    if predicted is None or (N // 3) % predicted == 0:
        continue
    a = remainder.analyse(f, m)
    population += 1
    if a["forced"]:
        forced.append(pick)
        continue
    mean += a["chance"]
    var += a["chance"] * (1 - a["chance"])
    if a["cubes"]:
        hits.append({"orbits": pick, "free": a["free"], "chance": a["chance"]})
out = {
    "m": m,
    "population": population,
    "forced": len(forced),
    "expected": mean,
    "sd": var**0.5,
    "observed": len(hits),
    "hits": hits,
    "seconds": round(time.time() - t),
}
(HERE / f"family-{m}.json").write_text(json.dumps(out) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "hits"}))
