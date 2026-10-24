"""
Faster instruments for census stage 3b, checked against stage 3a's (examples/qec-census-3) on
the stage-1 tori before anything runs on a held-out torus.

**Classes by orbit representatives** (`classes`). Stage 3a sent every pair (A, B) with k > 0 to
census.c's canonical key. Here the polynomials 1 + u + v are first grouped into orbits under the
torus group (automorphisms, then the translation that puts 1 back in: `poly_orbits`), and only
pairs (a, B) are keyed, with a an orbit representative and B any polynomial whose orbit is not
before a's. Every class is reached: a class holds (A, B) and (B, A); take the order in which A's
orbit comes first, then apply the group element that carries A to its representative, which
carries B to a polynomial of the same orbit as B. The keys are census.c's, so the classes are
stage 3a's, and the tests check that on stage-1 tori. Class sizes are not computed.

**The frontier driver** (`frontier`). The predictions need, for each k, the best exact d, not
every class's d. For each class an upper bound comes first: the window (random information
sets, examples/qec-open-distance/window.c) with a fixed seed and WINDOW_SECONDS. Then, for each k,
the classes in decreasing order of that bound are taken in groups of `workers`: once a best
exists, each class whose bound is above it gets a second, longer window (WINDOW_RETRY), and
those still above go to the exact search (stage 3a's deep_distance). This goes on until the best
exact d found is at least the next class's bound. A class skipped
there has d <= its bound <= the best, so it cannot raise the best. Each skipped class keeps its
checked upper bound. Exact runs that time out are reported, and they make the best for that k
incomplete when their lower bound does not settle it.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WINDOW_SECONDS = 0.25  # the first bound, for every class
WINDOW_RETRY = 3.0  # a second, for a class whose bound is still above the best
WINDOW_SEED = 0


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c3 = _load("qec_census_stage3", HERE.parent / "qec-census-3" / "census3.py")
census, bb, distance, pack = c3.census, c3.bb, c3.distance, c3.pack


def guard(ell: int, m: int) -> None:
    """Replaced by study.py's guard in a registered run; stage 1's otherwise."""
    c3.guard(ell, m)


def poly_orbits(ell: int, m: int, pairs: np.ndarray) -> np.ndarray:
    """For each polynomial 1 + u + v (pairs[i] = (u, v)), the least index of a polynomial in its
    orbit under the automorphisms and translations of the torus."""
    guard(ell, m)
    index = {(int(u), int(v)): i for i, (u, v) in enumerate(pairs)}
    auts = census.automorphisms(ell, m)
    orbit = np.arange(len(pairs))
    for i, (u, v) in enumerate(pairs):
        mons = [(0, 0), (int(u) // m, int(u) % m), (int(v) // m, int(v) % m)]
        best = i
        for (g0, g1), (h0, h1) in auts:
            img = [((p * g0 + q * h0) % ell, (p * g1 + q * h1) % m) for p, q in mons]
            for p0, q0 in img:  # translate so that this monomial becomes 1
                ts = sorted(((p - p0) % ell) * m + (q - q0) % m for p, q in img)
                j = index[(ts[1], ts[2])]
                best = min(best, j)
        orbit[i] = best
    return orbit


def classes(ell: int, m: int) -> dict:
    """Stage 3a's classes (census.c keys) of the codes with k > 0, from orbit representatives:
    for each, its key, a representative pair, k and whether it is connected."""
    guard(ell, m)
    start = time.time()
    pairs, masks = c3.zero_masks(ell, m)
    orbit = poly_orbits(ell, m, pairs)
    live = np.flatnonzero(masks.any(axis=1))
    reps = [int(i) for i in live if orbit[i] == i]
    keys: dict[tuple, tuple[int, int]] = {}
    batch: list[tuple[int, int]] = []

    def flush():
        codes = [(c3.polynomial(pairs[i], m), c3.polynomial(pairs[j], m)) for i, j in batch]
        for (key, _, _), ij in zip(census.canonical(codes, ell, m), batch, strict=True):
            keys.setdefault(key, ij)
        batch.clear()

    for a in reps:
        meet = np.zeros(len(pairs), dtype=bool)
        for w in range(masks.shape[1]):
            meet |= (masks[a, w] & masks[:, w]) != 0
        for j in np.flatnonzero(meet & (orbit >= orbit[a])):
            batch.append((a, int(j)))
            if len(batch) >= c3.CHUNK:
                flush()
    if batch:
        flush()
    out = []
    for key, (i, j) in keys.items():
        A, B = c3.polynomial(pairs[i], m), c3.polynomial(pairs[j], m)
        k = bb.k_linalg(A, B, ell, m)
        if k == 0:
            raise RuntimeError(f"{ell}x{m}: a keyed pair with k = 0: {A}, {B}")
        out.append({"key": [[list(t) for t in P] for P in key], "A": [list(t) for t in A],
                    "B": [list(t) for t in B], "k": k,
                    "connected": c3.generates(A, B, ell, m)})  # fmt: skip
    out.sort(key=lambda c: (-c["k"], c["key"]))
    return {"l": ell, "m": m, "n": 2 * ell * m, "orbit_reps": len(reps), "classes": out,
            "seconds": round(time.time() - start, 2)}  # fmt: skip


def window_bound(A, B, ell: int, m: int, seconds: float = WINDOW_SECONDS) -> int | None:
    """A checked upper bound on d (kind Z) by the window; None for k > 128 (beyond window.c's
    labels), where small_weight decides."""
    guard(ell, m)
    if bb.k_linalg(A, B, ell, m) > 128:
        return None
    w = pack.plain.window(A, B, ell, m, "Z", seeds=(WINDOW_SEED,), seconds=seconds, workers=1)
    return w["upper"]


def frontier(ell: int, m: int, workers: int = 4, limit: float = 1800.0, log=print) -> dict:
    """For each k, the best exact d over the connected classes and over all classes, by the
    bound-then-exact rule (module docstring). Returns the classes with their bound and, where
    run, their exact result, and per k the best and whether it is settled."""
    guard(ell, m)
    c = classes(ell, m)
    rows = c["classes"]
    log(f"{ell}x{m}: {len(rows)} classes from {c['orbit_reps']} orbit representatives "
        f"({c['seconds']} s)")  # fmt: skip

    def bound(r):
        return r | {"upper": window_bound(r["A"], r["B"], ell, m)}

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(bound, rows))
    t_bound = time.time() - t0
    exact = {}

    def run(i):
        r = rows[i]
        return i, c3.deep_distance(r["A"], r["B"], ell, m, limit)

    # the connected classes decide the predictions; all classes are reported as well
    result = {}
    for label, pick in (("connected", lambda r: r["connected"]), ("all", lambda r: True)):
        per_k = defaultdict(list)
        for i, r in enumerate(rows):
            if pick(r):
                per_k[r["k"]].append(i)
        best = {}
        for k, idx in per_k.items():
            # unbounded (k > 128: small_weight decides) first, then by decreasing upper bound
            idx.sort(key=lambda i: -(rows[i]["upper"] if rows[i]["upper"] is not None else 10**6))
            top, unresolved, pos = None, [], 0
            while pos < len(idx):
                ub = rows[idx[pos]]["upper"]
                if top is not None and ub is not None and ub <= top:
                    break  # every class from here on has d <= its bound <= top
                todo = idx[pos : pos + workers]
                if top is not None:  # a longer window first: it may bring the bound to <= top
                    retry = [j for j in todo if j not in exact and rows[j]["upper"] is not None
                             and not rows[j].get("retried")]  # fmt: skip
                    def longer(j):
                        return window_bound(rows[j]["A"], rows[j]["B"], ell, m, WINDOW_RETRY)

                    with ThreadPoolExecutor(max_workers=workers) as pool:
                        for j, ub2 in zip(retry, pool.map(longer, retry), strict=True):
                            rows[j] = rows[j] | {"upper": min(rows[j]["upper"], ub2),
                                                 "retried": True}  # fmt: skip
                    todo = [j for j in todo if j in exact or rows[j]["upper"] is None
                            or rows[j]["upper"] > top]  # fmt: skip
                    if not todo:
                        pos += workers
                        idx[pos:] = sorted(idx[pos:], key=lambda i: -(rows[i]["upper"] if
                                           rows[i]["upper"] is not None else 10**6))  # fmt: skip
                        continue
                need = [j for j in todo if j not in exact]
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    for j, res in pool.map(run, need):
                        exact[j] = res
                for j in todo:
                    if exact[j]["status"] == "complete":
                        top = exact[j]["d"] if top is None else max(top, exact[j]["d"])
                    else:
                        unresolved.append(j)
                pos += workers
            # settled unless an unfinished class could still exceed the best
            settled = top is not None and all(
                rows[j]["upper"] is not None and rows[j]["upper"] <= top for j in unresolved
            )
            best[k] = {"d": top, "settled": settled, "unresolved": len(unresolved)}
        result[label] = best
    for i, res in exact.items():
        rows[i] = rows[i] | {"exact": res}
    return {**{k: c[k] for k in ("l", "m", "n", "orbit_reps")}, "classes_seconds": c["seconds"],
            "bound_seconds": round(t_bound, 1), "exact_runs": len(exact),
            "exact_seconds": round(sum(r["seconds"] for r in exact.values()), 1),
            "best": result, "classes": rows}  # fmt: skip
