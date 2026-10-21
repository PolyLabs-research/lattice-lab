import json
from collections import Counter
codes = set(); pairs = 0; dis = []; nonopt = []; ns = Counter(); ds = Counter(); toric = 0
agree = Counter(); k0 = 0
def chk(tag, ilp, ref):
    if ilp["status"] == "optimal":
        if ilp["d"] != ref: dis.append((tag, "ilp", ilp["d"], "ref", ref))
        return True
    nonopt.append((tag, ilp["status"], ilp.get("lower"), ilp.get("upper"), ref))
    if not ((ilp.get("lower") or 0) <= ref <= (ilp.get("upper") or 10**9)):
        dis.append((tag, "bounds", ilp.get("lower"), ilp.get("upper"), "ref", ref))
    return False
for f in ("cmpA.jsonl", "cmpB.jsonl"):
    for l in open(f):
        r = json.loads(l)
        n = 2 * r["l"] * r["m"]
        if r["k"] == 0:
            k0 += 1
            for kind in "ZX":
                if r[kind]["ilp"]["status"] != "no_logicals": dis.append((f, r["i"], kind, "k0", r[kind]["ilp"]["status"]))
            continue
        codes.add((f, r["i"])); ns[n] += 1
        for kind in "ZX":
            x = r[kind]; ref = x["dfs"]; tag = (f, r["i"], kind)
            pairs += 1; ds[ref] += 1
            if chk(tag, x["ilp"], ref): agree["ilp(trans)=dfs"] += 1
            for key in ("brute_theirs", "brute_mine"):
                if x.get(key) is not None:
                    if x[key] != ref: dis.append((tag, key, x[key], ref))
                    else: agree[key + "=dfs"] += 1
            if x.get("ilp_wit_mine") is False or x.get("ilp_wit_theirs") is False: dis.append((tag, "witness"))
            if x.get("brute_theirs_wit") is False: dis.append((tag, "brute witness"))
            if kind == "Z":
                nt = x["ilp_notrans"]
                if chk(tag + ("notrans",), {**nt, "lower": None, "upper": None}, ref) : agree["ilp(notrans)=dfs"] += 1
                s = x.get("scip_perlog_nosym")
                if isinstance(s, int):
                    if s != ref: dis.append((tag, "perlog", s, ref))
                    else: agree["my scip per-logical=dfs"] += 1
                h = x.get("highs")
                if isinstance(h, int):
                    if h != ref: dis.append((tag, "highs", h, ref))
                    else: agree["my highs=dfs"] += 1
        zx = (r["Z"]["ilp"], r["X"]["ilp"])
        if zx[0]["status"] == zx[1]["status"] == "optimal":
            agree["dX=dZ (ilp, both optimal)"] += zx[0]["d"] == zx[1]["d"]
            if zx[0]["d"] != zx[1]["d"]: dis.append((f, r["i"], "dX!=dZ"))
        if r["Z"]["dfs"] == r["X"]["dfs"]: agree["dX=dZ (dfs)"] += 1
        else: dis.append((f, r["i"], "dfs dX!=dZ"))
large = [json.loads(l) for l in open("large.jsonl")]
for r in large:
    tag = ("large", r["i"], r["kind"], "trans" if r["trans"] else "notrans")
    codes.add(("devcodes2.json-large", r["i"])); ns[2 * r["l"] * r["m"]] += 0
    ds[r["dfs"]] += 1
    if chk(tag, r["ilp"], r["dfs"]): agree["large ilp=dfs"] += 1
    if r.get("wit_mine") is False or r.get("wit_theirs") is False: dis.append((tag, "witness"))
for l in open("toric.jsonl"):
    r = json.loads(l); toric += 1
    if not r["ok"]: dis.append(("toric", r))
print("codes with k>0 (cmpA/cmpB/large):", len(codes), "k=0 codes:", k0, "toric sizes:", toric)
print("(code, kind) pairs in cmpA/cmpB:", pairs, "large rows:", len(large))
print("n:", sorted(set(ns)) + sorted({2 * r['l'] * r['m'] for r in large}))
print("reference distances:", dict(sorted(ds.items())))
print("agreements:", dict(agree))
print("non-optimal ILP ends (bounds checked):", nonopt)
print("DISAGREEMENTS:", len(dis))
for d in dis: print("  ", d)
