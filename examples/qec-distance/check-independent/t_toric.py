import time, sys
import mydist as M
for ell, m in [(6, 7), (7, 7), (8, 8), (9, 10)]:
    A, B = M.toric(ell, m)
    for kind in "Z":
        Hc, Hs = M.pair(kind, A, B, ell, m)
        t = time.time(); dd = M.distance_dfs(Hc, Hs, 2*ell*m+1, time_limit=300); t1 = time.time()-t
        t = time.time(); dh = M.distance_highs(Hc, Hs, time_limit=300); t2 = time.time()-t
        t = time.time(); ds = M.distance_scip(Hc, Hs, time_limit=300); t3 = time.time()-t
        print(ell, m, kind, "dfs", dd[0], dd[2], dd[3], f"{t1:.1f}s", "highs", dh[0], f"{t2:.1f}s", "scip", ds[0], f"{t3:.1f}s", "expect", min(ell, m), flush=True)
