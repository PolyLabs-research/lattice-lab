"""
Stage 3a's analysis (examples/qec-census-3/census3.py's data): the frontier of weight-6 codes by
n and k, against stage 1's frontier of the published form (examples/qec-census/summary.json) and,
for n <= 100, against Lin and Pryadko's catalog of abelian two-block codes (QEC-pages/2BGA-codes,
abelian.zip, weight 6 with 3 + 3 terms), passed as a JSON file of its parsed entries.

    uv run --no-sync python examples/qec-census-3/analyse.py [--catalog bga_abelian.json]

The catalog is compared by (group order, k): its best d over all abelian groups of that order
against ours over the tori of that order. Tori are the abelian groups with at most two
generators, so where the catalog's best comes from a group needing three (Z_2^3 x ..., say) ours
may be lower, and never higher if both are right.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
STAGE1 = HERE.parent / "qec-census" / "summary.json"


def rows():
    for path in sorted(DATA.glob("*.jsonl")):
        lines = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        for r in lines[1:]:
            yield lines[0], r


def frontier(connected_only: bool = False) -> dict:
    """(n, k) -> the best exact d and where; an open class (timed out) whose lower bound is at
    least the best exact d is flagged."""
    best, open_ = {}, defaultdict(list)
    for h, r in rows():
        if connected_only and not r["connected"]:
            continue
        key = (h["n"], r["k"])
        if r["status"] != "complete":
            open_[key].append(r["lower"])
            continue
        if key not in best or r["d"] > best[key]["d"]:
            best[key] = {"d": r["d"], "torus": f"{h['l']}x{h['m']}", "A": r["A"], "B": r["B"],
                         "connected": r["connected"], "count": 0}  # fmt: skip
        if r["d"] == best[key]["d"]:
            best[key]["count"] += 1
    for key, lows in open_.items():
        if key in best:
            best[key]["open_at_or_above"] = sum(1 for x in lows if x is not None and
                                                x >= best[key]["d"])  # fmt: skip
        else:
            best[key] = {"d": None, "open_lower": max(x or 0 for x in lows)}
    return best


def stage1_best() -> dict:
    out = {}
    for entry in json.loads(STAGE1.read_text())["frontier"]:
        for k, v in entry["best_d_by_k"].items():
            out[(entry["n"], int(k))] = v["d"]
    return out


def catalog_best(path: Path) -> dict:
    out = {}
    for x in json.loads(Path(path).read_text()):
        if (x["wt"], x["wtL"]) != (6, 3):
            continue
        key = (2 * x["order"], x["k"])
        out[key] = max(out.get(key, 0), x["d"])
    return out


def score(n, k, d):
    return k * d * d / n


def report(catalog: Path | None) -> dict:
    ours, ours_conn, old = frontier(), frontier(True), stage1_best()
    better = sorted((n, k, v["d"], old[(n, k)]) for (n, k), v in ours.items()
                    if v["d"] is not None and (n, k) in old and v["d"] > old[(n, k)])  # fmt: skip
    new_k = sorted((n, k, v["d"]) for (n, k), v in ours.items()
                   if v["d"] is not None and (n, k) not in old)  # fmt: skip
    worse = sorted((n, k, v["d"], old[(n, k)]) for (n, k), v in ours.items()
                   if v["d"] is not None and (n, k) in old and v["d"] < old[(n, k)])  # fmt: skip
    by_n = defaultdict(list)
    for (n, k), v in ours_conn.items():
        if v["d"] is not None:
            by_n[n].append((score(n, k, v["d"]), k, v["d"]))
    best_score = {n: max(v) for n, v in sorted(by_n.items())}
    out = {"stage1_improved": better, "stage1_missing_k": new_k, "below_stage1": worse,
           "best_score_by_n": {str(n): {"score": round(s, 3), "k": k, "d": d}
                               for n, (s, k, d) in best_score.items()},
           "open": {f"{n},{k}": v for (n, k), v in ours.items() if v.get("d") is None
                    or v.get("open_at_or_above")}}  # fmt: skip
    if catalog:
        cat = catalog_best(catalog)
        conn = {key: v["d"] for key, v in ours_conn.items() if v["d"] is not None}
        out["catalog"] = {
            "pairs_compared": len(set(cat) & set(conn)),
            "equal": sorted(k for k in set(cat) & set(conn) if cat[k] == conn[k]),
            "ours_lower": sorted((k, conn[k], cat[k]) for k in set(cat) & set(conn)
                                 if conn[k] < cat[k]),  # fmt: skip
            "ours_higher": sorted((k, conn[k], cat[k]) for k in set(cat) & set(conn)
                                  if conn[k] > cat[k]),  # fmt: skip
            "catalog_only": sorted(k for k in set(cat) - set(conn) if k[0] <= 200),
        }
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path)
    a = ap.parse_args()
    print(json.dumps(report(a.catalog), indent=1, default=list))
