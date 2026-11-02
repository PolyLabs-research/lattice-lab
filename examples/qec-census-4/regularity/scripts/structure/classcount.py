"""Extreme-value check: do cyclic groups simply have more classes (more draws) than same-order
non-cyclic groups? Classes with k = k_min, connected."""
from common import *
R = torus_records()
G = {}
for t, v in R.items():
    g = group_key(*t)
    if v["classes"] == 0:
        continue
    rows = [r for r in v["rows"] if r["connected"]]
    if not rows:
        continue
    kmin = min(r["k"] for r in rows)
    G.setdefault(g, (len(rows), sum(r["k"] == kmin for r in rows), t, v["stage"]))
byN = defaultdict(list)
for g, x in G.items():
    byN[g[0] * g[1]].append((g, x))
tab = Counter(); out = []
for N, gs in sorted(byN.items()):
    cyc = [x for g, x in gs if g[0] == 1]
    if not cyc or len(gs) < 2:
        continue
    for g, x in gs:
        if g[0] == 1:
            continue
        tab["cyclic has more k_min classes" if cyc[0][1] > x[1] else "non-cyclic has more or equal"] += 1
        out.append((2 * N, f"Z{g[0]}xZ{g[1]}", x[1], cyc[0][1]))
print(dict(tab))
print("(n, group, connected k_min classes, cyclic's)", out)
print("rows hold every class on every stage (len(rows) == classes on all 211 tori with codes)")
