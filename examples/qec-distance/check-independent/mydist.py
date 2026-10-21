"""
An independent checker's distance computation for bivariate bicycle codes (scratch, not part of
the study). Written without reading the builder's distance.py.

Definitions. The l x m torus G = Z_l x Z_m; group element (i, j) is index i*m + j. A polynomial
is a list of exponent pairs (p, q); repeats cancel mod 2 after reduction mod (l, m). The matrix
of multiplication by A has entry [(i, j), (i - p, j - q)] += 1 for each monomial, so
(A v)(g) = sum_{h in A} v(g - h). H_X = [A | B], H_Z = [B^T | A^T], n = 2lm.

For a pair (Hc, Hs) with Hc Hs^T = 0, the distance is min |c| over c in ker Hc minus rowspace Hs.
kind "Z": (Hc, Hs) = (H_X, H_Z) (Z-type logicals); kind "X": (H_Z, H_X).

Exact methods here:
- brute: enumerate all of ker Hc (split tables, numpy popcount). Nontriviality by k-bit labels
  c . L_j with L_j a basis of ker Hs modulo rowspace Hc.
- dfs: a check-driven exhaustive search. For every anchor qubit a (as the lowest index of the
  support), grow S from {a}: while the syndrome is nonzero, pick an unsatisfied check r; any
  codeword containing S meets r outside S, so branch over r's qubits (> a, not excluded),
  excluding earlier siblings. Prune by |S| + ceil(unsat / maxcol) >= best. A zero-syndrome S is
  a leaf (a min-weight nontrivial codeword contains no nonzero codeword as a proper subset that is
  trivial, and nontrivial S is recorded). No LP, no translation symmetry.
- highs / scip: one ILP per logical L_j: min sum c, Hc c = 2 s, L_j c = 2 t + 1, with the
  incumbent as a cutoff, no symmetry-breaking row.
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "qec-bb"))

import bb  # noqa: E402

# Group orders of published tori (n/2), and abelian-group types of the study's method sizes.
PUBLISHED_ORDERS = {15, 21, 35, 36, 45, 54, 63, 72, 144}
METHOD_SIZES = [(3, 4), (2, 8), (3, 6), (4, 5), (2, 10), (3, 8), (4, 6), (5, 5)]


def group_type(ell, m):
    """Invariant factors as the sorted list of prime-power factors of Z_l x Z_m."""
    out = []
    for n in (ell, m):
        x, p = n, 2
        while x > 1:
            if x % p == 0:
                e = 1
                while x % p == 0:
                    x //= p
                    e *= p
                out.append(e)
            p += 1
    return sorted(out)


METHOD_TYPES = {tuple(group_type(a, b)) for a, b in METHOD_SIZES}


def is_toric(A, B, ell, m):
    return sorted(bb._monomials(A, ell, m)) == sorted(bb._monomials([(0, 0), (1, 0)], ell, m)) \
        and sorted(bb._monomials(B, ell, m)) == sorted(bb._monomials([(0, 0), (0, 1)], ell, m))


def guard(A, B, ell, m):
    """Refuse a distance computation the test's rules forbid."""
    if is_toric(A, B, ell, m):
        return
    if ell * m in PUBLISHED_ORDERS:
        raise RuntimeError(f"forbidden: non-toric code at order {ell * m} ({ell}x{m})")
    if tuple(group_type(ell, m)) in METHOD_TYPES:
        raise RuntimeError(f"avoid: non-toric code on a method-size torus type ({ell}x{m})")


# ------------------------------------------------------------------ matrices


def mult(poly, ell, m):
    M = np.zeros((ell * m, ell * m), dtype=np.uint8)
    for i in range(ell):
        for j in range(m):
            for p, q in poly:
                M[i * m + j, ((i - p) % ell) * m + (j - q) % m] ^= 1
    return M


def checks(A, B, ell, m):
    a, b = mult(A, ell, m), mult(B, ell, m)
    return np.hstack([a, b]), np.hstack([b.T, a.T])


# ------------------------------------------------------------------ GF(2)


def rref(M):
    M = (np.array(M, dtype=np.uint8) & 1).copy()
    rows, cols = M.shape
    piv = []
    r = 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0:
            continue
        p = r + nz[0]
        if p != r:
            M[[r, p]] = M[[p, r]]
        others = np.nonzero(M[:, c])[0]
        others = others[others != r]
        M[others] ^= M[r]
        piv.append(c)
        r += 1
    return M[:r], piv


def rank(M):
    return len(rref(M)[1])


def kernel(M):
    R, piv = rref(M)
    n = M.shape[1]
    free = [c for c in range(n) if c not in set(piv)]
    K = np.zeros((len(free), n), dtype=np.uint8)
    for t, f in enumerate(free):
        K[t, f] = 1
        for i, p in enumerate(piv):
            K[t, p] = R[i, f]
    return K


def logical_reps(Hc, Hs):
    """A basis of ker Hs modulo rowspace Hc: vectors L_j with c in ker Hc trivial (in rowspace
    Hs) iff c . L_j = 0 for all j."""
    base = rref(Hc)[0]
    r0 = base.shape[0]
    cur = base.copy()
    out = []
    for v in kernel(Hs):
        trial = np.vstack([cur, v[None, :]])
        if rank(trial) > cur.shape[0]:
            cur = trial
            out.append(v)
    L = np.array(out, dtype=np.uint8).reshape(-1, Hc.shape[1])
    assert rank(np.vstack([base, L])) == r0 + len(out)
    return L


def pair(kind, A, B, ell, m):
    hx, hz = checks(A, B, ell, m)
    return (hx, hz) if kind == "Z" else (hz, hx)


def nontrivial(c, Hc, Hs):
    """c in ker Hc and not in rowspace Hs, by rank (independent of the labels)."""
    c = np.asarray(c, dtype=np.uint8)
    if np.any((Hc.astype(np.int64) @ c) % 2):
        return False
    return rank(np.vstack([Hs, c[None, :]])) > rank(Hs)


# ------------------------------------------------------------------ brute force


def _pack(V):
    n = V.shape[1]
    W = (n + 63) // 64
    out = np.zeros((V.shape[0], W), dtype=np.uint64)
    for i, v in enumerate(V):
        x = 0
        for q in np.nonzero(v)[0]:
            x |= 1 << int(q)
        for w in range(W):
            out[i, w] = (x >> (64 * w)) & ((1 << 64) - 1)
    return out


def _span_table(P, labs):
    T = np.zeros((1, P.shape[1]), dtype=np.uint64)
    Lb = np.zeros(1, dtype=np.int64)
    for v, lb in zip(P, labs, strict=True):
        T = np.vstack([T, T ^ v[None, :]])
        Lb = np.concatenate([Lb, Lb ^ lb])
    return T, Lb


def distance_brute(Hc, Hs, cap=30):
    L = logical_reps(Hc, Hs)
    if len(L) == 0:
        return None
    K = kernel(Hc)
    D = K.shape[0]
    if D > cap:
        raise ValueError(f"dim {D} > cap {cap}")
    labs = [int(sum(int(x) << j for j, x in enumerate((L.astype(np.int64) @ v) % 2))) for v in K]
    P = _pack(K)
    d1 = min(D, 16)
    T1, L1 = _span_table(P[:d1], labs[:d1])
    T2, L2 = _span_table(P[d1:], labs[d1:])
    best = None
    for t2, l2 in zip(T2, L2, strict=True):
        w = np.bitwise_count(T1 ^ t2[None, :]).sum(axis=1)
        mask = (L1 ^ l2) != 0
        if mask.any():
            x = int(w[mask].min())
            best = x if best is None else min(best, x)
    return best


# ------------------------------------------------------------------ check-driven search


def distance_dfs(Hc, Hs, ub, time_limit=None):
    """Exact: min weight of a nontrivial codeword if < ub, else ub (no nontrivial codeword of
    weight < ub). Returns (value, found_vector_or_None, nodes, complete)."""
    L = logical_reps(Hc, Hs)
    n = Hc.shape[1]
    rows = [list(np.nonzero(r)[0]) for r in Hc]
    rows = [[int(q) for q in r] for r in rows]
    colmask = [0] * n
    for ri, r in enumerate(rows):
        for q in r:
            colmask[q] |= 1 << ri
    maxcol = max(bin(x).count("1") for x in colmask) or 1
    label = [int(sum(int(L[j, q]) << j for j in range(len(L)))) for q in range(n)]
    best = [ub, None]
    nodes = [0]
    t0 = time.time()

    sys.setrecursionlimit(10000)

    def rec(a, S, syn, lab, excl):
        nodes[0] += 1
        if time_limit and nodes[0] % 4096 == 0 and time.time() - t0 > time_limit:
            raise TimeoutError
        size = len(S)
        if syn == 0:
            if lab != 0 and size < best[0]:
                best[0], best[1] = size, list(S)
            return
        u = syn.bit_count()
        if size + -(-u // maxcol) >= best[0]:
            return
        r = (syn & -syn).bit_length() - 1
        opts = [q for q in rows[r] if q > a and not (excl >> q) & 1]
        for q in opts:
            S.append(q)
            rec(a, S, syn ^ colmask[q], lab ^ label[q], excl | (1 << q))
            S.pop()
            excl |= 1 << q

    complete = True
    try:
        for a in range(n):
            rec(a, [a], colmask[a], label[a], 1 << a)
    except TimeoutError:
        complete = False
    return best[0], best[1], nodes[0], complete


# ------------------------------------------------------------------ ILPs, one per logical


def distance_highs(Hc, Hs, time_limit=600):
    from scipy.optimize import Bounds, LinearConstraint, milp

    L = logical_reps(Hc, Hs)
    if len(L) == 0:
        return None, "no_logicals"
    n, r = Hc.shape[1], Hc.shape[0]
    best, wit = n + 1, None
    t0 = time.time()
    for j in range(len(L)):
        # variables: c (n), s (r), t (1)
        nv = n + r + 1
        rw = Hc.sum(axis=1).astype(int)
        lw = int(L[j].sum())
        Aeq = np.zeros((r + 1, nv))
        Aeq[:r, :n] = Hc
        Aeq[:r, n : n + r] = -2 * np.eye(r)
        Aeq[r, :n] = L[j]
        Aeq[r, n + r] = -2
        lo = np.concatenate([np.zeros(r), [1]])
        cons = [LinearConstraint(Aeq, lo, lo)]
        obj_row = np.zeros((1, nv))
        obj_row[0, :n] = 1
        cons.append(LinearConstraint(obj_row, 0, best - 1))
        ub = np.concatenate([np.ones(n), rw // 2, [max(0, (lw - 1) // 2)]])
        cost = np.zeros(nv)
        cost[:n] = 1
        rem = time_limit - (time.time() - t0)
        if rem <= 0:
            return None, "timeout"
        res = milp(
            cost,
            constraints=cons,
            integrality=np.ones(nv),
            bounds=Bounds(np.zeros(nv), ub),
            options={"mip_rel_gap": 0, "time_limit": rem},
        )
        if res.status == 2:  # infeasible: no nontrivial c with L_j odd lighter than best
            continue
        if res.status != 0:
            return None, f"status {res.status}: {res.message}"
        c = np.round(res.x[:n]).astype(np.uint8)
        w = int(c.sum())
        assert w < best and nontrivial(c, Hc, Hs), (w, best)
        best, wit = w, c
    return best, wit


def distance_scip(Hc, Hs, time_limit=600, symmetry=True, seed=0):
    from pyscipopt import Model, quicksum

    L = logical_reps(Hc, Hs)
    if len(L) == 0:
        return None, "no_logicals"
    n = Hc.shape[1]
    best, wit = n + 1, None
    t0 = time.time()
    for j in range(len(L)):
        mdl = Model()
        mdl.hideOutput()
        mdl.setParam("randomization/randomseedshift", seed)
        if not symmetry:
            mdl.setParam("misc/usesymmetry", 0)
        rem = time_limit - (time.time() - t0)
        if rem <= 0:
            return None, "timeout"
        mdl.setParam("limits/time", rem)
        c = [mdl.addVar(vtype="B") for _ in range(n)]
        for row in Hc:
            sup = [int(q) for q in np.nonzero(row)[0]]
            s = mdl.addVar(vtype="I", lb=0, ub=len(sup) // 2)
            mdl.addCons(quicksum(c[q] for q in sup) == 2 * s)
        sup = [int(q) for q in np.nonzero(L[j])[0]]
        t = mdl.addVar(vtype="I", lb=0, ub=max(0, (len(sup) - 1) // 2))
        mdl.addCons(quicksum(c[q] for q in sup) == 2 * t + 1)
        mdl.addCons(quicksum(c) <= best - 1)
        mdl.setObjective(quicksum(c), "minimize")
        mdl.optimize()
        st = mdl.getStatus()
        if st == "infeasible":
            continue
        if st != "optimal":
            return None, st
        x = np.array([round(mdl.getVal(v)) for v in c], dtype=np.uint8)
        w = int(x.sum())
        assert w < best and nontrivial(x, Hc, Hs), (w, best)
        best, wit = w, x
    return best, wit


def k_of(A, B, ell, m):
    hx, hz = checks(A, B, ell, m)
    return 2 * ell * m - rank(hx) - rank(hz)


def mindeg(ell, m):
    return min(ell, m)


def toric(ell, m):
    return [(0, 0), (1, 0)], [(0, 0), (0, 1)]


if __name__ == "__main__":
    print(math.pi)


# ------------------------------------------------------------------ the C search


def dfs_c(Hc, Hs, ub, procs=1, timeout=1100):
    """distance_dfs in C (dfs.c), anchors split over `procs` processes. Returns (value, witness,
    nodes): value < ub with a witness, or ub (no nontrivial codeword of weight < ub)."""
    import subprocess

    L = logical_reps(Hc, Hs)
    n = Hc.shape[1]
    assert len(L) <= 128 and ub <= 64
    head_rows = []
    for row in Hc:
        sup = [int(q) for q in np.nonzero(row)[0]]
        head_rows.append(" ".join(map(str, [len(sup), *sup])))
    labs = []
    for q in range(n):
        x = sum(int(L[j, q]) << j for j in range(len(L)))
        labs.append(f"{x & ((1 << 64) - 1):x} {x >> 64:x}")
    cuts = [round(i * n / procs) for i in range(procs + 1)]
    ps = []
    for a0, a1 in zip(cuts, cuts[1:], strict=False):
        txt = f"{n} {Hc.shape[0]} {len(L)} {ub} {a0} {a1}\n" + "\n".join(head_rows + labs) + "\n"
        p = subprocess.Popen([str(HERE / "dfs")], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             text=True)
        p.stdin.write(txt)
        p.stdin.close()
        ps.append(p)
    best, wit, nodes = ub, None, 0
    for p in ps:
        p.wait(timeout=timeout)
        out = p.stdout.read().split("\n")
        assert p.returncode == 0, p.returncode
        v, nd = map(int, out[0].split())
        nodes += nd
        if v < best:
            best, wit = v, [int(t) for t in out[1].split()]
    if wit is not None:
        x = np.zeros(n, dtype=np.uint8)
        x[wit] = 1
        assert nontrivial(x, Hc, Hs) and int(x.sum()) == best
    return best, wit, nodes


def dfs_anchors(Hc, Hs, ub, ranges, timeout=1100):
    """dfs.c over the given anchor ranges [(a0, a1), ...], one process each."""
    import subprocess

    L = logical_reps(Hc, Hs)
    n = Hc.shape[1]
    rows = []
    for row in Hc:
        sup = [int(q) for q in np.nonzero(row)[0]]
        rows.append(" ".join(map(str, [len(sup), *sup])))
    labs = []
    for q in range(n):
        x = sum(int(L[j, q]) << j for j in range(len(L)))
        labs.append(f"{x & ((1 << 64) - 1):x} {x >> 64:x}")
    ps = []
    for a0, a1 in ranges:
        txt = f"{n} {Hc.shape[0]} {len(L)} {ub} {a0} {a1}\n" + "\n".join(rows + labs) + "\n"
        p = subprocess.Popen([str(HERE / "dfs")], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             text=True)
        p.stdin.write(txt)
        p.stdin.close()
        ps.append(p)
    best, wit, nodes = ub, None, 0
    for p in ps:
        p.wait(timeout=timeout)
        out = p.stdout.read().split("\n")
        v, nd = map(int, out[0].split())
        nodes += nd
        if v < best:
            best, wit = v, [int(t) for t in out[1].split()]
    return best, wit, nodes
