"""
Census stage 4's instrument: stage 3b's frontier driver (examples/qec-census-3b/fast.py) with
DistQLDPC as the exact engine, the parity of d used throughout, and room for lm <= 200.

**What is stage 3b's, unchanged.** The classes (fast.classes: orbit representatives, census.c's
canonical keys, k by bb.k_linalg, connectedness), the first window bound for every class
(WINDOW_SECONDS, seed WINDOW_SEED) and the longer one (WINDOW_RETRY), and the order of work: for
each k, classes by decreasing bound, `workers` at a time, until the best exact d is at least the
next bound. Stage 3c's two in-process changes are applied too (bb._irreducible by Ben-Or's test,
census3.zero_masks in two 64-bit words), through examples/qec-census-3c/study.py's `patched`.

**What changes.**
- **census4.c** is census.c with MAXLM = 200 and WORDS = 7 (2lm <= 448 bits), set as
  census.CENSUS_C inside `opened` only. Nothing else in it differs.
- **The parity of d.** For this family d is even (A and B have odd weight, so the all-ones vector
  is in the row space of H_X and every Z-logical has even weight: docs/code-census.md, Proved 6).
  So an upper bound u gives d <= u - (u mod 2), and a lower bound l gives d >= l + (l mod 2).
  `even_down` and `even_up` apply it; the driver compares rounded bounds everywhere stage 3b
  compared raw ones.
- **The exact engine** (`exact`). DistQLDPC's cluster engine (-engine=cc, through
  examples/qec-census-3b/spotcheck/distq.py) with a wall-clock limit:
  - it returns d: the class is "complete" with that d, once a Z-logical of weight d is found and
    checked by distance.verify_witness: the window's witness if it has weight d, else the packing
    search run at that one weight (first = last = d, from (0, lm));
  - it stops first: its lower bound, rounded up to even, is kept. When that reaches the class's
    verified upper bound, the class is "complete" with d = that bound and the window's witness
    (status "complete", by "parity");
  - a d from DistQLDPC with no witness of that weight found is "unverified": it counts as
    unfinished, with DistQLDPC's d as its lower bound.
  For k > 128 (beyond window.c's and DistQLDPC's use here) stage 3a's small_weight decides, as in
  stage 3b.
- **The guard.** `opened(tori)` lets exactly the given tori through census.guard, for this
  process's run, and nothing else.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = HERE.parent
CENSUS4_C = HERE / "census4.c"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fast = _load("qec_census_stage3b_fast", EX / "qec-census-3b" / "fast.py")
s3c = _load("qec_census_stage3c_study", EX / "qec-census-3c" / "study.py")
distq = _load("spotcheck_distq", EX / "qec-census-3b" / "spotcheck" / "distq.py")
c3, census, bb, distance, pack = fast.c3, fast.census, fast.bb, fast.distance, fast.pack

WINDOW_SECONDS, WINDOW_RETRY, WINDOW_SEED = fast.WINDOW_SECONDS, fast.WINDOW_RETRY, fast.WINDOW_SEED
LIMIT = 3600  # DistQLDPC's limit per class, seconds; the study sets its own
WITNESS_LIMIT = 1800.0  # the packing search's limit when it looks for a witness of weight d


def even_down(u: int | None) -> int | None:
    return None if u is None else u - (u % 2)


def even_up(lower: int | None) -> int | None:
    return None if lower is None else lower + (lower % 2)


@contextmanager
def opened(tori):
    """census.guard lets these tori through (and keeps refusing every other held-out or
    unknown torus); census.CENSUS_C is census4.c; stage 3c's two patches are on."""
    allowed = {(int(a), int(b)) for a, b in tori}
    original_guard, original_c = census.guard, census.CENSUS_C

    def guard(ell, m, allow_isomorphic=False):
        if (int(ell), int(m)) in allowed:
            return
        original_guard(ell, m, allow_isomorphic)

    census.guard, census.CENSUS_C = guard, CENSUS4_C
    try:
        with s3c.patched():
            yield
    finally:
        census.guard, census.CENSUS_C = original_guard, original_c


def window(A, B, ell: int, m: int, seconds: float) -> tuple[int | None, list | None]:
    """The window's checked upper bound and its witness (kind Z, seed WINDOW_SEED); (None, None)
    for k > 128."""
    if bb.k_linalg(A, B, ell, m) > 128:
        return None, None
    w = pack.plain.window(A, B, ell, m, "Z", seeds=(WINDOW_SEED,), seconds=seconds, workers=1)
    return w["upper"], w["witness"]


def _witness_at(A, B, ell: int, m: int, d: int) -> list | None:
    """A verified Z-logical of weight d by the packing search at that one weight, or None."""
    r = pack.search(A, B, ell, m, "Z", anchors=(0, ell * m), first=d, last=d, parts=1,
                    workers=1, time_limit=WITNESS_LIMIT)  # fmt: skip
    if r["status"] == "complete" and r["d"] == d:
        return r["witness"]
    return None


def exact(row: dict, ell: int, m: int, limit: float = LIMIT) -> dict:
    """The class's exact d by DistQLDPC and a verified witness, or the parity rule; else its
    best lower bound (module docstring)."""
    A, B = [tuple(t) for t in row["A"]], [tuple(t) for t in row["B"]]
    t0 = time.time()
    if row["k"] > 128:
        return c3.small_weight(A, B, ell, m) | {"engine": "small_weight"}
    upper, witness = row["upper"], row.get("witness")
    r = distq.run(A, B, ell, m, engine="cc", limit=int(limit))
    out = {"engine": "distqldpc-cc", "distqldpc": {k: r[k] for k in
                                                   ("d", "lower", "upper", "returncode",
                                                    "withdrawn", "seconds")}}  # fmt: skip
    if r["d"] is not None:
        d = r["d"]
        if upper is not None and upper < d:
            raise RuntimeError(f"{ell}x{m}: DistQLDPC d = {d} above a verified bound {upper}")
        w = witness if witness is not None and len(witness) == d else _witness_at(A, B, ell, m, d)
        if w is not None:
            check = distance.verify_witness(A, B, ell, m, "Z", w)
            if not check["logical"] or check["weight"] != d:
                raise RuntimeError(f"{ell}x{m}: a bad witness of weight {d}")
            return out | {"d": d, "lower": d, "status": "complete", "by": "distqldpc",
                          "witness": w, "seconds": round(time.time() - t0, 3)}  # fmt: skip
        return out | {"d": None, "lower": d, "status": "unverified", "witness": None,
                      "seconds": round(time.time() - t0, 3)}  # fmt: skip
    lower = even_up(r["lower"])
    if lower is not None and upper is not None and lower >= even_down(upper):
        if lower > upper:
            raise RuntimeError(f"{ell}x{m}: DistQLDPC lower {r['lower']} above upper {upper}")
        check = distance.verify_witness(A, B, ell, m, "Z", witness)
        if not check["logical"] or check["weight"] != upper:
            raise RuntimeError(f"{ell}x{m}: the window's witness does not check")
        return out | {"d": upper, "lower": upper, "status": "complete", "by": "parity",
                      "witness": witness, "seconds": round(time.time() - t0, 3)}  # fmt: skip
    return out | {"d": None, "lower": lower, "status": "timelimit", "witness": None,
                  "seconds": round(time.time() - t0, 3)}  # fmt: skip


def frontier(ell: int, m: int, workers: int = 4, limit: float = LIMIT, log=print) -> dict:
    """Stage 3b's frontier (fast.frontier), with `exact` as the engine and bounds compared after
    rounding to even (module docstring). Same return shape, plus each class's witness when it
    has one."""
    c = fast.classes(ell, m)
    rows = c["classes"]
    log(f"{ell}x{m}: {len(rows)} classes from {c['orbit_reps']} orbit representatives "
        f"({c['seconds']} s)")  # fmt: skip

    def bound(r):
        u, w = window(r["A"], r["B"], ell, m, WINDOW_SECONDS)
        return r | {"upper": u, "witness": w}

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(bound, rows))
    t_bound = time.time() - t0
    done: dict[int, dict] = {}

    def run(i):
        return i, exact(rows[i], ell, m, limit)

    def longer(j):
        u, w = window(rows[j]["A"], rows[j]["B"], ell, m, WINDOW_RETRY)
        return u, w

    def ub(i):  # the rounded upper bound; None (k > 128) sorts first
        return even_down(rows[i]["upper"])

    def improve(j, u2, w2):
        r = rows[j]
        if u2 is not None and (r["upper"] is None or u2 < r["upper"]):
            rows[j] = r | {"upper": u2, "witness": w2, "retried": True}
        else:
            rows[j] = r | {"retried": True}

    result = {}
    for label, pick in (("connected", lambda r: r["connected"]), ("all", lambda r: True)):
        per_k = defaultdict(list)
        for i, r in enumerate(rows):
            if pick(r):
                per_k[r["k"]].append(i)
        best = {}
        for k, idx in per_k.items():
            idx.sort(key=lambda i: -(ub(i) if ub(i) is not None else 10**6))
            top, unresolved, pos = None, [], 0
            while pos < len(idx):
                u = ub(idx[pos])
                if top is not None and u is not None and u <= top:
                    break  # every class from here on has d <= its rounded bound <= top
                todo = idx[pos : pos + workers]
                if top is not None:
                    retry = [j for j in todo if j not in done and rows[j]["upper"] is not None
                             and not rows[j].get("retried")]  # fmt: skip
                    with ThreadPoolExecutor(max_workers=workers) as pool:
                        for j, (u2, w2) in zip(retry, pool.map(longer, retry), strict=True):
                            improve(j, u2, w2)
                    todo = [j for j in todo if j in done or ub(j) is None or ub(j) > top]
                    if not todo:
                        pos += workers
                        idx[pos:] = sorted(idx[pos:], key=lambda i: -(ub(i) if ub(i) is not None
                                                                     else 10**6))  # fmt: skip
                        continue
                need = [j for j in todo if j not in done]
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    for j, res in pool.map(run, need):
                        done[j] = res
                for j in todo:
                    if done[j]["status"] == "complete":
                        top = done[j]["d"] if top is None else max(top, done[j]["d"])
                    else:
                        unresolved.append(j)
                pos += workers
            late = [j for j in unresolved if rows[j]["upper"] is not None
                    and not rows[j].get("retried")]  # fmt: skip
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for j, (u2, w2) in zip(late, pool.map(longer, late), strict=True):
                    improve(j, u2, w2)
            settled = top is not None and all(ub(j) is not None and ub(j) <= top
                                              for j in unresolved)  # fmt: skip
            best[k] = {"d": top, "settled": settled, "unresolved": len(unresolved)}
        result[label] = best
    for i, res in done.items():
        rows[i] = rows[i] | {"exact": res}
    return {**{k: c[k] for k in ("l", "m", "n", "orbit_reps")}, "classes_seconds": c["seconds"],
            "bound_seconds": round(t_bound, 1), "exact_runs": len(done),
            "exact_seconds": round(sum(r["seconds"] for r in done.values()), 1),
            "best": result, "classes": rows}  # fmt: skip
