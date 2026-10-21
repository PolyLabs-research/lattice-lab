"""One job: builder's distance_ilp on one dev code (kind, translation), plus my C search."""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
import mydist as M
spec = json.loads(sys.argv[1])
codes = json.load(open(spec["file"]))
c = codes[spec["i"]]
A, B, ell, m = c["A"], c["B"], c["l"], c["m"]
M.guard(A, B, ell, m)
kind, n = spec["kind"], 2 * ell * m
Hc, Hs = M.pair(kind, A, B, ell, m)
t = time.time()
v, w, nd = M.dfs_c(Hc, Hs, 64, procs=1, timeout=900)
out = {**spec, "l": ell, "m": m, "k": c["k"], "form": c["form"], "dfs": v, "dfs_nodes": nd,
       "t_dfs": round(time.time() - t, 1)}
r = D.distance_ilp(A, B, ell, m, kind, time_limit=spec["limit"], translation=spec["trans"])
out["ilp"] = {k: r[k] for k in ("status", "d", "lower", "upper", "dual_bound", "nodes", "seconds")}
if r["witness"]:
    x = np.zeros(n, dtype=np.uint8); x[r["witness"]] = 1
    out["wit_mine"] = bool(M.nontrivial(x, Hc, Hs))
    out["wit_theirs"] = D.verify_witness(A, B, ell, m, kind, r["witness"])["logical"]
print(json.dumps(out))
