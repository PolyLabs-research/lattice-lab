"""
Is the chance model honest? On random symmetric square rules (unions of D4 orbits of the
translations within distance 4), compare the confinements the model expects with those found.

    uv run --no-sync python examples/census-remainder/calibrate.py <seed> <count> <m> [<m> ...]

Exploratory only: its seeds must never be the registered test's.
"""

import itertools
import json
import random
import sys
import time

import atlas3
import remainder
from remainder import census

ORBITS = sorted(
    {
        tuple(sorted((abs(a), abs(b)), reverse=True))
        for a, b in itertools.product(range(-4, 5), repeat=2)
    }
)


def orbit(a, b):
    return {(s * x, t * y) for x, y in ((a, b), (b, a)) for s in (1, -1) for t in (1, -1)}


def random_rules(seed, count):
    rng, out, seen = random.Random(seed), [], set()
    while len(out) < count:
        pick = tuple(o for o in ORBITS if rng.random() < 0.5)
        if not pick or pick in seen:
            continue
        seen.add(pick)
        f = frozenset().union(*(orbit(*o) for o in pick))
        out.append((pick, f))
    return out


def tally(rules, m):
    mean = var = 0.0
    population = forced = observed = 0
    hits = []
    for pick, f in rules:
        predicted, _ = atlas3.predict(f, m)
        N = 2 ** census.eigen.field(m)[1] - 1
        if predicted is None or (N // 3) % predicted == 0:
            continue  # explained by a known mechanism, or no prediction
        a = remainder.analyse(f, m)
        population += 1
        if a["forced"]:
            forced += 1
            continue
        mean += a["chance"]
        var += a["chance"] * (1 - a["chance"])
        if a["cubes"]:
            observed += 1
            hits.append([list(pick), a["free"], round(a["chance"], 5)])
    return {
        "m": m,
        "population": population,
        "forced": forced,
        "expected": round(mean, 2),
        "sd": round(var**0.5, 2),
        "observed": observed,
        "hits": hits,
    }


if __name__ == "__main__":
    seed, count, ms = int(sys.argv[1]), int(sys.argv[2]), [int(x) for x in sys.argv[3:]]
    rules = random_rules(seed, count)
    for m in ms:
        t = time.time()
        r = tally(rules, m)
        print(
            json.dumps({k: v for k, v in r.items() if k != "hits"}),
            f"{time.time() - t:.0f}s",
            flush=True,
        )
