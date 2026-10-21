import json, time
import mydist as M
codes = json.load(open("devcodes2.json"))
for i, c in enumerate(codes):
    if i < 30: continue
    Hc, Hs = M.pair("Z", c["A"], c["B"], c["l"], c["m"])
    t = time.time()
    v, w, nd = M.dfs_c(Hc, Hs, 64, procs=1, timeout=900)
    print(i, c["l"], c["m"], c["form"], "k", c["k"], "dZ", v, "nodes", nd, f"{time.time()-t:.1f}s", flush=True)
