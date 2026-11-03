"""Data for the census explorer (census-explorer.html): every (torus, k) frontier entry of the
weight-6 census, stages 3a to 4, with the best connected code's A and B, plus the published codes.

    python examples/qec-census-4/explorer/build_data.py > examples/qec-census-4/explorer/data.json
"""

import glob
import json
import math
from pathlib import Path

EX = Path(__file__).resolve().parents[2]
S3D = {(3, 45), (5, 27), (2, 69), (3, 46), (6, 23), (3, 47), (2, 72), (4, 36), (3, 49)}


def poly(P):
    return [list(t) for t in P]


def entries():
    out = []
    # stage 3a: every class's d on the stage-1 tori
    for p in sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl"))):
        lines = [json.loads(x) for x in open(p) if x.strip()]
        head, best = lines[0], {}
        for r in lines[1:]:
            if r.get("connected") and r["status"] == "complete":
                if r["k"] not in best or r["d"] > best[r["k"]]["d"]:
                    best[r["k"]] = r
        for k, r in best.items():
            out.append({"l": head["l"], "m": head["m"], "n": head["n"], "k": k, "d": r["d"],
                        "A": poly(r["A"]), "B": poly(r["B"]), "stage": "3a", "settled": True})
    # stages 3b/3c (with 3d) and 4: the frontier records
    for folder, stage in (("qec-census-3b", "3b/3c"), ("qec-census-3c", "3b/3c"),
                          ("qec-census-4", "4")):
        f = EX / folder / "records.jsonl"
        if not f.exists():
            continue
        for x in open(f):
            r = json.loads(x)
            if r.get("job") != "torus" or "error" in r or not r.get("classes"):
                continue
            for ks, v in r["best"]["connected"].items():
                k, d = int(ks), v["d"]
                settled = v["settled"]
                if (r["l"], r["m"]) in S3D and not settled:
                    d, settled = 24, True  # stage 3d
                if d is None:
                    continue
                row = next((y for y in r["rows"] if y["connected"] and y["k"] == k
                            and (y.get("exact") or {}).get("status") == "complete"
                            and y["exact"]["d"] == d), None)
                out.append({"l": r["l"], "m": r["m"], "n": r["n"], "k": k, "d": d,
                            "A": poly(row["A"]) if row else None,
                            "B": poly(row["B"]) if row else None,
                            "stage": stage, "settled": settled,
                            "group": r.get("group")})
    for e in out:
        e["score"] = round(e["k"] * e["d"] ** 2 / e["n"], 4)
        e["ratio"] = round(e["d"] / math.sqrt(e["n"]), 4)
    return out


def published():
    codes = json.loads((EX / "qec-bb" / "codes.json").read_text())["codes"]
    out = []
    for c in codes:
        n, k, d = c.get("n"), c.get("k"), c.get("d")
        if n and k and d:
            out.append({"name": c["name"], "n": n, "k": k, "d": d,
                        "score": round(k * d * d / n, 4), "ratio": round(d / math.sqrt(n), 4)})
    # beyond codes.json: the open-distance codes, with their best known d
    out += [{"name": "[[360,12,24]] (Bravyi et al.; d = 24 shown here)", "n": 360, "k": 12,
             "d": 24, "score": 19.2, "ratio": round(24 / math.sqrt(360), 4)}]
    return out


if __name__ == "__main__":
    e = entries()
    print(json.dumps({"entries": e, "published": published(),
                      "laws": {"p2": 1.40, "env_c": 0.8011, "env_b": 0.6074,
                               "s3b_record": 13.5, "s4_record": 13.6054, "s4_ceiling": 17.0}},
                     separators=(",", ":")))
