"""Refined single-k rule, and the k=8/k=4 layer ratio trend with n."""
from common import *
from orbits import admissible
import numpy as np

rows = json.load(open("groups.json"))
for r in rows:
    r["kd"] = {int(k): v for k, v in r["kd"].items()}; r["g"] = tuple(r["g"])

def adm_orders(g):
    E = odd_exponent(*g)
    return [t for t in (3, 7, 15, 31, 63, 73, 85, 127) if E % t == 0]

def prank(g, p):
    return sum(1 for x in g if x % p == 0)

tab = Counter(); miss = []
for r in rows:
    S = adm_orders(r["g"])
    # rule: r2 <= 1, exactly one admissible order t, every prime of t has rank 1
    pred = r["r2"] <= 1 and len(S) == 1 and all(prank(r["g"], p) == 1 for p in factor(S[0]))
    act = len(r["kset"]) == 1
    tab[(pred, act)] += 1
    if pred != act:
        miss.append((r["g"], S, r["r2"], r["kset"]))
print("(predicted single k, actually single k):", dict(tab))
print("misses:", miss)

# layer ratio trend
print("\nd8/d4 by n band (groups with both):")
v = [(r["n"], r["kd"][8] / r["kd"][4]) for r in rows if 8 in r["kd"] and 4 in r["kd"]]
for lo, hi in [(0, 100), (100, 200), (200, 300), (300, 400)]:
    x = [b for a, b in v if lo < a <= hi]
    print(f"  ({lo},{hi}]: n={len(x)} mean {np.mean(x):.3f} min {min(x):.3f} max {max(x):.3f}")
print("d4 - d8 (absolute gap) by band:")
v2 = [(r["n"], r["kd"][4] - r["kd"][8]) for r in rows if 8 in r["kd"] and 4 in r["kd"]]
for lo, hi in [(0, 100), (100, 200), (200, 300), (300, 400)]:
    x = [b for a, b in v2 if lo < a <= hi]
    print(f"  ({lo},{hi}]: n={len(x)} gaps {Counter(x)}")
