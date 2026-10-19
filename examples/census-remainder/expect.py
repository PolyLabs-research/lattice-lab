"""
For each census size: the rules the atlas procedure gives the full bound, how many of them are
confined by forced subfields (structure), and how many confinements chance would give.

    uv run --no-sync python examples/census-remainder/expect.py [lo hi]

Writes expected.jsonl, one line per m.
"""

import json
import sys
import time
from pathlib import Path

import remainder
from remainder import census

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected.jsonl"
lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (9, 161)
done = {json.loads(line)["m"] for line in OUT.read_text().splitlines()} if OUT.exists() else set()
for m in census.cube_sizes(lo, hi):
    if m in done:
        continue
    t = time.time()
    mean = var = 0.0
    forced, confined_free, population = [], [], 0
    for lattice, shells, f in census.rules():
        key = (lattice, shells)
        if key in census.TWISTED and census._twisted(m) is not None:
            continue
        if census.explained(f, m, 3, key):
            continue  # a known mechanism predicts cube confinement, or makes no prediction
        a = remainder.analyse(f, m)
        population += 1
        name = f"{lattice} {'+'.join(shells)}"
        if a["forced"]:
            forced.append(name)
            continue
        p = a["chance"]
        mean += p
        var += p * (1 - p)
        if a["cubes"]:
            confined_free.append([name, round(p, 6), a["free"]])
    row = {
        "m": m,
        "population": population,
        "forced": forced,
        "expected": round(mean, 3),
        "sd": round(var**0.5, 3),
        "observed": len(confined_free),
        "confined": confined_free,
        "seconds": round(time.time() - t, 1),
    }
    with open(OUT, "a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(
        m,
        population,
        "forced",
        len(forced),
        "expected",
        row["expected"],
        "+-",
        row["sd"],
        "observed",
        row["observed"],
        f"{row['seconds']}s",
        flush=True,
    )
