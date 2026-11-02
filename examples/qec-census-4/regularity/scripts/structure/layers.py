"""Staircase of column tops, single-orbit envelope, k layers, tall columns (21 | N)."""
from common import *
from orbits import orbit_profile
import numpy as np

rows = json.load(open("groups.json"))
for r in rows:
    r["kd"] = {int(k): v for k, v in r["kd"].items()}; r["g"] = tuple(r["g"])
byn = defaultdict(list)
for r in rows:
    byn[r["n"]].append(r)
top = {n: max(r["dbest"] for r in rs) for n, rs in byn.items()}

# 1. staircase on the 6-comb
comb = sorted(n for n in top if (n // 2) % 3 == 0)
print("== staircase on n = 0 mod 6 (column top d):")
seq = [(n, top[n]) for n in comb]
print(seq)
dips = [(seq[i][0], seq[i - 1][1], seq[i][1]) for i in range(1, len(seq)) if seq[i][1] < seq[i - 1][1]]
print("non-monotone steps:", dips)
first = {}
for n, d in seq:
    if d not in first and all(d > x for m, x in seq if m < n):
        first[d] = n
print("first n reaching each d (step positions):", first)
plateau = Counter(d for n, d in seq)
print("columns per plateau:", sorted(plateau.items()))
print("n_d / d^2:", {d: round(n / d / d, 3) for d, n in first.items()})
# missing comb points (no data yet)
allcomb = [n for n in range(12, 401, 6)]
print("comb points with no data (stage 4 pending):", [n for n in allcomb if n not in top])

# 2. other columns vs the staircase: shortfall below the comb envelope at that n
def comb_env(n):
    lo = max((m for m in comb if m <= n), default=None)
    hi = min((m for m in comb if m >= n), default=None)
    return lo, hi, top.get(lo), top.get(hi)
print("\n== non-comb columns: top d vs neighbouring comb tops (k_min, orbit size)")
short = defaultdict(list)
for n in sorted(top):
    if (n // 2) % 3 == 0:
        continue
    lo, hi, a, b = comb_env(n)
    km = min(min(r["kd"]) for r in byn[n])
    env = max(x for x in (a, b) if x is not None)
    envmin = min(x for x in (a, b) if x is not None)
    short[km].append((n, top[n], a, b))
    print(f"n={n:3d} k_min={km:2d} top={top[n]:2d}  comb neighbours {lo}:{a} {hi}:{b}  shortfall vs lower neighbour {a - top[n] if a else None}")
for km, v in sorted(short.items()):
    sf = [a - t for n, t, a, b in v if a is not None]
    print(f"k_min={km}: columns {len(v)}, shortfall vs lower comb neighbour: mean {np.mean(sf):.2f}, values {sf}")

# 3. layers: d_k / d_kmin within a group, by k, as function of n
print("\n== layers: d(k) / d(k_min) within groups (3|N groups, k_min = 4)")
lay = defaultdict(list)
for r in rows:
    if min(r["kd"]) != 4:
        continue
    for k, d in r["kd"].items():
        if k > 4:
            lay[k].append((r["n"], d / r["kd"][4], d, r["kd"][4]))
for k in sorted(lay):
    v = lay[k]
    big = [x[1] for x in v if x[0] >= 150]
    print(f"k={k:2d}: groups {len(v):3d}  mean ratio {np.mean([x[1] for x in v]):.3f} "
          f"(n>=150: {np.mean(big) if big else float('nan'):.3f}, sd {np.std(big) if big else float('nan'):.3f}, n={len(big)})  "
          f"sqrt(4/k)={math.sqrt(4/k):.3f}")
# k=8 by mechanism
print("\n== k=8 layer by mechanism (3|N groups)")
mech = defaultdict(list)
for r in rows:
    if 8 in r["kd"] and 4 in r["kd"]:
        prof = orbit_profile(r["g"])
        m = []
        if 15 in prof: m.append("15-orbit")
        if prof.get(3, (0, 0))[0] >= 4: m.append("two 3-orbits")
        if r["r2"] == 2: m.append("term 2 (r2=2)")
        mech[" + ".join(m) or "?"].append((r["n"], r["kd"][8] / r["kd"][4]))
for m, v in mech.items():
    print(f"  {m:40s} groups {len(v):2d}  mean d8/d4 {np.mean([x[1] for x in v]):.3f}  {v[:8]}")

# 4. tall columns: dedup points per column by class
print("\n== dedup points per column by class")
cls = defaultdict(list)
for n, rs in byn.items():
    N = n // 2
    c = "21|N" if N % 21 == 0 else ("15|N" if N % 15 == 0 else ("3|N other" if N % 3 == 0 else ("7|N" if N % 7 == 0 else "31/73/85")))
    cls[c].append((n, sum(len(r["kset"]) for r in rs), len(rs)))
for c, v in cls.items():
    print(f"{c:10s} columns {len(v):2d}  mean points {np.mean([x[1] for x in v]):.2f}  "
          f"single-point columns {sum(x[1]==1 for x in v)}  {[(n, p) for n, p, g in sorted(v)]}")
