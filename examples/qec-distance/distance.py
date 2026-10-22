"""
Exact distances of bivariate bicycle codes: an integer program solved by SCIP, an enumeration
and a search that share nothing with it, and an independent check of the programs' witnesses.

A bivariate bicycle code (examples/qec-bb/bb.py) is a pair A, B in R = GF(2)[x, y] /
(x^l - 1, y^m - 1), acting on GF(2)^(lm) in bb's convention: (A v)(i, j) = Σ v(i - p, j - q)
over the monomials x^p y^q of A, and A^T is multiplication by A* = A(x^-1, y^-1). The checks are
H_X = [A | B] and H_Z = [B^T | A^T], on n = 2lm qubits (the left block, then the right; position
(i, j) of a block is index i m + j). Since AB = BA, H_X H_Z^T = 0, and k = n - rank H_X -
rank H_Z (bb.k_linalg).

- **Definitions.** A Z-logical is a vector c with H_X c = 0 and c not in the rowspace of H_Z; an
  X-logical has H_Z c = 0 and c not in the rowspace of H_X. d_Z and d_X are their least weights,
  and the code's distance is d = min(d_X, d_Z). A code with k = 0 has no logicals, and no
  distance. Since the rowspace of H_Z is the orthogonal complement of ker H_Z, and ker H_Z is the
  rowspace of H_X plus the span of the X-logicals, a vector c in ker H_X is a Z-logical exactly
  when L·c = 1 for some vector L of a basis of the X-logicals modulo the rowspace of H_X
  (`logical_basis`); the integer program uses that test, and the enumeration the other one.
- **d_X = d_Z for every bivariate bicycle code.** Let P be the inversion of the torus,
  (P u)(i, j) = u(-i, -j), and Φ(u, v) = (P v, P u): swap the two blocks and invert both. In
  bb's convention P A P = A^T, since (P A P v)(i, j) = Σ (P v)(-i - p, -j - q) =
  Σ v(i + p, j + q) = (A^T v)(i, j), and likewise for B. So
  P H_X Φ (u, v) = P A P v + P B P u = B^T u + A^T v = H_Z (u, v), that is, H_Z = P H_X Φ.
  P is invertible and Φ is a symmetric involution, so ker H_Z = Φ ker H_X and the rowspace of
  H_Z is Φ applied to the rowspace of H_X. Φ therefore maps the Z-logicals onto the
  X-logicals, and it permutes coordinates, so it keeps weight: d_X = d_Z, and d = d_Z.
  `inversion_swap` builds P and Φ; the tests check H_Z = P H_X Φ entry by entry, and
  d_X = d_Z by computation.
- **What a result rests on.** An upper bound is certified: each comes with a witness, and
  `verify_witness` checks it with bb's bitmask rows and ranks (bb.rank_gf2), not with the numpy
  algebra the program is built from. A lower bound, and so optimality, rests on SCIP: its
  presolve (which turns the parity rows into its XOR constraints and adds its own symmetry
  handling), its branch and bound, its floating-point LP solver within its tolerances, and its
  conclusion that the objective is integral, all applied to the formulation in `distance_ilp`,
  whose soundness is argued there. SCIP 10.0 was found to be wrong on this formulation: its
  presolving of the XOR constraints cut off every optimal solution of some programs with fixed
  variables, and its "optimal" was then too high, with a witness that passes the check. The
  program therefore runs with XOR presolving and rapid learning off (SCIP_FIX, recorded in
  every result's settings; `distance_ilp` gives the fault and the evidence for the fix). The
  lower bound then rests on those two being the routes by which that presolving reaches the
  answer; the fault's place in SCIP's code was not found. It also rests on `logical_basis`
  (numpy elimination) being complete: with fewer than k logicals the program would miss some
  Z-logicals, and its optimum and dual bound could exceed d_Z. The program records the basis's
  size as k, and the study compares it with bb.k_linalg at run time. Nothing in the program
  certifies a lower bound independently. Where the enumeration is feasible (`distance_brute`,
  dim ker H_X at most BRUTE_CAP), it gives the exact value by a route that shares no code with
  the program but bb's matrices; where the search completes (`distance_search`, a C program),
  so does it, with integer arithmetic only, no LP and no floating point.
"""

from __future__ import annotations

import atexit
import functools
import math
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))

import bb  # noqa: E402

KINDS = ("Z", "X")
SEED = 0  # SCIP's randomization/randomseedshift
# Against SCIP 10.0's fault in presolving XOR constraints (distance_ilp's docstring): no XOR
# presolving in the main SCIP, and no rapid learning, whose sub-SCIP presolves with SCIP's
# defaults. Neither changes the program or its optimum.
SCIP_FIX = {"constraints/xor/maxprerounds": 0, "separating/rapidlearning/freq": -1}
# SCIP's limits/memory, in MB. It bounds SCIP's own estimate of its memory, which SCIP's
# parameter documentation says is lower than real use, not the process's RSS; 3000 leaves four
# runs at once a margin of about 3 GB below 15 GB for that difference.
MEMORY_MB = 3000
BRUTE_CAP = 28  # the largest dim ker H_X that distance_brute enumerates: 2^28 vectors, ~2 s
SEARCH_C = HERE / "search.c"
SEARCH_BOUND = 64  # the largest bound search.c accepts


# ---------------------------------------------------------------- the check matrices (numpy)


def multiplication(poly, ell: int, m: int) -> np.ndarray:
    """The lm x lm matrix of multiplication by poly over GF(2), in bb's convention: row (i, j)
    has a 1 in column (i - p, j - q) for each monomial x^p y^q. Repeated monomials cancel."""
    M = np.zeros((ell * m, ell * m), dtype=np.uint8)
    rows = np.arange(ell * m)
    i, j = rows // m, rows % m
    for p, q in poly:
        M[rows, ((i - p) % ell) * m + (j - q) % m] ^= 1
    return M


def check_matrices(A, B, ell: int, m: int) -> tuple[np.ndarray, np.ndarray]:
    """(H_X, H_Z) = ([A | B], [B^T | A^T]) as uint8 arrays of shape (lm, 2lm)."""
    a, b = multiplication(A, ell, m), multiplication(B, ell, m)
    return np.hstack([a, b]), np.hstack([b.T, a.T])


def inversion_swap(ell: int, m: int) -> tuple[np.ndarray, np.ndarray]:
    """(P, Φ): the torus's inversion (P u)(i, j) = u(-i, -j), lm x lm, and Φ(u, v) = (P v, P u),
    2lm x 2lm. H_Z = P H_X Φ (module docstring)."""
    lm = ell * m
    P = np.zeros((lm, lm), dtype=np.uint8)
    idx = np.arange(lm)
    P[idx, ((-(idx // m)) % ell) * m + (-(idx % m)) % m] = 1
    Phi = np.zeros((2 * lm, 2 * lm), dtype=np.uint8)
    Phi[:lm, lm:] = P
    Phi[lm:, :lm] = P
    return P, Phi


# ---------------------------------------------------------------- GF(2) linear algebra (numpy)


def rref(M: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """The reduced row echelon form of M over GF(2) (nonzero rows only) and its pivot columns."""
    M = (np.asarray(M) % 2).astype(np.uint8)
    pivots: list[int] = []
    r = 0
    for c in range(M.shape[1]):
        if r == M.shape[0]:
            break
        below = np.flatnonzero(M[r:, c])
        if not below.size:
            continue
        p = r + int(below[0])
        if p != r:
            M[[r, p]] = M[[p, r]]
        hit = np.flatnonzero(M[:, c])
        M[hit[hit != r]] ^= M[r]
        pivots.append(c)
        r += 1
    return M[:r], pivots


def rank(M: np.ndarray) -> int:
    return len(rref(M)[1])


def kernel(M: np.ndarray) -> np.ndarray:
    """A basis of {v : M v = 0} over GF(2), one vector per row."""
    R, pivots = rref(M)
    n, pivot_set = M.shape[1], set(pivots)
    free = [c for c in range(n) if c not in pivot_set]
    K = np.zeros((len(free), n), dtype=np.uint8)
    K[np.arange(len(free)), free] = 1
    if pivots:
        K[:, pivots] = R[:, free].T
    return K


def logical_basis(A, B, ell: int, m: int, kind: str) -> np.ndarray:
    """k vectors, one per row, whose classes form a basis of the logicals of the given kind:
    ker H_Z modulo the rowspace of H_X for kind "X", ker H_X modulo the rowspace of H_Z for "Z".
    A kernel vector is kept when it is not in the span of the stabilizers and the vectors kept
    before it, and is stored reduced against them (still a logical of that kind)."""
    if kind not in KINDS:
        raise ValueError(kind)
    hx, hz = check_matrices(A, B, ell, m)
    of, stabilizers = (hz, hx) if kind == "X" else (hx, hz)
    R, pivots = rref(stabilizers)
    rows, pivots, out = list(R), list(pivots), []
    for v in kernel(of):
        w = v.copy()
        for p, row in zip(pivots, rows, strict=True):
            if w[p]:
                w ^= row
        if w.any():
            rows.append(w)
            pivots.append(int(np.flatnonzero(w)[0]))
            out.append(w)
    return np.array(out, dtype=np.uint8).reshape(len(out), of.shape[1])


# ---------------------------------------------------------------- the integer program (SCIP)


def scip_version() -> str:
    from pyscipopt import Model

    return f"SCIP {Model().version()} (pyscipopt {_pyscipopt_version()})"


def _pyscipopt_version() -> str:
    import pyscipopt

    return pyscipopt.__version__


def _non_default(model) -> dict:
    from pyscipopt import Model

    default = Model().getParams()
    return {k: v for k, v in sorted(model.getParams().items()) if default.get(k) != v}


def distance_ilp(
    A,
    B,
    ell: int,
    m: int,
    kind: str = "Z",
    time_limit: float = 600.0,
    memory_mb: float = MEMORY_MB,
    seed: int = SEED,
    translation: bool = True,
    configure=None,
    scip_fix: bool = True,
) -> dict:
    """The least weight of a logical of the given kind ("Z": H_X c = 0, c not in the rowspace
    of H_Z; "X": the same with H_X and H_Z exchanged), by one integer program solved by SCIP.

    The program, for kind Z (kind X exchanges H_X and H_Z): binary c_1..c_n; for each row h of
    H_X, h·c = 2 s_h with s_h an integer in [0, |h|/2]; for each vector L of
    logical_basis(..., "X"), L·c = 2 t_L + z_L with t_L an integer and z_L binary; Σ z_L >= 1;
    and, with `translation`, c_(0,0) + c_(lm + (0,0)) >= 1. Minimise Σ c. The parity rows say
    H_X c = 0 and the z's say L·c = 1 for some L, which for c in ker H_X is exactly "c is not in
    the rowspace of H_Z" (module docstring). So without the translation row, the optimum is d_Z.

    The translation row keeps the optimum. For g = x^a y^b, let T_g shift both blocks by g,
    T_g(u, v) = (g u, g v). R is commutative, so g commutes with A, B, A* and B*:
    H_X T_g (u, v) = g (A u + B v) = g H_X (u, v), and T_g (B w, A w) = (B g w, A g w). So T_g
    maps ker H_X into itself, and the rowspace of H_Z, {(B w, A w)}, into itself; being
    invertible, onto both. It therefore maps Z-logicals to Z-logicals, and it permutes
    coordinates, so it keeps weight. If c is a least-weight Z-logical and (i, j) is in the support
    of either block, T_g with g = x^-i y^-j moves that position to (0, 0): a least-weight
    Z-logical satisfying the row. The constrained optimum is therefore d_Z, and a lower bound for
    the constrained program is a lower bound for d_Z. (For kind X the same holds with A* and B*.)

    SCIP's fault, and the settings against it. SCIP's presolve turns the parity rows into its XOR
    constraints, and in SCIP 10.0 their presolving can cut off every optimal solution of a program
    in which some variables are already fixed, or declare it infeasible. SCIP makes such fixings
    itself (reduced-cost fixing, once a heuristic has found a solution), and the wrong conclusion
    reaches the answer by two routes: rapid learning, which solves a copy of the program in a
    sub-SCIP whose presolving it first resets to SCIP's defaults, and passes back a dual bound,
    conflicts or bound changes; and the main SCIP's own presolve after a restart. The registered
    test (examples/qec-distance) met it on a 4 x 5 code with d_X = 2: d_X = 3, status optimal, at
    seeds 0, 2 and 4. A hunt over 2,476 development codes (n = 8 to 50, both kinds, seeds 0 to 19)
    then found 292 wrong optima in 99,040 runs, on 48 (code, kind) programs of 37 codes, every one
    too high, by 1 or 2, at d from 2 to 4 (the range that hunt met, not a bound: a later one, over
    2,058 development codes with n = 8 to 156, found the defaults wrong at d = 5 too), and every one
    with a witness that passes verify_witness: only the lower bound was wrong. With `scip_fix` (the
    default) the program runs with SCIP_FIX, XOR presolving off (constraints/xor/maxprerounds 0) and
    rapid learning off (separating/rapidlearning/freq -1), both recorded in the settings. Neither
    changes the program. Under them the 48 programs and the 4 x 5 code gave the right d at every
    seed from 0 to 19 (1,000 runs), the whole hunt gave no wrong answer at seeds 0 to 9 (49,520
    runs), and 16 runs at d = 12 to 16 took 2,359 s in all against the defaults' 2,968 s (single
    runs on a shared machine). Turning off SCIP's dual reductions, the fix first proposed, gave the
    right d on those programs but not on one of 2,760 variants with further fixings, and about
    doubled the time. The XOR constraints and their propagation stay. In SCIP's source the XOR
    handler's presolving routines (applyFixings, and its pairwise, hash and clique presolving) run
    only in presolving. Its propagation stays on, the Gauss propagator among it
    (constraints/xor/gausspropfreq 5), which runs from propagation, reads the current fixings, fixes
    variables and can cut off a node; it was tested under stress: on 119 programs (those of the
    hunt's failures and of high k) with 30 variants each that fix further variables, SCIP_FIX gave
    no wrong answer in 10,710 solves, with the Gauss propagator or without it, where the defaults
    gave 23, and the later hunts' 33,682 runs under SCIP_FIX gave none. That the two routes are the
    only ones rests on reading SCIP's source (its other sub-SCIPs presolve nothing, or only propose
    solutions, which the main SCIP checks); the faulty statement itself was not found.
    scip_fix=False gives SCIP's defaults, the registered test's settings.

    Returns a dict: k (the number of logicals logical_basis found: the program is sound only if
    it is the code's k); status (SCIP's: "optimal", "timelimit", "memlimit", ..., or
    "no_logicals" when k = 0); d (the optimum, when optimal); upper (the best solution's weight,
    None if none was found) and lower (SCIP's dual bound less 1e-4, rounded up, the objective
    being integral: the slack absorbs a dual bound a rounding error above an integer, such as
    8.000000000000002, and can only weaken the bound, by one, for a dual bound less than 1e-4
    above an integer);
    witness (the best solution's support: a least-weight logical when optimal); seconds (wall
    clock, building the program included); nodes; the SCIP version; seed; scip_fix; the
    parameters set here (settings, SCIP_FIX among them); and every parameter that differs from
    SCIP's defaults (parameters). SCIP's time limit is wall clock (timing/clocktype 2). SCIP runs
    on one thread, its randomness comes from the fixed seed (randomization/randomseedshift), and
    a run with the same inputs and parameters is deterministic up to where a limit stops it.
    `configure`, if given, is called with the SCIP model before solving (for development;
    whatever it changes is recorded in parameters, not in settings).
    """
    from pyscipopt import Model, quicksum

    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    hx, hz = check_matrices(A, B, ell, m)
    checks = hx if kind == "Z" else hz
    detectors = logical_basis(A, B, ell, m, "X" if kind == "Z" else "Z")
    n, lm = 2 * ell * m, ell * m
    model = Model(f"distance-{kind}")
    model.hideOutput()
    settings = {"limits/time": float(time_limit), "limits/memory": float(memory_mb),
                "timing/clocktype": 2, "randomization/randomseedshift": int(seed),
                **(SCIP_FIX if scip_fix else {})}  # fmt: skip
    for name, value in settings.items():
        model.setParam(name, value)
    if configure is not None:
        configure(model)
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": len(detectors), "time_limit": time_limit,
           "memory_mb": memory_mb, "seed": seed, "translation": translation,
           "scip_fix": scip_fix, "solver": scip_version(), "settings": settings,
           "parameters": _non_default(model)}  # fmt: skip
    if not len(detectors):
        return {**out, "status": "no_logicals", "d": None, "upper": None, "lower": None,
                "dual_bound": None, "witness": None, "nodes": 0, "solving_seconds": 0.0,
                "seconds": round(time.time() - start, 3)}  # fmt: skip
    c = [model.addVar(f"c{i}", vtype="B") for i in range(n)]
    for r, row in enumerate(checks):
        support = np.flatnonzero(row).tolist()
        s = model.addVar(f"s{r}", vtype="I", lb=0, ub=len(support) // 2)
        model.addCons(quicksum(c[i] for i in support) == 2 * s)
    zs = []
    for j, row in enumerate(detectors):
        support = np.flatnonzero(row).tolist()
        t = model.addVar(f"t{j}", vtype="I", lb=0, ub=len(support) // 2)
        z = model.addVar(f"z{j}", vtype="B")
        model.addCons(quicksum(c[i] for i in support) == 2 * t + z)
        zs.append(z)
    model.addCons(quicksum(zs) >= 1)
    if translation:
        model.addCons(c[0] + c[lm] >= 1)
    model.setObjective(quicksum(c), "minimize")
    model.optimize()
    status = model.getStatus()
    witness = upper = None
    if model.getNSols():
        best = model.getBestSol()
        witness = [i for i in range(n) if model.getSolVal(best, c[i]) > 0.5]
        upper = len(witness)
    dual = model.getDualbound()
    lower = max(1, math.ceil(dual - 1e-4)) if math.isfinite(dual) and dual < 1e19 else None
    if status == "optimal":
        lower = upper
    return {**out, "status": status, "d": upper if status == "optimal" else None,
            "upper": upper, "lower": lower, "dual_bound": dual, "witness": witness,
            "nodes": model.getNTotalNodes(), "solving_seconds": round(model.getSolvingTime(), 3),
            "seconds": round(time.time() - start, 3)}  # fmt: skip


# ---------------------------------------------------------------- independent checks (bitmasks)


def _bit_rows(A, B, ell: int, m: int) -> tuple[list[int], list[int]]:
    """H_X and H_Z as bb builds them in k_linalg: one int per row, bit t for qubit t."""
    lm = ell * m
    a_rows, b_rows = bb._matrix_rows(A, ell, m), bb._matrix_rows(B, ell, m)
    a_cols, b_cols = bb._matrix_rows(A, ell, m, True), bb._matrix_rows(B, ell, m, True)
    hx = [a | (b << lm) for a, b in zip(a_rows, b_rows, strict=True)]
    hz = [b | (a << lm) for a, b in zip(a_cols, b_cols, strict=True)]
    return hx, hz


def verify_witness(A, B, ell: int, m: int, kind: str, support) -> dict:
    """Check, with bb's bitmask rows and bb.rank_gf2 only, that the vector with this support is
    a logical of the given kind: for Z, every row of H_X meets it evenly, and adding it to the
    rows of H_Z raises their rank (it is not in their span); for X, the same with H_X and H_Z
    exchanged. A support that passes certifies its weight as an upper bound on d of that kind."""
    if kind not in KINDS:
        raise ValueError(kind)
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    support = [int(i) for i in support]
    valid = len(set(support)) == len(support) and all(0 <= i < 2 * ell * m for i in support)
    c = sum(1 << i for i in set(support))
    in_kernel = all((row & c).bit_count() % 2 == 0 for row in checks)
    nontrivial = bb.rank_gf2([*stabilizers, c]) > bb.rank_gf2(stabilizers)
    return {"weight": len(set(support)), "valid_support": valid, "in_kernel": in_kernel,
            "nontrivial": nontrivial, "logical": valid and in_kernel and nontrivial}  # fmt: skip


def _kernel_bits(rows: list[int], n: int) -> list[int]:
    """A basis of {v : r·v = 0 for every row r}, by elimination on int bitmasks."""
    pivots: dict[int, int] = {}
    for r in rows:
        for p, prow in pivots.items():
            if r >> p & 1:
                r ^= prow
        if r:
            p = r.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= r
            pivots[p] = r
    return [(1 << f) | sum(1 << p for p, prow in pivots.items() if prow >> f & 1)
            for f in range(n) if f not in pivots]  # fmt: skip


def _words(x: int, count: int) -> list[int]:
    return [(x >> (64 * w)) & ((1 << 64) - 1) for w in range(count)]


def distance_brute(A, B, ell: int, m: int, kind: str = "Z", cap: int = BRUTE_CAP) -> dict:
    """The least weight of a logical of the given kind, by enumerating all of ker H_X (kind Z;
    ker H_Z for X). It shares nothing with distance_ilp but bb's matrices: bases of ker H_X and
    ker H_Z by elimination on bb's bitmask rows, and the test that c in ker H_X is outside the
    rowspace of H_Z exactly when z·c = 1 for some z in a basis of ker H_Z (the rowspace being
    ker H_Z's orthogonal complement). The 2^dim vectors are formed by XOR in numpy, as a table of
    all combinations of the first (up to 16) basis vectors, shifted by each combination of the
    rest. Refuses (ValueError) when dim exceeds `cap`. d is None when no vector is a logical
    (k = 0)."""
    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    n = 2 * ell * m
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    basis = _kernel_bits(checks, n)
    dual = _kernel_bits(stabilizers, n)
    dim = len(basis)
    if dim > cap:
        raise ValueError(f"dim ker = {dim} exceeds the enumeration cap {cap}")
    syndromes = [sum(((c & z).bit_count() & 1) << j for j, z in enumerate(dual)) for c in basis]
    wv, ws = (n + 63) // 64, max(1, (len(dual) + 63) // 64)
    vec = np.array([_words(c, wv) for c in basis], dtype=np.uint64).reshape(dim, wv)
    syn = np.array([_words(s, ws) for s in syndromes], dtype=np.uint64).reshape(dim, ws)
    low = min(dim, 16)
    tv = np.zeros((1 << low, wv), dtype=np.uint64)
    ts = np.zeros((1 << low, ws), dtype=np.uint64)
    for i in range(low):
        h = 1 << i
        tv[h : 2 * h] = tv[:h] ^ vec[i]
        ts[h : 2 * h] = ts[:h] ^ syn[i]
    weights = np.bitwise_count(tv).sum(axis=1, dtype=np.int64)
    best, witness = None, None
    hv, hs = np.zeros(wv, dtype=np.uint64), np.zeros(ws, dtype=np.uint64)
    for step in range(1 << (dim - low)):
        if step:  # Gray code over the remaining basis vectors: flip one per step
            flip = low + (step & -step).bit_length() - 1
            hv, hs = hv ^ vec[flip], hs ^ syn[flip]
        nontrivial = (ts ^ hs).any(axis=1)
        if not nontrivial.any():
            continue
        w = np.bitwise_count(tv ^ hv).sum(axis=1, dtype=np.int64) if step else weights
        w = np.where(nontrivial, w, n + 1)
        i = int(np.argmin(w))
        if best is None or w[i] < best:
            best = int(w[i])
            bits = _join(tv[i] ^ hv)
            witness = [t for t in range(n) if bits >> t & 1]
    return {"kind": kind, "d": best, "witness": witness, "dim": dim, "vectors": 1 << dim,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


def _join(words: np.ndarray) -> int:
    return sum(int(w) << (64 * i) for i, w in enumerate(words))


# ---------------------------------------------------------------- the search (C, bitmasks)


def _logicals_bits(of: list[int], stabilizers: list[int], n: int) -> list[int]:
    """A basis of ker(of) modulo the span of `stabilizers`, by elimination on int bitmasks: each
    kernel vector is reduced by leading bits against the stabilizers and the vectors kept before
    it, and kept, reduced, when something remains. Shares no code with logical_basis."""
    basis: dict[int, int] = {}

    def add(v: int) -> int:
        while v:
            p = v.bit_length() - 1
            if p not in basis:
                basis[p] = v
                return v
            v ^= basis[p]
        return 0

    for row in stabilizers:
        add(row)
    return [w for w in map(add, _kernel_bits(of, n)) if w]


@functools.cache
def _search_binary() -> tuple[str, str]:
    """search.c compiled with the system's cc into a temporary directory (removed when the
    process exits), once per process; and the compiler's version line."""
    directory = Path(tempfile.mkdtemp(prefix="qec-search-"))
    atexit.register(shutil.rmtree, directory, True)
    binary = directory / "search"
    subprocess.run(["cc", "-O2", "-o", str(binary), str(SEARCH_C)], check=True, capture_output=True)
    version = subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout
    return str(binary), version.splitlines()[0] if version else "cc"


def distance_search(
    A,
    B,
    ell: int,
    m: int,
    kind: str = "Z",
    bound: int = SEARCH_BOUND,
    anchors=None,
    time_limit: float = 1200.0,
    deepen: bool = True,
) -> dict:
    """The least weight of a logical of the given kind, if it is below `bound`, by an exhaustive
    check-driven search (search.c) whose bound is raised one at a time. It shares nothing with
    distance_ilp but bb's matrices: the checks are bb's bitmask rows, a vector c with H_X c = 0
    (kind Z) is nontrivial exactly when L·c = 1 for some L of a basis of the X-logicals modulo the
    rowspace of H_X found by bitmask elimination (`_logicals_bits`, whose size must be
    bb.k_linalg), and the search uses integer arithmetic only. For kind X, H_X and H_Z exchange.

    A pass with bound b. For each anchor a it grows a set S from {a}: while S has a nonzero
    syndrome it branches over the qubits above a of one unsatisfied check, each branch excluding
    the earlier ones; a set with zero syndrome is a leaf, kept when nontrivial and lighter than
    the best so far (b at the start); a branch stops when |S| + ceil(u / maxcol) reaches the best
    so far (u unsatisfied checks, each qubit in at most maxcol checks). Every leaf kept is a
    logical, so the best is an upper bound with its witness. The pass is exhaustive below b: let
    c be a least-weight logical, of weight w < b, whose least qubit is an anchor a. Some branch
    keeps S inside the support of c and its excluded qubits outside it, since c meets each check
    evenly and so meets the chosen unsatisfied one outside S, above a; the first such qubit in the
    check is a branch with that property. Its syndrome becomes zero only at S = c: an S strictly
    inside c with zero syndrome would make S and c + S codewords lighter than c, one of them
    nontrivial. It is not cut while the best exceeds w, since the qubits of c outside S must clear
    the u unsatisfied checks, so |S| + ceil(u / maxcol) <= w. So a pass keeps a leaf whenever
    some logical is lighter than b (c itself, if it keeps none before), and one that runs to its
    end ends with the best at w. A pass that keeps no leaf shows that no logical is lighter
    than b.

    The passes. Write d for the least weight of a logical of the kind. With `deepen` (the
    default) the passes run with b = 2, 3, ..., `bound` in turn, and the search stops at its
    first leaf kept. Pass b runs only after pass b - 1 kept none, so d >= b - 1 (d >= 1 before
    pass 2: a logical is nonzero). If d >= b, pass b keeps no leaf (each would be a logical
    lighter than b), and ends having shown d >= b. If d < b, then d = b - 1, and pass b keeps a
    leaf, whose weight w has b - 1 <= d <= w < b: w = d. So the first logical found has weight
    exactly d, and the passes before it show that nothing is lighter. A time-out stops a pass,
    not the argument: each pass that ended without a leaf still shows d >= its b, so the largest
    such b is a lower bound. Without `deepen` there is one pass, with b = `bound`, which runs to
    its end (unless it keeps a leaf of weight 1, which nothing can be lighter than): the search
    that study.py registered, which reaches d by lowering its bound from `bound` to each leaf
    kept, and so can go very deep before it meets a logical.

    `anchors`: None searches from every qubit, so every logical has its least qubit among them.
    (0, lm) is enough too, by distance_ilp's translation argument: a least-weight logical moved
    to contain qubit 0, if it meets the left block, has least qubit 0; one in the right block
    alone, moved to contain lm, has least qubit lm. The second rests on that argument, the first
    on nothing but the search.

    Returns a dict: status ("complete", "timelimit" when stopped after `time_limit` seconds of
    wall clock, or "no_logicals" when k = 0); d (exact, when complete and below the bound);
    lower (d; or the bound, when complete with nothing below it; at a time-out the largest b of
    a pass that ended without a leaf, None if there is none); upper and witness (the lightest
    logical found, None if none); nodes (of every pass, when complete); passes (for each pass
    that ended without a leaf, in order: its bound, nodes and seconds); deepen; k; bound;
    anchors; seconds; and the compiler. Requires a C compiler as `cc`."""
    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    n = 2 * ell * m
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    labels = _logicals_bits(stabilizers, checks, n)
    if len(labels) != bb.k_linalg(A, B, ell, m):
        raise RuntimeError(f"{len(labels)} logicals found, but k = {bb.k_linalg(A, B, ell, m)}")
    starts = list(range(n)) if anchors is None else [int(a) for a in anchors]
    binary, compiler = _search_binary()
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": len(labels), "bound": bound,
           "deepen": deepen, "anchors": "all" if anchors is None else starts,
           "time_limit": time_limit, "compiler": compiler}  # fmt: skip
    if not labels:
        return {**out, "status": "no_logicals", "d": None, "lower": None, "upper": None,
                "witness": None, "nodes": 0, "passes": [],
                "seconds": round(time.time() - start, 3)}  # fmt: skip
    if not 1 <= bound <= SEARCH_BOUND or len(labels) > 128 or n > 2048 or len(checks) > 1024:
        raise ValueError("beyond search.c's limits")
    first = min(2, bound) if deepen else bound
    header = f"{n} {len(checks)} {len(labels)} {first} {bound} {len(starts)}"
    lines = [header, " ".join(map(str, starts))]
    for row in checks:
        support = [t for t in range(n) if row >> t & 1]
        lines.append(" ".join(map(str, [len(support), *support])))
    for t in range(n):
        x = sum((v >> t & 1) << j for j, v in enumerate(labels))
        lines.append(f"{x & (2**64 - 1):x} {x >> 64:x}")
    proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)  # fmt: skip
    try:
        stdout, stderr = proc.communicate("\n".join(lines) + "\n", timeout=time_limit)
        status = "complete"
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        status = "timelimit"
    if status == "complete" and proc.returncode:
        raise RuntimeError(f"search.c failed: {stderr.strip()}")
    witness, nodes, passes = None, None, []
    for words in map(str.split, stdout.splitlines()):
        if words[:1] == ["best"] and len(words) >= 2 and len(words) == int(words[1]) + 2:
            witness = [int(q) for q in words[2:]]
        elif words[:1] == ["pass"] and len(words) == 4:
            b, count, ms = map(int, words[1:])
            passes.append({"bound": b, "nodes": count, "seconds": ms / 1000})
        elif words[:1] == ["done"] and len(words) == 2:
            nodes = int(words[1])
    if status == "complete" and nodes is None:
        raise RuntimeError("search.c ended without finishing")
    upper = len(witness) if witness else None
    proven = passes[-1]["bound"] if passes else None
    if upper is not None and proven is not None and upper < proven:
        raise RuntimeError(f"search.c found weight {upper} after a pass with bound {proven}")
    if status == "complete" and upper is None and proven != bound:
        raise RuntimeError(f"search.c ended without a pass at its bound {bound}")
    exact = status == "complete" and upper is not None
    if status == "complete":
        lower = upper if exact else bound
    else:
        lower = proven
    return {**out, "status": status, "d": upper if exact else None, "lower": lower,
            "upper": upper, "witness": witness, "nodes": nodes, "passes": passes,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


# ---------------------------------------------------------------- tori


def torus_type(ell: int, m: int) -> tuple[int, ...]:
    """The isomorphism type of Z_l x Z_m: its prime-power cyclic factors, sorted. Codes on
    isomorphic tori correspond under the isomorphism (it carries the group ring along), so a
    held-out size excludes every size of the same type, not only (l, m) and (m, l). The converse
    does not hold: codes on non-isomorphic groups of the same order can in principle be
    equivalent under a permutation of qubits, so a different type alone does not show that two
    codes differ. n and k are invariants of that equivalence, and the study's development record
    (study.py, EXCLUDED_SEEN) uses them."""
    out = []
    for n in (ell, m):
        p = 2
        while n > 1:
            if n % p == 0:
                q = 1
                while n % p == 0:
                    n //= p
                    q *= p
                out.append(q)
            p += 1
    return tuple(sorted(out))
