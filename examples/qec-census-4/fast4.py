"""
Census stage 4's instrument: stage 3b's frontier driver (examples/qec-census-3b/fast.py) with
DistQLDPC as the exact engine, the parity of d used throughout, and room for lm <= 200.

**What is stage 3b's, unchanged.** The classes (fast.classes: orbit representatives, census.c's
canonical keys, k by bb.k_linalg, connectedness), the first window bound for every class
(WINDOW_SECONDS, seed WINDOW_SEED) and the longer one (WINDOW_RETRY), and the order of work: for
each k, classes by decreasing bound until the best exact d is at least the next bound. Stage 3b
took them in groups of `workers` and waited for each group; here up to `workers` run at once and
the next starts as soon as one ends (a class's longer window runs when it starts, against the
best found by then), so one long class no longer holds the others back. Stage 3c's two in-
process changes are applied too (bb._irreducible by Ben-Or's test, census3.zero_masks in two
64-bit words), through examples/qec-census-3c/study.py's `patched`.

**What changes.**
- **census4.c** is census.c with MAXLM = 200 and WORDS = 7 (2lm <= 448 bits), set as
  census.CENSUS_C inside `opened` only. Nothing else in it differs.
- **A third window.** A class whose bound is still above the best after WINDOW_RETRY gets a
  WINDOW_LONG window before any exact run. Like the others it only lowers a bound, with a checked
  witness, so it changes which classes need DistQLDPC, never a settled result. It was added
  after the validation run (validate4.py), to save exact runs at d >= 26.
- **The parity of d.** For this family d is even (A and B have odd weight, so the all-ones vector
  is in the row space of H_X and every Z-logical has even weight: docs/code-census.md, Proved 6).
  So an upper bound u gives d <= u - (u mod 2), and a lower bound l gives d >= l + (l mod 2).
  `even_down` and `even_up` apply it; the driver compares rounded bounds everywhere stage 3b
  compared raw ones.
- **The exact engine** (`exact`). DistQLDPC's cluster engine (-engine=cc, through
  examples/qec-census-3b/spotcheck/distq.py) with a wall-clock limit:
  - it returns d: the class is "complete" with that d, once a Z-logical of weight d is found and
    checked by distance.verify_witness: the window's witness if it has weight d, else longer
    windows (WITNESS_WINDOWS: seeds 1-2 for 120 s each, then seeds 3-10 for 300 s each, stopping at
    the first of weight d);
  - it stops first: its lower bound, rounded up to even, is kept. When that reaches the class's
    verified upper bound, the class is "complete" with d = that bound and the window's witness
    (status "complete", by "parity");
  - a d from DistQLDPC with no witness of that weight found is "unverified": it counts as
    unfinished, with DistQLDPC's d as its lower bound.
  - DistQLDPC killed at its limit + 600 s, or failing in any other way, leaves the class
    unfinished ("timelimit", with the error kept), never the torus failed.
  For k > 128 (beyond window.c's and DistQLDPC's use here) stage 3a's small_weight decides, as in
  stage 3b.
- **Checkpoints.** `frontier` takes the exact results already found (`cache`, by class key) and
  reports each new one (`on_exact`), so a stopped run loses only the classes in progress.
- **The guard.** `opened(tori)` lets exactly the given tori through census.guard, for this
  process's run, and nothing else.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
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
WINDOW_LONG = 60.0  # a third window, for a class still above the best after WINDOW_RETRY
LIMIT = 14400  # DistQLDPC's limit per class, seconds; the study sets its own
WITNESS_WINDOWS = [[[1, 2], 120.0], [list(range(3, 11)), 300.0]]  # [seeds, seconds] rounds


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
    census._census_binary.cache_clear()  # never a binary compiled from census.c before this
    try:
        with s3c.patched():
            yield
    finally:
        census.guard, census.CENSUS_C = original_guard, original_c
        census._census_binary.cache_clear()


def window(A, B, ell: int, m: int, seconds: float) -> tuple[int | None, list | None]:
    """The window's checked upper bound and its witness (kind Z, seed WINDOW_SEED); (None, None)
    for k > 128."""
    if bb.k_linalg(A, B, ell, m) > 128:
        return None, None
    w = pack.plain.window(A, B, ell, m, "Z", seeds=(WINDOW_SEED,), seconds=seconds, workers=1)
    return w["upper"], w["witness"]


def _witness_at(A, B, ell: int, m: int, d: int) -> list | None:
    """A Z-logical of weight d from longer windows (WITNESS_WINDOWS), or None. window() checks
    every witness it returns."""
    for seeds, seconds in WITNESS_WINDOWS:
        for seed in seeds:
            w = pack.plain.window(A, B, ell, m, "Z", seeds=(seed,), seconds=seconds, workers=1)
            if w["witness"] is not None and len(w["witness"]) == d:
                return w["witness"]
    return None


def exact(row: dict, ell: int, m: int, limit: float = LIMIT) -> dict:
    """The class's exact d by DistQLDPC and a verified witness, or the parity rule; else its
    best lower bound (module docstring)."""
    A, B = [tuple(t) for t in row["A"]], [tuple(t) for t in row["B"]]
    t0 = time.time()
    if row["k"] > 128:
        return c3.small_weight(A, B, ell, m) | {"engine": "small_weight"}
    upper, witness = row["upper"], row.get("witness")
    try:
        r = distq.run(A, B, ell, m, engine="cc", limit=int(limit))
    except Exception as exc:  # a crash leaves the class unfinished, not the torus failed
        return {"engine": "distqldpc-cc", "d": None, "lower": None, "status": "timelimit",
                "witness": None, "error": repr(exc)[-500:],
                "seconds": round(time.time() - t0, 3)}  # fmt: skip
    out = {"engine": "distqldpc-cc", "distqldpc": {k: r.get(k) for k in
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


def frontier(ell: int, m: int, workers: int = 4, limit: float = LIMIT, log=print,
             cache: dict | None = None, on_exact=None) -> dict:  # fmt: skip
    """Stage 3b's frontier (fast.frontier), with `exact` as the engine and bounds compared after
    rounding to even (module docstring). Same return shape; each exact result keeps its witness.
    `cache` maps a class key (json of row["key"]) to an exact result found before; `on_exact`
    is called with (key, result, row) for each new one."""
    import json

    cache = cache or {}
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
        key = json.dumps(rows[i]["key"])
        if key in cache:
            return i, cache[key]
        res = exact(rows[i], ell, m, limit)
        if on_exact is not None:
            on_exact(key, res, rows[i])
        return i, res

    def longer(j, top=None):
        """WINDOW_RETRY, then WINDOW_LONG if the bound is still above the best: the lighter."""
        u, w = window(rows[j]["A"], rows[j]["B"], ell, m, WINDOW_RETRY)
        if top is not None and u is not None and even_down(u) > top:
            u2, w2 = window(rows[j]["A"], rows[j]["B"], ell, m, WINDOW_LONG)
            if u2 is not None and u2 < u:
                u, w = u2, w2
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
            state = {"top": None}
            unresolved, pos = [], 0

            def job(j, state=state):
                """A longer window first when a best exists (it may bring the bound to <= the
                best, and then no exact run is needed), then the exact run."""
                top = state["top"]
                if j not in done and top is not None and rows[j]["upper"] is not None \
                        and not rows[j].get("retried"):  # fmt: skip
                    improve(j, *longer(j, top))
                    if ub(j) is not None and state["top"] is not None and ub(j) <= state["top"]:
                        return j, None  # skipped: d <= its bound <= the best
                return run(j)

            def take(j, res, state=state, unresolved=unresolved):
                if res is None:
                    return
                done[j] = res
                if res["status"] == "complete":
                    state["top"] = res["d"] if state["top"] is None else max(state["top"], res["d"])
                else:
                    unresolved.append(j)

            # rolling: up to `workers` classes at once, the next submitted as soon as one ends,
            # in decreasing order of bound, until the next bound is <= the best found
            with ThreadPoolExecutor(max_workers=workers) as pool:
                running = set()
                while True:
                    while len(running) < workers and pos < len(idx):
                        j, u = idx[pos], ub(idx[pos])
                        if state["top"] is not None and u is not None and u <= state["top"]:
                            pos = len(idx)  # every class from here on has d <= its bound <= top
                            break
                        pos += 1
                        if j in done:  # found in the connected pass (or the checkpoint)
                            take(j, done[j])
                            continue
                        running.add(pool.submit(job, j))
                    if not running:
                        break
                    finished, running = wait(running, return_when=FIRST_COMPLETED)
                    for f in finished:
                        take(*f.result())
            top = state["top"]
            # an unfinished class gets the longer windows too, if it has not had them
            late = [j for j in unresolved if rows[j]["upper"] is not None
                    and not rows[j].get("retried")]  # fmt: skip
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for j, (u2, w2) in zip(late, pool.map(lambda j, t=top: longer(j, t), late),
                                       strict=True):  # fmt: skip
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
