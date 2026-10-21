"""Cross-check the builder's distance_ilp / distance_brute against my methods on dev codes."""
import json, sys, time
from pathlib import Path
import numpy as np
import mydist as M
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D

codes = json.load(open(sys.argv[1]))
outp = sys.argv[2]
LIM = float(sys.argv[3]) if len(sys.argv) > 3 else 300
start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
HIGHS_N = int(sys.argv[5]) if len(sys.argv) > 5 else 100
PERLOG_N = int(sys.argv[6]) if len(sys.argv) > 6 else 1000
END = int(sys.argv[7]) if len(sys.argv) > 7 else 10**9
done = set()
if Path(outp).exists():
    done = {json.loads(l)["i"] for l in open(outp)}
out = open(outp, "a")
for ci, c in enumerate(codes):
    if ci < start or ci in done or ci >= END:
        continue
    ell, m, A, B = c["l"], c["m"], c["A"], c["B"]
    M.guard(A, B, ell, m)
    n = 2 * ell * m
    rec = {"i": ci, **c}
    for kind in "ZX":
        Hc, Hs = M.pair(kind, A, B, ell, m)
        r = {}
        # builder
        t = time.time()
        z = D.distance_ilp(A, B, ell, m, kind, time_limit=LIM)
        r["ilp"] = {k: z[k] for k in ("status", "d", "lower", "upper", "nodes", "seconds", "k")}
        if z["witness"] is not None:
            x = np.zeros(n, dtype=np.uint8); x[z["witness"]] = 1
            r["ilp_wit_mine"] = bool(M.nontrivial(x, Hc, Hs))
            r["ilp_wit_theirs"] = D.verify_witness(A, B, ell, m, kind, z["witness"])["logical"]
            r["ilp_wit_has_origin"] = bool(x[0] or x[ell * m])
        if c["k"] == 0:
            rec[kind] = r
            continue
        dim = M.kernel(Hc).shape[0]
        r["dim"] = dim
        if dim <= 28:
            b = D.distance_brute(A, B, ell, m, kind)
            r["brute_theirs"] = b["d"]
            if b["witness"]:
                x = np.zeros(n, dtype=np.uint8); x[b["witness"]] = 1
                r["brute_theirs_wit"] = bool(M.nontrivial(x, Hc, Hs)) and len(b["witness"]) == b["d"]
        if dim <= 27:
            r["brute_mine"] = M.distance_brute(Hc, Hs)
        t = time.time()
        try:
            v, w, nd = M.dfs_c(Hc, Hs, min(64, n + 1), procs=1, timeout=LIM * 3)
            r["dfs"] = v if v <= n else None; r["dfs_nodes"] = nd
        except Exception as e:
            r["dfs"] = None; r["dfs_err"] = repr(e)
        r["t_dfs"] = round(time.time() - t, 2)
        if kind == "Z":
            nt = D.distance_ilp(A, B, ell, m, kind, time_limit=LIM, translation=False)
            r["ilp_notrans"] = {k: nt[k] for k in ("status", "d", "nodes", "seconds")}
            t = time.time()
            s = M.distance_scip(Hc, Hs, time_limit=LIM, symmetry=False) if n <= PERLOG_N else (None, "skipped")
            r["scip_perlog_nosym"] = s[0] if not isinstance(s[1], str) else s[1]
            r["t_scip_perlog"] = round(time.time() - t, 2)
            if n <= HIGHS_N:
                t = time.time()
                h = M.distance_highs(Hc, Hs, time_limit=min(LIM, 120))
                r["highs"] = h[0] if not isinstance(h[1], str) else h[1]
                r["t_highs"] = round(time.time() - t, 2)
        rec[kind] = r
    out.write(json.dumps(rec) + "\n"); out.flush()
    zz, xx = rec["Z"], rec["X"]
    print(ci, ell, m, c["form"], "k", c["k"], "Z", zz["ilp"]["status"], zz["ilp"]["d"], zz.get("dfs"),
          zz.get("brute_theirs"), zz.get("brute_mine"), zz.get("ilp_notrans", {}).get("d"), zz.get("scip_perlog_nosym"), zz.get("highs"),
          "| X", xx["ilp"]["status"], xx["ilp"]["d"], xx.get("dfs"), xx.get("brute_theirs"), xx.get("brute_mine"),
          f"t={zz['ilp']['seconds']:.1f}/{xx['ilp']['seconds']:.1f}/{zz.get('t_dfs')}", flush=True)
