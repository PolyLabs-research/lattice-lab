"""Same-order pairwise comparisons by structural feature; orbit count vs #k and top."""
from common import *
from orbits import orbit_profile
from scipy.stats import spearmanr
import numpy as np

rows = json.load(open("groups.json"))
for r in rows:
    r["kd"] = {int(k): v for k, v in r["kd"].items()}; r["g"] = tuple(r["g"])
byn = defaultdict(list)
for r in rows:
    byn[r["n"]].append(r)

def cmp(feature_name, sel):
    t = Counter(); ex = []
    for n, rs in byn.items():
        cyc = [r for r in rs if r["cyclic"]]
        for r in rs:
            if not r["cyclic"] and sel(r) and cyc:
                c = cyc[0]
                res = "lower" if r["dbest"] < c["dbest"] else ("tie" if r["dbest"] == c["dbest"] else "higher")
                t[res] += 1
                if res != "tie": ex.append((n, f"Z{r['g'][0]}xZ{r['g'][1]}", r["dbest"], c["dbest"]))
    print(f"{feature_name:28s} vs cyclic group of same order (top d): {dict(t)}  {sorted(ex)}")

cmp("r2 = 2 (two even sides)", lambda r: r["r2"] == 2)
cmp("r3 = 2 (Z3 x Z3 inside)", lambda r: r["r3"] == 2)
cmp("other non-cyclic", lambda r: r["r2"] < 2 and r["r3"] < 2)

# orbit counts
na, nk, sh, sm = [], [], [], []
for n, rs in byn.items():
    top = max(r["dbest"] for r in rs)
    for r in rs:
        prof = orbit_profile(r["g"])
        na.append(sum(no for no, sz in prof.values())); nk.append(len(r["kset"]))
        sh.append(top - r["dbest"]); sm.append(r["smax"])
print("\nSpearman(#admissible orbits, #frontier k) = %.2f (p=%.1e)" % spearmanr(na, nk))
print("Spearman(#admissible orbits, shortfall of top below column max) = %.2f (p=%.2f)" % spearmanr(na, sh))
print("Spearman(#admissible orbits, best k d^2/n) = %.2f (p=%.2f)" % spearmanr(na, sm))
