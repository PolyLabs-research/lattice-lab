"""
Independent check of [[310,10,22]] (stage 4's record k d^2/n = 15.61, on 5 x 31), with the
spot-check's instruments and its rules (examples/qec-census-3b/spotcheck/run.py: execute, assess,
tier). Stage 4 found its d with DistQLDPC's cluster engine (10.8 s) and a witness checked by
distance.verify_witness. Run after that result was known; not part of stage 4's registration.

    python examples/qec-census-4/check-310/check.py [--limit SECONDS] [--workers N] [--only C6,...]
        [--out FILE]   (records-long.jsonl: the pod's rerun of the unfinished checks, 24 h limits)

The checks:
- **C1** SCIP (a second method);
- **C2** this project's unpruned search from every qubit;
- **C3** the packing search on X-logicals (d_X = d_Z);
- **C4** long windows, Z and X;
- **C5** DistQLDPC's MaxSAT engine (a second method) and cluster engine;
- **C6** SAT with a drat-trim-checked DRAT proof:
  - at w = 21, "no Z-logical of weight <= 21", which certifies d = 22 together with the witness;
  - at w = 20, which certifies d >= 21, and so d = 22 by the parity of d (Proved 6 in
    docs/code-census.md).
Records go to records.jsonl here, one per job. A job already recorded is skipped.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "records.jsonl"
CODE = {"torus": [5, 31], "n": 310, "k": 10, "d": 22,
        "A": [[0, 0], [0, 1], [1, 13]], "B": [[0, 0], [1, 27], [3, 17]],
        "witness": [4, 5, 27, 38, 39, 45, 46, 47, 79, 90, 183, 193, 200, 204, 210, 220, 231,
                    235, 279, 283, 289, 303],
        "group": "stage4", "why": "stage 4's record k d^2/n"}  # fmt: skip


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


R = _load("spotcheck_run", ROOT / "examples" / "qec-census-3b" / "spotcheck" / "run.py")


def jobs() -> list[dict]:
    out = [{"check": "C4", "code": CODE, "kind": k, "seed": s} for k in ("Z", "X") for s in (0, 1)]
    out += [{"check": c, "code": CODE} for c in ("C3", "C2", "C1", "C6")]
    out += [{"check": "C6", "code": CODE, "w": 20}]
    out += [{"check": "C5", "code": CODE, "engine": e} for e in ("maxsat", "cc")]
    for j in out:
        j["key"] = R.key(j) + (f":w={j['w']}" if "w" in j else "")
    return out


def execute(j: dict, limit: float) -> dict:
    R.LIMITS = {k: limit for k in R.LIMITS}
    R.WINDOW_SECONDS = min(900.0, limit)
    if j["check"] == "C6" and "w" in j:  # the parity claim: no Z-logical of weight <= w
        pack, sat, _ = R._instruments()
        D = pack.distance
        A, B = R._ab(j["code"])
        ell, m = j["code"]["torus"]
        hx, hz = D._bit_rows(A, B, ell, m)
        logicals = D._logicals_bits(hz, hx, 2 * ell * m)
        t0 = time.time()
        r = sat.certify(hx, logicals, 2 * ell * m, j["w"], anchors=(0, ell * m), limit=limit)
        if r.get("support") is not None:
            r["support_check"] = D.verify_witness(A, B, ell, m, "Z", r["support"])
        r["witness_check"] = D.verify_witness(A, B, ell, m, "Z", j["code"]["witness"])
        return {**j, "result": r, "seconds": round(time.time() - t0, 1)}
    return R.execute(j)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=float, default=3600.0)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--only")
    p.add_argument("--out", type=Path, default=OUT, help="records file (a longer rerun: its own)")
    a = p.parse_args()
    out = a.out
    done = {json.loads(x)["key"] for x in out.read_text().splitlines()} if out.exists() else set()
    todo = [j for j in jobs() if j["key"] not in done
            and (not a.only or j["check"] in a.only.split(","))]  # fmt: skip
    with ProcessPoolExecutor(a.workers) as pool:
        for rec in pool.map(execute, todo, [a.limit] * len(todo)):
            with out.open("a") as fh:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
            res = rec.get("result") or {}
            print(
                rec["key"][:40],
                rec.get("error", "")[-200:]
                or {k: res.get(k) for k in ("status", "d", "lower", "upper")},
                flush=True,
            )


if __name__ == "__main__":
    main()
