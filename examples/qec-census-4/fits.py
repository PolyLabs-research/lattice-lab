"""
The laws stage 4 registers, fitted to stages 3a-3d (every weight-6 code on every torus with
n <= 300, exact distances; stage 3d's d = 24 on the 9 formerly incomplete tori).

    python examples/qec-census-4/fits.py

Per torus: d_max (the best connected d over k) and s_max (the best k d^2 / n over connected
classes). Fits, over the tori with codes and n >= 60:
- the growth exponent b: least squares of log(max d_max at each n) on log n;
- the envelope constant c: the largest d_max / n^b over the tori, so every torus has
  d_max <= c n^b;
- the score trend: the largest s_max in each band of 50 in n, and a line through the band maxima.
"""

from __future__ import annotations

import glob
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

EX = Path(__file__).resolve().parent.parent
S3D = [(3, 45), (5, 27), (2, 69), (3, 46), (6, 23), (3, 47), (2, 72), (4, 36), (3, 49)]


def tori() -> dict[tuple[int, int], dict]:
    """(l, m) -> {n, group, best: {k: d}} from stage 3a's data and stage 3b/3c's records, with
    stage 3d's results."""
    out = {}
    for p in sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl"))):
        lines = [json.loads(x) for x in open(p) if x.strip()]
        head, best = lines[0], {}
        for r in lines[1:]:
            if r.get("connected") and r["status"] == "complete":
                best[r["k"]] = max(best.get(r["k"], 0), r["d"])
        out[(head["l"], head["m"])] = {"n": head["n"], "group": "stage1", "best": best}
    for f in ("qec-census-3b", "qec-census-3c"):
        for x in open(EX / f / "records.jsonl"):
            r = json.loads(x)
            if r.get("job") != "torus" or "error" in r:
                continue
            best = {int(k): v["d"] for k, v in r["best"]["connected"].items() if v["d"] is not None}
            out[(r["l"], r["m"])] = {"n": r["n"], "group": r["group"], "best": best}
    for t in S3D:  # stage 3d: the unsettled entries are 24
        b = out[t]["best"]
        b[4] = 24
        if t == (3, 49):
            b[6] = 24
    return out


def fit() -> dict:
    rows = []
    for t, v in tori().items():
        if v["best"]:
            n = v["n"]
            rows.append({"torus": list(t), "n": n, "group": v["group"],
                         "d_max": max(v["best"].values()),
                         "s_max": max(k * d * d / n for k, d in v["best"].items())})  # fmt: skip
    by_n = defaultdict(int)
    for r in rows:
        by_n[r["n"]] = max(by_n[r["n"]], r["d_max"])
    ns = np.array([n for n in sorted(by_n) if n >= 60], dtype=float)
    ds = np.array([by_n[int(n)] for n in ns], dtype=float)
    b, loga = np.polyfit(np.log(ns), np.log(ds), 1)
    use = [r for r in rows if r["n"] >= 60]
    c = max(r["d_max"] / r["n"] ** b for r in use)
    arg = max(use, key=lambda r: r["d_max"] / r["n"] ** b)
    bands = {}
    for lo in range(50, 300, 50):
        sel = [r for r in rows if lo < r["n"] <= lo + 50]
        if sel:
            top = max(sel, key=lambda r: r["s_max"])
            bands[f"{lo + 1}-{lo + 50}"] = {"s_max": round(top["s_max"], 4), "torus": top["torus"],
                                            "n": top["n"]}  # fmt: skip
    mids = np.array([int(k.split("-")[1]) for k in bands], dtype=float)
    smax = np.array([v["s_max"] for v in bands.values()])
    slope, icept = np.polyfit(mids, smax, 1)
    ratio = {f"{lo + 1}-{lo + 50}": round(max((r["d_max"] / math.sqrt(r["n"]) for r in rows
                                               if lo < r["n"] <= lo + 50), default=0), 4)
             for lo in range(0, 300, 50)}  # fmt: skip
    return {"tori_with_codes": len(rows), "b": round(float(b), 4),
            "a": round(math.exp(loga), 4), "c": round(float(c), 4), "c_at": arg,
            "d_over_sqrt_n_by_band": ratio, "score_by_band": bands,
            "score_line": {"slope_per_n": round(float(slope), 5),
                           "at_350": round(float(slope * 350 + icept), 2),
                           "at_400": round(float(slope * 400 + icept), 2)},
            "record_score": max(r["s_max"] for r in rows),
            "record_d_over_sqrt_n": max(r["d_max"] / math.sqrt(r["n"]) for r in rows)}  # fmt: skip


if __name__ == "__main__":
    out = fit()
    print(json.dumps(out, indent=1))
    b, c = out["b"], out["c"]
    for n in (302, 330, 350, 380, 400):
        print(
            n,
            "envelope c n^b =",
            round(c * n**b, 2),
            " fit a n^b =",
            round(out["a"] * n**b, 2),
            " 1.461 sqrt n =",
            round(1.461 * math.sqrt(n), 2),
        )
