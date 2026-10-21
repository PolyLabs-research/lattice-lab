"""Translation-anchored search (anchors 0, lm) vs the recorded full search, both kinds."""
import json, sys, time
import mydist as M
recs = {}
for f, src in (("cmpA.jsonl", "devcodes.json"), ("cmpB.jsonl", "devcodes2.json")):
    for l in open(f):
        r = json.loads(l)
        if r["k"]:
            for kind in "ZX":
                if r[kind].get("dfs") is not None:
                    recs[(src, r["i"], kind)] = (r, r[kind]["dfs"])
for l in open("large.jsonl"):
    r = json.loads(l)
    if "dfs" in r:
        c = json.load(open(r["file"]))[r["i"]]
        recs.setdefault((r["file"], r["i"], r["kind"]), ({**c, "i": r["i"]}, r["dfs"]))
tot = bad = 0
t0 = time.time()
for (src, i, kind), (r, full) in sorted(recs.items()):
    lm = r["l"] * r["m"]
    Hc, Hs = M.pair(kind, r["A"], r["B"], r["l"], r["m"])
    anch = M.dfs_anchors(Hc, Hs, min(64, 2 * lm + 1), [(0, 1), (lm, lm + 1)], timeout=600)[0]
    tot += 1
    if anch != full:
        bad += 1
        print("DIFF", src, i, kind, full, anch, flush=True)
print("pairs", tot, "differences", bad, f"{time.time()-t0:.0f}s", flush=True)
