"""Group structure vs envelope height, k-set and score (deduplicated by group)."""
from common import *
import numpy as np

rows = json.load(open("groups.json"))
for r in rows:
    r["kd"] = {int(k): v for k, v in r["kd"].items()}
    r["g"] = tuple(r["g"])

def typ(r):
    return ("cyc" if r["cyclic"] else "noncyc") + f" r2={r['r2']} r3={r['r3']}"

byn = defaultdict(list)
for r in rows:
    byn[r["n"]].append(r)

# (a) d-envelope: cyclic vs non-cyclic at k_min in columns with >= 2 groups
print("== (a) top of column: cyclic group vs best non-cyclic group of the same order")
tally = Counter(); detail = []
for n, rs in sorted(byn.items()):
    cyc = [r for r in rs if r["cyclic"]]
    non = [r for r in rs if not r["cyclic"]]
    if not cyc or not non:
        continue
    c = cyc[0]["dbest"]; o = max(r["dbest"] for r in non)
    res = "cyclic higher" if c > o else ("tie" if c == o else "non-cyclic higher")
    tally[res] += 1
    detail.append((n, c, o, res))
print(dict(tally))
print([x for x in detail if x[3] != "tie"])
# how often is the column max attained by a cyclic group (when one exists)?
att = Counter()
for n, rs in byn.items():
    top = max(r["dbest"] for r in rs)
    att[("cyclic exists" if any(r["cyclic"] for r in rs) else "no cyclic group"),
        any(r["cyclic"] and r["dbest"] == top for r in rs)] += 1
print("column max attained by a cyclic group:", dict(att))

# (b) by type: mean of dbest/sqrt(n) residual vs column max, number of k's, max score
print("\n== (b) per group type: shortfall of best d below the column max, #k values, best score")
T = defaultdict(list)
for n, rs in byn.items():
    top = max(r["dbest"] for r in rs)
    for r in rs:
        T[typ(r)].append((top - r["dbest"], len(r["kset"]), r["smax"], n))
for t in sorted(T):
    v = T[t]
    print(f"{t:22s} groups={len(v):3d} mean shortfall={np.mean([x[0] for x in v]):.2f} "
          f"at-top={sum(x[0]==0 for x in v)/len(v):.0%} mean #k={np.mean([x[1] for x in v]):.2f} "
          f"mean best score={np.mean([x[2] for x in v]):.2f} max score={max(x[2] for x in v):.2f}")

# (c) score frontier: which group carries the best k d^2/n in each column; and the top 25 overall
print("\n== (c) best k d^2/n in each multi-group column: carried by")
c2 = Counter()
for n, rs in sorted(byn.items()):
    if len(rs) < 2:
        continue
    top = max(r["smax"] for r in rs)
    w = [r for r in rs if abs(r["smax"] - top) < 1e-9]
    c2[" / ".join(sorted(set(typ(r) for r in w)))] += 1
for k, v in c2.most_common():
    print(f"  {v:3d}  {k}")
print("\n== top 25 (group, k) cells by k d^2/n")
cells = [(k * d * d / r["n"], r["n"], k, d, r["g"], typ(r)) for r in rows for k, d in r["kd"].items()]
cells.sort(reverse=True)
for s, n, k, d, g, t in cells[:25]:
    print(f"  {s:6.2f} [[{n},{k},{d}]] G=Z{g[0]}xZ{g[1]}  {t}")
print("types among top 25:", Counter(c[5] for c in cells[:25]))
print("base rate of types among groups:", Counter(typ(r) for r in rows))

# (d) high-k, high-d: for each k >= 8, best d/sqrt(n) by type
print("\n== (d) for each k, best ratio d/sqrt(n) (n >= 100) by type [count of groups having that k]")
for k in sorted(set(k for r in rows for k in r["kd"])):
    if k < 8:
        continue
    by = defaultdict(list)
    for r in rows:
        if k in r["kd"] and r["n"] >= 100:
            by[typ(r)].append(r["kd"][k] / math.sqrt(r["n"]))
    print(f"k={k:2d}: " + "; ".join(f"{t}: {max(v):.3f} [{len(v)}]" for t, v in sorted(by.items())))

# (e) k = 12 entries in detail
print("\n== (e) k=12 cells, n>=120, sorted by score")
k12 = sorted([(12 * r["kd"][12] ** 2 / r["n"], r["n"], r["kd"][12], r["g"], typ(r)) for r in rows
              if 12 in r["kd"] and r["n"] >= 120], reverse=True)
for x in k12[:20]:
    print(f"  {x[0]:6.2f} n={x[1]} d={x[2]} Z{x[3][0]}xZ{x[3][1]} {x[4]}")
