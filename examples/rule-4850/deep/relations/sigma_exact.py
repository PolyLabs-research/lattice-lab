"""
bfactor.py found that the F(2^9)-valued factor of the trio relation is identically 1 off the axis
lines, i.e. an exact identity of eigenvalues: for every character c = (j, k) with j k != 0,
    lambda_{20982139}(c)  t_j t_k = lambda_{10491524}(10 c)  t_{10 j} t_{10 k}
    lambda_{178279803}(c) t_j t_k = lambda_{10491524}(26 c)  t_{26 j} t_{26 k}
(10 = -27 = -2^6 and 26 = 2^12 mod 37: the cube roots of 1 mod 37, i.e. sigma and sigma^2).
In the group ring R = F2[x,y]/(x^37 - 1, y^37 - 1) this says that
    D = g * ab + (f * ab)(x^d, y^d)
has Fourier transform supported on the axis lines, i.e. D = J_x P(y) + J_y Q(x) + c J_x J_y with
J_x = sum_p x^p. This script computes D exactly, checks that form, and prints P and Q; it
also checks the eigenvalue identity directly at all 1369 characters (field arithmetic).

    python sigma_exact.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402

M = 37
F = RT.F36


def dense(n):
    return S.dense(RT.expset(n))


def analyse(g, f, d):
    ab = dense(4)
    lhs = S.gmul(dense(g), ab)
    rhs = S.dilate(S.gmul(dense(f), ab), d)
    D = lhs ^ rhs
    # D = J_x P(y) + J_y Q(x): every column (fixed q) constant in p, up to a function of p alone.
    # Write D[p, q] = P[q] + Q[p] (+ const absorbed); test: D[p,q] + D[p,0] + D[0,q] + D[0,0] == 0
    test = D ^ D[:, :1] ^ D[:1, :] ^ D[0, 0]
    form = not test.any()
    P = D[0, :] ^ D[0, 0]  # function of q (the y-part), normalised P[0] = 0
    Q = D[:, 0]  # function of p
    # eigenvalue identity at all characters with jk != 0
    G, Fn, U = RT.expset(g), RT.expset(f), RT.expset(4)
    bad = 0
    for j in range(1, M):
        for k in range(1, M):
            l1 = F.mul(RT.value(G, j, k), RT.value(U, j, k))
            l2 = F.mul(RT.value(Fn, d * j % M, d * k % M), RT.value(U, d * j % M, d * k % M))
            bad += l1 != l2
    return {"terms_lhs": int(lhs.sum()), "terms_rhs": int(rhs.sum()), "terms_D": int(D.sum()),
            "D_is_axis_form": form, "P_support(q)": [int(q) for q in np.flatnonzero(P)],
            "Q_support(p)": [int(p) for p in np.flatnonzero(Q)], "eig_failures_jk_nonzero": bad}


if __name__ == "__main__":
    for g, d in ((20982139, 10), (20982139, 27), (178279803, 26), (178279803, 11)):
        print(g, "vs 10491524 dilated by", d, analyse(g, 10491524, d))
    # also: are 4850 and 10491524 related the same way to anything? (control: 4850 vs itself)
    print("control 10491524 vs itself, d=10:", analyse(10491524, 10491524, 10))
