"""Independent loader (verify-structure-3): class-level rows from every census stage."""
import json, math, glob, os, pickle
from collections import defaultdict

EX = "/home/user/lattice-lab/examples"
OUT = os.path.dirname(os.path.abspath(__file__))


def gkey(l, m):
    g = math.gcd(l, m)
    return (g, l * m // g)


def load_tori():
    """torus (l,m) -> dict(stage, rows=[(k, connected, d_exact_or_None, upper_or_None)])."""
    T = {}
    # stage 3a: one jsonl per torus, header + class rows (every class exact)
    for f in sorted(glob.glob(f"{EX}/qec-census-3/data/*.jsonl")):
        lines = [json.loads(x) for x in open(f)]
        h = lines[0]
        rows = []
        for r in lines[1:]:
            rows.append(dict(A=r["A"], B=r["B"], k=r["k"], conn=r["connected"], d=r["d"] if r.get("status") == "complete" else None,
                             lower=r.get("lower"), upper=r["d"], size=r.get("size")))
        T[(h["l"], h["m"])] = dict(stage="3a", rows=rows, n=h["n"])
    # stage 3b / 3c / 4 records
    for st, f in (("3b", "qec-census-3b/records.jsonl"), ("3c", "qec-census-3c/records.jsonl"),
                  ("4", "qec-census-4/records.jsonl")):
        for line in open(f"{EX}/{f}"):
            r = json.loads(line)
            if r.get("job") != "torus":
                continue
            rows = []
            for c in r["rows"]:
                ex = c.get("exact")
                d = ex["d"] if ex and ex.get("status", "complete") == "complete" and ex.get("d") is not None else None
                rows.append(dict(A=c["A"], B=c["B"], k=c["k"], conn=c["connected"], d=d, lower=(ex or {}).get("lower"),
                                 upper=c.get("upper"), size=None))
            key = (r["l"], r["m"])
            if key in T:
                print("dup torus", key, T[key]["stage"], st)
            T[key] = dict(stage=st, rows=rows, n=r["n"], best=r["best"], group=r.get("group"))
    # stage 3d: DistQLDPC reruns of classes left incomplete on 9 tori
    hit = 0
    for line in open(f"{EX}/qec-census-3d/records.jsonl"):
        r = json.loads(line)
        cl, dq = r["class"], r["distqldpc"]
        t = T[tuple(cl["torus"])]
        for row in t["rows"]:
            if row["A"] == cl["A"] and row["B"] == cl["B"] and row["k"] == cl["k"]:
                if dq.get("d") is not None and r["witness_check"].get("weight") == dq["d"]:
                    row["d"] = dq["d"]; row["src3d"] = True; hit += 1
                break
        else:
            print("3d class not found", cl["torus"], cl["A"], cl["B"])
    print("stage 3d classes merged:", hit)
    return T


if __name__ == "__main__":
    T = load_tori()
    print(len(T), "tori;", sum(len(v["rows"]) for v in T.values()), "class rows")
    pickle.dump(T, open(f"{OUT}/tori.pkl", "wb"))
