"""
The symmetric line-unit lattice at m = 37, modulo F(2^9)*.

For a primitive w, t_w = X_w + 1/X_w has value t_{w.c} = t_1^(2^a(w.c)) at a character c with
w.c != 0 (2 is a primitive root mod 37, t_{-j} = t_j) and 0 on the line w.c = 0, while
Psi_e(t_w) (e > 1) has value t_{w.c}^(A_e/2) there and 1 on that line. A symmetric unit is a
product over D4-orbits of directions; the orbit of (1, k) is {(1,k),(1,-k),(k,1),(k,-1)}/+-.
log t_1 = 3u with u a unit mod 171 (t_1 has order 87381 = (2^18-1)/3). So, modulo F(2^9)*, the
class logs of symmetric non-vanishing unit products (Psi-type units, any exponents) form the
lattice 3 * (Z/171-span of the orbit vectors g_k(c) = sum_{w in O_k, w.c != 0} 2^a(w.c)), and
t-type orbit products have the same vector but vanish on the classes perpendicular to O_k.

    python units.py     # ranks, and membership of the dossier's vectors
"""
from __future__ import annotations

import os
import sys

import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tables  # noqa: E402

M = 37
CHARS = tables.CHARS
LOG2 = {pow(2, a, M): a for a in range(36)}
FREE = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]
OFF = [2, 3, 4, 5, 7, 8, 9, 10]


def orbit_dirs(k):
    ws = {(1, k), (1, -k), (k, 1), (k, -1)}
    out = []
    for w in ws:
        if (-w[0], -w[1]) not in out:
            out.append(w)
    return out


def orbit_reps():
    return [c[1] if c != (0, 1) else 0 for c in CHARS]  # k = 0 (axes) and the ten k's


def gvec(k):
    """sum over the orbit of 2^a(w.c) mod 171 at each class, and the classes where it vanishes."""
    v, zero = [], []
    for ci, (j, kk) in enumerate(CHARS):
        s = 0
        for w in orbit_dirs(k):
            d = (w[0] * j + w[1] * kk) % M
            if d == 0:
                zero.append(ci)
                continue
            s += pow(2, LOG2[d], 171)
        v.append(s % 171)
    return v, sorted(set(zero))


def log_t1():
    lt = tables.f18.log(tables.f18.t(1))
    assert lt % 3 == 0
    return lt


def smith_rank(A, p):
    return sympy.Matrix(A).rank(iszerofunc=lambda x: x % p == 0) if False else _rank_mod(A, p)


def _rank_mod(A, p):
    A = [list(map(int, r)) for r in A]
    A = [[x % p for x in r] for r in A]
    rank, rows, cols = 0, len(A), len(A[0])
    for c in range(cols):
        piv = next((r for r in range(rank, rows) if A[r][c] % p), None)
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        inv = pow(A[rank][c], -1, p)
        A[rank] = [x * inv % p for x in A[rank]]
        for r in range(rows):
            if r != rank and A[r][c]:
                f = A[r][c]
                A[r] = [(x - f * y) % p for x, y in zip(A[r], A[rank])]
        rank += 1
    return rank


def solve_mod(G, target, p):
    """x with x G = target (mod p prime), or None. G: generators as rows."""
    G = sympy.Matrix(G).applyfunc(lambda x: x % p)
    t = sympy.Matrix([target]).applyfunc(lambda x: x % p)
    n = G.shape[0]
    aug = G.T.row_join(t.T)
    rG = _rank_mod(G.T.tolist(), p)
    ra = _rank_mod(aug.tolist(), p)
    return rG, ra, rG == ra


if __name__ == "__main__":
    lt = log_t1()
    u = (lt // 3) % 171
    print("log t_1 =", lt, " = 3u, u mod 171 =", u)
    reps = orbit_reps()
    G, Z = [], []
    for k in reps:
        v, z = gvec(k)
        G.append(v)
        Z.append(z)
        print(f"orbit (1,{k}): dirs {orbit_dirs(k)}  vanishes on classes {[CHARS[i] for i in z]}")
    G = np.array(G)
    # check against actual logs: the t-type orbit product for k = 0 is ab = orbit (1,1) = rule 4
    L = tables.L5()
    ab = L[:, 4].astype(int)
    pred = [(3 * u * G[0][c]) % 513 if c not in Z[0] else -1 for c in range(11)]
    print("rule 4 = ab:", ab.tolist(), "predicted", pred)
    assert ab.tolist() == pred
    k1 = L[:, 8].astype(int)  # orbit (2,0) = a^2 + b^2 = t(xy) t(x/y)
    pred = [(3 * u * G[1][c]) % 513 if c not in Z[1] else -1 for c in range(11)]
    print("rule 8 = t(xy)t(x/y):", k1.tolist(), "predicted", pred)
    assert k1.tolist() == pred
    for p in (3, 19):
        print(f"rank mod {p} of the 11 orbit vectors on the 10 free classes:",
              _rank_mod(G[:, FREE].tolist(), p), "; on the 8 off-line classes:",
              _rank_mod(G[:, OFF].tolist(), p))
    np.save(os.path.join(HERE, "unit_G.npy"), G)
