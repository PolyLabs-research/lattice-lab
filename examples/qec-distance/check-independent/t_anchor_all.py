"""Translation-anchored LP-free search (anchors 0, lm) vs full search (all anchors), both kinds."""
import json, time
import mydist as M
tot = bad = 0
for f in ("devcodes.json", "devcodes2.json"):
    for i, c in enumerate(json.load(open(f))):
        if c["k"] == 0 or (f == "devcodes2.json" and i in (44, 60, 63, 64, 65)):
            continue
        lm = c["l"] * c["m"]
        for kind in "ZX":
            Hc, Hs = M.pair(kind, c["A"], c["B"], c["l"], c["m"])
            ub = min(64, 2 * lm + 1)
            full = M.dfs_c(Hc, Hs, ub)[0]
            anch = M.dfs_anchors(Hc, Hs, ub, [(0, 1), (lm, lm + 1)])[0]
            tot += 1
            if full != anch:
                bad += 1
                print("DIFF", f, i, kind, full, anch, flush=True)
print("pairs", tot, "differences", bad)
