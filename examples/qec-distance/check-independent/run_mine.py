"""My exact methods on the development codes; results to mine.jsonl."""
import json, sys, time
import mydist as M

codes = json.load(open(sys.argv[1]))
out = open(sys.argv[2], "a")
lim = float(sys.argv[3]) if len(sys.argv) > 3 else 120
for ci, c in enumerate(codes):
    ell, m, A, B = c["l"], c["m"], c["A"], c["B"]
    M.guard(A, B, ell, m)
    rec = {"i": ci, **c}
    for kind in "ZX":
        Hc, Hs = M.pair(kind, A, B, ell, m)
        if c["k"] == 0:
            rec[kind] = {"note": "k=0", "reps": len(M.logical_reps(Hc, Hs))}
            continue
        r = {}
        D = M.kernel(Hc).shape[0]
        if D <= 27:
            t = time.time(); r["brute"] = M.distance_brute(Hc, Hs); r["t_brute"] = time.time() - t
        t = time.time()
        v, wit, nodes, comp = M.distance_dfs(Hc, Hs, Hc.shape[1] + 1, time_limit=lim)
        r["dfs"] = v if comp else None; r["dfs_ub"] = v; r["t_dfs"] = time.time() - t; r["dfs_nodes"] = nodes
        if wit is not None:
            import numpy as np
            x = np.zeros(Hc.shape[1], dtype=np.uint8); x[wit] = 1
            r["dfs_wit_ok"] = bool(M.nontrivial(x, Hc, Hs)) and int(x.sum()) == v
        if kind == "Z" or Hc.shape[1] <= 120:
            t = time.time(); h = M.distance_highs(Hc, Hs, time_limit=lim); r["highs"] = h[0]; r["t_highs"] = time.time() - t
        rec[kind] = r
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(ci, ell, m, c["form"], "k", c["k"], {k: (rec[k].get("brute"), rec[k].get("dfs"), rec[k].get("dfs_ub"), rec[k].get("highs")) for k in "ZX" if "note" not in rec[k]}, flush=True)
