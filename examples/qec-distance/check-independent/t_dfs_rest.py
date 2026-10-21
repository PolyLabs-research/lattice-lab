import json, time
import mydist as M
codes = json.load(open("devcodes2.json"))
for i in range(64, len(codes)):
    c = codes[i]
    Hc, Hs = M.pair("Z", c["A"], c["B"], c["l"], c["m"])
    t = time.time()
    try:
        v, w, nd = M.dfs_c(Hc, Hs, 64, procs=1, timeout=240)
    except Exception as e:
        print(i, c["l"], c["m"], "timeout", flush=True); continue
    print(i, c["l"], c["m"], c["form"], "k", c["k"], "dZ", v, "nodes", nd, f"{time.time()-t:.1f}s", flush=True)
