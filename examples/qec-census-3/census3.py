"""
The code census, stage 3a: every weight-6 bivariate bicycle code (A and B each three distinct
monomials) on the stage-1 tori, with exact distances. An exploratory survey like stage 1 (not a
registered test); its patterns are meant to feed a registered stage 3b on the held-out tori.

    uv run --no-sync python examples/qec-census-3/census3.py run --workers 4    (resumes)
    uv run --no-sync python examples/qec-census-3/census3.py torus L M          (one torus)
    uv run --no-sync python examples/qec-census-3/census3.py summary

**The family.** A and B each a set of three distinct monomials of Z_l x Z_m. Stage 1's form
(A = x^a + y^b + y^c, B = y^d + x^e + x^f) is a subfamily. Multiplying A, or B, by a monomial is
an equivalence (examples/qec-distance-2's equivalence_key), so every class has a member with 1 in
A and 1 in B, and the census enumerates A = 1 + u + v and B = 1 + s + t with u < v and s < t
nonzero monomials (as indices p m + q), and, since swapping A and B is an equivalence too, only
the pairs with (u, v) <= (s, t). Raw codes: N (N + 1) / 2 with N = C(lm - 1, 2).

**k > 0, by common zeros.** k = 2 sum over the characters chi of the odd part of
dim L/(A_chi, B_chi) (bb.local_terms), and a term is nonzero exactly when both A_chi and B_chi
are non-units of the local ring L, that is, when A(alpha, beta) = B(alpha, beta) = 0 at chi's
roots of unity (alpha, beta) in GF(2^r). So k > 0 exactly when A and B have a common zero among
the characters. The census evaluates every A = 1 + u + v at every character once (`zero_masks`),
and keeps the pairs whose zero sets meet (`candidates`); the tests check the rule against
bb.k_linalg on every raw code of small tori.

**Classes.** The candidates are grouped by stage 1's census.c key (census.canonical: monomial
factors on A and on B, the swap, and the automorphisms of the torus); k is computed for each
class's representative (bb.k_linalg) and for up to K_CHECKS further members, which must agree.

**Distances.** For each class, examples/qec-open-distance-2's packing search (search_pack.c,
registered and tested there), deepening from 2 from anchors (0, lm) in one process, with a limit
of LIMIT seconds: exact d when it completes, else the lower bound of its last empty pass. Every
witness is checked by distance.verify_witness. d_X = d_Z, so kind Z only.

**The hold-out.** Every function that computes on a torus calls stage 1's census.guard, which
refuses the held-out tori, any torus outside stage1_tori, and the 8 stage-1 tori isomorphic to a
held-out one (census.census_tori()).
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


census = _load("qec_census_stage1", HERE.parent / "qec-census" / "census.py")
pack = _load("qec_open_pack", HERE.parent / "qec-open-distance-2" / "pack.py")
bb, distance = census.bb, census.distance

DATA = HERE / "data"
LIMIT = 600.0
K_CHECKS = 2
CHUNK = 200_000


def guard(ell: int, m: int) -> None:
    census.guard(ell, m)


def _mono(t: int, m: int) -> tuple[int, int]:
    return (t // m, t % m)


def polynomial(pair, m: int) -> list[tuple[int, int]]:
    """1 + u + v for a pair (u, v) of monomial indices."""
    return [(0, 0), _mono(int(pair[0]), m), _mono(int(pair[1]), m)]


def zero_masks(ell: int, m: int):
    """(pairs, masks): every pair u < v of nonzero monomial indices, and for each the set of
    characters chi of the odd part with (1 + u + v)(chi) = 0, as a bitmask over characters."""
    guard(ell, m)
    (_, lo), (_, mo) = bb.two_part(ell), bb.two_part(m)
    N = math.lcm(lo, mo)
    F = bb._field(N)
    roots = [F.pow(F.zeta, e) for e in range(N)]
    chars = [(j, k) for j in range(lo) for k in range(mo)]
    value = np.array([[roots[(j * (N // lo) * p + k * (N // mo) * q) % N] for j, k in chars]
                      for p in range(ell) for q in range(m)], dtype=np.int64)  # fmt: skip
    pairs = np.array(list(itertools.combinations(range(1, ell * m), 2)), dtype=np.int64)
    zero = (value[0][None, :] ^ value[pairs[:, 0]] ^ value[pairs[:, 1]]) == 0
    words = (len(chars) + 63) // 64
    masks = np.zeros((len(pairs), words), dtype=np.uint64)
    for c in range(len(chars)):
        masks[:, c // 64] |= zero[:, c].astype(np.uint64) << np.uint64(c % 64)
    return pairs, masks


def candidates(ell: int, m: int) -> list[tuple[int, int]]:
    """The pairs (i, j), i <= j, of indices into zero_masks' pairs whose zero sets meet: the raw
    codes with k > 0."""
    pairs, masks = zero_masks(ell, m)
    live = np.flatnonzero(masks.any(axis=1))
    sub = masks[live]
    out = []
    for a, i in enumerate(live):
        meet = np.zeros(len(live) - a, dtype=bool)
        for w in range(sub.shape[1]):
            meet |= (sub[a, w] & sub[a:, w]) != 0
        out.extend((int(i), int(live[a + b])) for b in np.flatnonzero(meet))
    return pairs, out


def generates(A, B, ell: int, m: int) -> bool:
    """True when the differences of A's terms and of B's terms generate Z_l x Z_m (the code is
    connected: not a disjoint union of copies of a code on a smaller torus)."""
    steps = {((p[0] - q[0]) % ell, (p[1] - q[1]) % m) for P in (A, B) for p in P for q in P}
    reached, frontier = {(0, 0)}, [(0, 0)]
    while frontier:
        x = frontier.pop()
        for g in steps:
            y = ((x[0] + g[0]) % ell, (x[1] + g[1]) % m)
            if y not in reached:
                reached.add(y)
                frontier.append(y)
    return len(reached) == ell * m


def classes(ell: int, m: int) -> dict:
    """The classes of the raw codes with k > 0: for each, its key, size, representative, k
    (checked on up to K_CHECKS more members) and whether it is connected."""
    guard(ell, m)
    start = time.time()
    pairs, cand = candidates(ell, m)
    groups: dict[tuple, list[tuple[int, int]]] = {}
    for c0 in range(0, len(cand), CHUNK):
        chunk = cand[c0 : c0 + CHUNK]
        codes = [(polynomial(pairs[i], m), polynomial(pairs[j], m)) for i, j in chunk]
        for (key, _, _), ij in zip(census.canonical(codes, ell, m), chunk, strict=True):
            groups.setdefault(key, []).append(ij)
    out = []
    for key, members in groups.items():
        A, B = (polynomial(pairs[t], m) for t in members[0])
        k = bb.k_linalg(A, B, ell, m)
        for ij in members[1 : 1 + K_CHECKS]:
            A2, B2 = (polynomial(pairs[t], m) for t in ij)
            if bb.k_linalg(A2, B2, ell, m) != k:
                raise RuntimeError(f"{ell}x{m}: k differs within the class of {A}, {B}")
        if k == 0:
            raise RuntimeError(f"{ell}x{m}: a candidate with k = 0: {A}, {B}")
        out.append({"key": [list(map(list, P)) for P in key], "size": len(members),
                    "A": [list(t) for t in A], "B": [list(t) for t in B], "k": k,
                    "connected": generates(A, B, ell, m)})  # fmt: skip
    out.sort(key=lambda c: (-c["k"], c["key"]))
    raw = len(pairs) * (len(pairs) + 1) // 2
    return {"l": ell, "m": m, "n": 2 * ell * m, "raw_codes": raw, "raw_k_positive": len(cand),
            "classes": out, "seconds": round(time.time() - start, 2)}  # fmt: skip


def small_weight(A, B, ell: int, m: int, wmax: int = 4) -> dict:
    """For codes beyond search_pack.c's 128 logical labels: the least weight w <= wmax of a
    Z-logical, by enumeration. A set of qubits has zero syndrome when its columns of H_X sum to
    zero; w = 1 needs a zero column, w = 2 two equal columns, w = 3 a pair whose column sum is a
    third column, w = 4 two pairs with equal sums. Each zero-syndrome set found is tested against
    every X-logical (distance._logicals_bits: nontrivial when some L has odd overlap) and checked
    by verify_witness; d is exact when one is found, else d > wmax (status "lower")."""
    guard(ell, m)
    n = 2 * ell * m
    hx, hz = distance._bit_rows(A, B, ell, m)
    logicals = distance._logicals_bits(hz, hx, n)  # X-logicals: ker H_Z mod rowspace H_X
    col = [sum(((row >> q) & 1) << i for i, row in enumerate(hx)) for q in range(n)]

    def nontrivial(qs):
        c = sum(1 << q for q in qs)
        return any((c & L).bit_count() & 1 for L in logicals)

    def found(qs):
        qs = sorted(qs)
        check = distance.verify_witness(A, B, ell, m, "Z", qs)
        if not check["logical"]:
            raise RuntimeError(f"{ell}x{m}: a bad small-weight witness for {A}, {B}")
        return {"d": len(qs), "lower": len(qs), "status": "complete", "witness": qs}

    t0 = time.time()
    for q in range(n):
        if col[q] == 0 and nontrivial([q]):
            return found([q]) | {"seconds": round(time.time() - t0, 3), "method": "small"}
    pairs: dict[int, list[tuple[int, int]]] = {}
    for a in range(n):
        for b in range(a + 1, n):
            pairs.setdefault(col[a] ^ col[b], []).append((a, b))
    for a, b in pairs.get(0, []):
        if nontrivial([a, b]):
            return found([a, b]) | {"seconds": round(time.time() - t0, 3), "method": "small"}
    if wmax >= 3:
        for q in range(n):
            for a, b in pairs.get(col[q], []):
                if q not in (a, b) and nontrivial([a, b, q]):
                    return found([a, b, q]) | {"seconds": round(time.time() - t0, 3),
                                               "method": "small"}  # fmt: skip
    if wmax >= 4:
        for group in pairs.values():
            for i, (a, b) in enumerate(group):
                for c, e in group[i + 1 :]:
                    qs = {a, b, c, e}
                    if len(qs) == 4 and nontrivial(qs):
                        return found(qs) | {"seconds": round(time.time() - t0, 3),
                                            "method": "small"}  # fmt: skip
    return {"d": None, "lower": wmax + 1, "status": "lower", "witness": None,
            "seconds": round(time.time() - t0, 3), "method": "small"}  # fmt: skip


def deep_distance(A, B, ell: int, m: int, limit: float = LIMIT) -> dict:
    """The packing search, deepening from 2 from (0, lm), in one process (search_pack.c's
    passes): exact d when it completes, else the lower bound of its last empty pass."""
    guard(ell, m)
    if bb.k_linalg(A, B, ell, m) > 128:
        return small_weight(A, B, ell, m)
    n, r, k, rows, marks = pack.packed._code(A, B, ell, m, "Z")
    exe, _ = pack.packed.binary(str(pack.SEARCH_C))
    text = "\n".join([f"{n} {r} {k} 2 {distance.SEARCH_BOUND} 2", f"0 {ell * m}", *rows,
                      *marks]) + "\n"  # fmt: skip
    t0 = time.time()
    stdout, done = pack.packed._run([exe], text, limit)
    finds = pack.packed._finds(stdout)
    passes = [int(w[1]) for w in map(str.split, stdout.splitlines()) if w[:1] == ["pass"]]
    lower = passes[-1] if passes else None
    witness = finds[-1] if finds else None
    if witness:
        check = distance.verify_witness(A, B, ell, m, "Z", witness)
        if not check["logical"] or (lower is not None and len(witness) < lower):
            raise RuntimeError(f"{ell}x{m}: a bad witness for {A}, {B}")
    d = len(witness) if done and witness else None
    return {"d": d, "lower": d if d is not None else lower, "status": "complete" if d else
            "timelimit", "seconds": round(time.time() - t0, 3), "witness": witness}  # fmt: skip


def torus_file(ell: int, m: int) -> Path:
    return DATA / f"{ell}x{m}.jsonl"


def census_torus(ell: int, m: int, workers: int = 4, limit: float = LIMIT, log=print) -> Path:
    guard(ell, m)
    c = classes(ell, m)
    log(f"{ell}x{m}: {c['raw_k_positive']} raw codes with k > 0, {len(c['classes'])} classes "
        f"({c['seconds']} s)")  # fmt: skip

    def one(cl):
        return cl | deep_distance(cl["A"], cl["B"], ell, m, limit)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(one, c["classes"]))
    header = {"l": ell, "m": m, "n": c["n"], "raw_codes": c["raw_codes"],
              "raw_k_positive": c["raw_k_positive"], "classes": len(rows),
              "classes_seconds": c["seconds"], "distance_seconds": round(time.time() - t0, 1),
              "limit": limit, "search_pack_c_sha256": pack.sha256(pack.SEARCH_C),
              "census3_py_sha256": pack.sha256(Path(__file__))}  # fmt: skip
    DATA.mkdir(exist_ok=True)
    path = torus_file(ell, m)
    tmp = path.with_suffix(".tmp")
    tmp.write_text("\n".join(json.dumps(x, sort_keys=True) for x in [header, *rows]) + "\n")
    tmp.replace(path)
    log(f"{ell}x{m}: done, distances {header['distance_seconds']} s")
    return path


def tori() -> list[tuple[int, int]]:
    """The stage-1 tori the guard allows, cheapest first (by raw-code count)."""
    return sorted(census.census_tori(), key=lambda t: (t[0] * t[1], t))


def read_torus(path: Path) -> tuple[dict, list[dict]]:
    lines = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    return lines[0], lines[1:]


def summary() -> dict:
    """The frontier: for each n and k, the best d over the classes (exact where the search
    completed), and the best k d^2 / n per n, over connected classes and over all."""
    best: dict[tuple[int, int], dict] = {}
    open_ = Counter()
    for path in sorted(DATA.glob("*.jsonl")):
        head, rows = read_torus(path)
        for r in rows:
            if r["status"] != "complete":
                open_[(head["n"], r["k"])] += 1
            key = (head["n"], r["k"])
            if r["lower"] is not None and (key not in best or r["lower"] > best[key]["d"]):
                best[key] = {"n": head["n"], "k": r["k"], "d": r["lower"],
                             "exact": r["status"] == "complete", "torus": f"{head['l']}x{head['m']}",
                             "A": r["A"], "B": r["B"], "connected": r["connected"]}  # fmt: skip
    return {
        "frontier": sorted(best.values(), key=lambda x: (x["n"], -x["k"])),
        "not_complete": {f"{n},{k}": v for (n, k), v in sorted(open_.items())},
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--limit", type=float, default=LIMIT)
    t = sub.add_parser("torus")
    t.add_argument("l", type=int)
    t.add_argument("m", type=int)
    t.add_argument("--workers", type=int, default=4)
    t.add_argument("--limit", type=float, default=LIMIT)
    sub.add_parser("summary")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        for ell, m in tori():
            if not torus_file(ell, m).exists():
                census_torus(ell, m, a.workers, a.limit, log=lambda s: print(s, flush=True))
    elif a.cmd == "torus":
        census_torus(a.l, a.m, a.workers, a.limit, log=lambda s: print(s, flush=True))
    else:
        print(json.dumps(summary(), indent=1))


if __name__ == "__main__":
    main()
