"""k banding: k/2 as a sum of admissible Frobenius-orbit sizes; dedup k counts; pending groups."""
from common import *
from orbits import orbit_profile
import numpy as np

rows = json.load(open("groups.json"))
for r in rows:
    r["kd"] = {int(k): v for k, v in r["kd"].items()}; r["g"] = tuple(r["g"])

print("k counts, all entries:", sorted(Counter(e["k"] for e in ENTRIES).items()))
print("k counts, dedup by group:", sorted(Counter(k for r in rows for k in r["kd"]).items()))

def subset_sums(sizes):
    s = {0}
    for x in sizes:
        s |= {a + x for a in s}
    return s

ok = bad = 0; badl = []
for r in rows:
    prof = orbit_profile(r["g"])
    sizes = [sz for t, (no, sz) in prof.items() for _ in range(no)]
    if r["r2"] <= 1:
        S = subset_sums(sizes)
        for k in r["kd"]:
            if k // 2 in S: ok += 1
            else: bad += 1; badl.append((r["g"], k, prof))
print(f"r2<=1 groups: frontier k with k/2 = a sum of distinct admissible orbit sizes: {ok} ok, {bad} not; {badl[:5]}")
# what fraction of possible sums are realised on the frontier?
real = poss = 0
for r in rows:
    if r["r2"] <= 1:
        prof = orbit_profile(r["g"])
        sizes = [sz for t, (no, sz) in prof.items() for _ in range(no)]
        S = {2 * s for s in subset_sums(sizes) if s > 0 and 2 * s <= 8 * r["N"] // 9}
        poss += len(S); real += len(set(r["kd"]) & S)
print(f"   possible k values (sums, <= 8N/9) realised by a connected frontier code: {real} of {poss}")

# r2 = 2 groups: terms up to 2^(s+t)
print("\nr2=2 groups: frontier k and orbit profile")
for r in rows:
    if r["r2"] == 2:
        print(f"  Z{r['g'][0]}xZ{r['g'][1]} n={r['n']} kd={dict(sorted(r['kd'].items()))} orbits={orbit_profile(r['g'])}")

# pending (uncomputed) groups with codes, n <= 400
R = torus_records()
computed_groups = {group_key(*t) for t, v in R.items()}
universe = [(l, m) for l in range(2, 201) for m in range(l, 201) if l * m <= 200]
pending = defaultdict(list)
for t in universe:
    g = group_key(*t)
    if criterion_e(*t) and g not in computed_groups:
        pending[g].append(t)
print("\npending groups with codes (not computed on any isomorphic torus):")
for g, ts in sorted(pending.items(), key=lambda x: x[0][0] * x[0][1]):
    pp = pparts(*g)
    r2 = sum(1 for x in pp.get(2, (0, 0)) if x > 0)
    ranks = {p: sum(1 for x in v if x > 0) for p, v in pp.items()}
    print(f"  n={2*g[0]*g[1]} Z{g[0]}xZ{g[1]} tori={ts} ranks={ranks} orbits={orbit_profile(g)}")
# r2=2 & r3=2 groups of order <= 200
print("\nall groups of order <= 200 with r2 = 2 and r3 = 2:",
      sorted({group_key(l, m) for l, m in universe if l % 6 == 0 and m % 6 == 0}))
print("k=12 on those (computed):", {tuple(r['g']): r['kd'].get(12) for r in rows if r['r2'] == 2 and r['r3'] == 2},
      " column tops:", {tuple(r['g']): max(x['dbest'] for x in rows if x['n'] == r['n']) for r in rows if r['r2'] == 2 and r['r3'] == 2})
