"""Translation-anchored search (anchors 0 and lm only) vs the full search, on dev codes."""
import json, time
import mydist as M
codes = json.load(open("devcodes2.json"))
known = {42: 14, 43: 12, 47: 14, 49: 14, 60: 16, 64: 18, 61: 14}
for i, d in known.items():
    c = codes[i]
    lm = c["l"] * c["m"]
    Hc, Hs = M.pair("Z", c["A"], c["B"], c["l"], c["m"])
    t = time.time()
    v, w, nd = M.dfs_anchors(Hc, Hs, 64, [(0, 1), (lm, lm + 1)])
    t1 = time.time() - t
    t = time.time()
    v2, _, nd2 = M.dfs_anchors(Hc, Hs, d, [(0, 1), (lm, lm + 1)])  # prove no weight < d
    print(i, c["l"], c["m"], "d", d, "anchored free:", v, nd, f"{t1:.1f}s", "| prove >= d:", v2, nd2, f"{time.time()-t:.1f}s", flush=True)
