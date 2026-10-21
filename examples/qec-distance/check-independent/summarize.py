import json, sys
from collections import Counter
rows = []
for f in sys.argv[1:]:
    rows += [(f, json.loads(l)) for l in open(f)]
stats = Counter(); dis = []; ns = set(); ds = Counter(); toric = 0
for f, r in rows:
    n = 2 * r["l"] * r["m"]
    for kind in "ZX":
        x = r[kind]
        ilp = x["ilp"]
        if r["k"] == 0:
            stats["k0 " + ilp["status"]] += 1
            continue
        stats["kinds"] += 1
        ns.add(n)
        ref = x.get("dfs")
        vals = {"ilp": ilp["d"] if ilp["status"] == "optimal" else None, "dfs": ref,
                "brute_theirs": x.get("brute_theirs"), "brute_mine": x.get("brute_mine")}
        if kind == "Z":
            vals["ilp_notrans"] = x["ilp_notrans"]["d"] if x["ilp_notrans"]["status"] == "optimal" else None
            vals["scip_perlog"] = x.get("scip_perlog_nosym") if isinstance(x.get("scip_perlog_nosym"), int) else None
            vals["highs"] = x.get("highs") if isinstance(x.get("highs"), int) else None
        present = {k: v for k, v in vals.items() if v is not None}
        if ilp["status"] != "optimal":
            stats["ilp not optimal"] += 1
            dis.append((f, r["i"], kind, "ilp status", ilp))
        if len(set(present.values())) > 1:
            dis.append((f, r["i"], kind, present))
        for k in present:
            stats["have " + k] += 1
        if x.get("ilp_wit_mine") is False or x.get("ilp_wit_theirs") is False:
            dis.append((f, r["i"], kind, "witness", x.get("ilp_wit_mine"), x.get("ilp_wit_theirs")))
        if x.get("brute_theirs_wit") is False:
            dis.append((f, r["i"], kind, "brute witness"))
        if ref is not None:
            ds[ref] += 1
    if r["k"]:
        zx = (r["Z"]["ilp"]["d"], r["X"]["ilp"]["d"])
        if zx[0] != zx[1]:
            dis.append((f, r["i"], "dX != dZ", zx))
        stats["codes k>0"] += 1
print(dict(stats))
print("n values", sorted(ns))
print("dfs distances", dict(sorted(ds.items())))
print("disagreements", len(dis))
for d in dis: print(d)
