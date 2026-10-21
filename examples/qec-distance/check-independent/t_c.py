import json, time
import mydist as M
codes = json.load(open("devcodes.json"))
mine = {json.loads(l)["i"]: json.loads(l) for l in open("mine.jsonl")}
bad = 0
for i, c in enumerate(codes[:72]):
    if c["k"] == 0: continue
    for kind in "ZX":
        Hc, Hs = M.pair(kind, c["A"], c["B"], c["l"], c["m"])
        t = time.time()
        v, w, nd = M.dfs_c(Hc, Hs, min(64, Hc.shape[1] + 1))
        ref = mine[i][kind]["dfs_ub"]
        if v != ref: bad += 1; print("DIFF", i, kind, v, ref)
print("bad", bad)
# toric timing
for ell, m in [(8, 8), (10, 10), (12, 12), (9, 16)]:
    A, B = M.toric(ell, m)
    Hc, Hs = M.pair("Z", A, B, ell, m)
    t = time.time(); v, w, nd = M.dfs_c(Hc, Hs, min(ell, m) + 1); print("toric", ell, m, v, nd, f"{time.time()-t:.2f}s")
    t = time.time(); v, w, nd = M.dfs_c(Hc, Hs, min(ell, m)); print("  prove >=", min(ell, m), v, nd, f"{time.time()-t:.2f}s")
# the hard ones from before, now with ub = known d
for i in [49, 56, 65]:
    c = codes[i]
    Hc, Hs = M.pair("Z", c["A"], c["B"], c["l"], c["m"])
    t = time.time(); v, w, nd = M.dfs_c(Hc, Hs, 64); print(i, "free", v, nd, f"{time.time()-t:.2f}s")
