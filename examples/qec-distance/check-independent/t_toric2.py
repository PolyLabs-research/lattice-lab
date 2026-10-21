import sys, time, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
import mydist as M
T = [(0, 0), (1, 0)], [(0, 0), (0, 1)]
out = open("toric.jsonl", "w")
for ell, m in [(1, 7), (2, 7), (4, 4), (3, 9), (5, 6), (6, 7), (7, 7), (4, 11), (7, 12), (9, 11), (10, 10), (8, 13), (11, 11), (6, 20)]:
    rec = {"l": ell, "m": m}
    for kind in "ZX":
        Hc, Hs = M.pair(kind, *T, ell, m)
        r = D.distance_ilp(*T, ell, m, kind, time_limit=300)
        x = np.zeros(2 * ell * m, dtype=np.uint8); x[r["witness"]] = 1
        v, w, nd = M.dfs_c(Hc, Hs, min(ell, m) + 1)
        rec[kind] = [r["status"], r["d"], bool(M.nontrivial(x, Hc, Hs)), v, round(r["seconds"], 1)]
    ok = rec["Z"][1] == rec["X"][1] == rec["Z"][3] == rec["X"][3] == min(ell, m) and rec["Z"][2] and rec["X"][2]
    rec["ok"] = ok
    print(rec, flush=True); out.write(json.dumps(rec) + "\n")
