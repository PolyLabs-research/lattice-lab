"""
Run the two-rule relation search (search.py) on the targets, the 4850 relatives and the
positive controls; verify every hit exactly in the group ring and classify it.

A hit (gp, dp, M1, M2) means 2^gp L(f) = 2^dp L(M1) + L(M2) (mod 513) at every class.
Classes of hits:
  exact      the relation comes from an exact group-ring identity with exponents +-1:
               (a) f' = M1' M2, (b) f' M1'' = M2, (c) f'' M2 = M1''
             (' = dilation by 2^gp or 2^dp, '' = by 2^(gp-9) or 2^(dp-9)); the F(2^9) factor is 1.
  multiple   f itself divides M1 or M2 in the Laurent ring (only possible for f of radius <= 5).
  genuine    neither: an F(2^9)-valued quotient that is not 1 and not through f.
In mode "off" (relation on the 8 classes i = 1..8 only) a hit is verified by eigenvalues at
the class representatives (field arithmetic in F(2^36), no logs), and "lines" records whether it
also holds on the axis and the diagonal.
Usage: python run_targets.py name mode n [n ...]    -> results_<name>.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
M = 37
X, Y = sympy.symbols("x y")


def radius_of(n: int) -> int:
    r = 0
    while (1 << len(C.orbits(r))) <= n:
        r += 1
    return r


def expset(n: int):
    return C.rule(n, max(radius_of(n), 5))


def poly(f):
    """f as a polynomial, shifted so that x and y do not divide it (f is symmetric)."""
    mp, mq = min(p for p, _ in f), min(q for _, q in f)
    s = 0
    for p, q in f:
        s += X ** (p - mp) * Y ** (q - mq)
    return sympy.Poly(s, X, Y, modulus=2)


def divides(f, g) -> bool:
    if not g:
        return False
    _, r = sympy.div(poly(g), poly(f))
    return r.is_zero


def exact_kind(f, gp, dp, m1, m2):
    d = lambda a, k: S.dilate(a, pow(2, k % 36, M))  # noqa: E731
    F_ = S.dense(f)
    A = S.dense(C.rule(m1, 5))
    B = S.dense(C.rule(m2, 5))
    if (d(F_, gp) == S.gmul(d(A, dp), B)).all():
        return "a"
    if (S.gmul(d(F_, gp), d(A, dp - 9)) == B).all():
        return "b"
    if (S.gmul(d(F_, gp - 9), B) == d(A, dp - 9)).all():
        return "c"
    return None


F36 = C.F
ZP = [F36.pow(F36.zeta, e) for e in range(M)]


def value(f, j, k):
    v = 0
    for p, q in f:
        v ^= ZP[(p * j + q * k) % M]
    return v


def eig_classes(f, gp, dp, m1, m2):
    """per class: True/False whether (l_f^(2^gp)/(l_1^(2^dp) l_2))^511 = 1, None if M1 or M2 is 0."""
    g1, g2 = C.rule(m1, 5), C.rule(m2, 5)
    out = []
    for j, k in tables.CHARS:
        vf, v1, v2 = (value(h, j, k) for h in (f, g1, g2))
        if v1 == 0 or v2 == 0 or vf == 0:
            out.append(None)
            continue
        lhs = F36.pow(F36.pow(vf, 2**gp), 511)
        rhs = F36.pow(F36.mul(F36.pow(v1, 2**dp), v2), 511)
        out.append(lhs == rhs)
    return out


def classify(n, hits, mode="all"):
    f = expset(n)
    small = radius_of(n) <= 5
    divcache = {}

    def fdiv(m):
        if not small:
            return False
        if m not in divcache:
            divcache[m] = divides(f, C.rule(m, 5))
        return divcache[m]

    out = []
    for gp, dp, m1, m2 in hits:
        ev = eig_classes(f, gp, dp, m1, m2)
        ok = all(ev[c] for c in S.MODES[mode]) and ev[6] is not False
        if mode == "all":
            ok = ok and S.exact_relation(f, gp, dp, m1, m2)
        kind = exact_kind(f, gp, dp, m1, m2)
        if kind is None and (fdiv(m1) or fdiv(m2)):
            kind = "multiple"
        h = {"gp": gp, "dp": dp, "M1": m1, "M2": m2, "verified": ok, "kind": kind or "genuine"}
        if mode == "off":
            h["lines"] = [ev[0], ev[1]]
        out.append(h)
    return out


def run(n, mode="all"):
    t0 = time.time()
    f = expset(n)
    F = tables.logs513(f)
    if (F[S.MODES[mode]] < 0).any():
        return {"rule": n, "logs513": F.tolist(), "note": "has zero eigenvalues"}
    hits = S.index(mode).search(F)
    cl = classify(n, hits, mode)
    kinds = {}
    for h in cl:
        kinds[h["kind"]] = kinds.get(h["kind"], 0) + 1
    res = {"rule": n, "mode": mode, "radius": radius_of(n), "logs513": F.tolist(), "hits": len(hits),
           "all_verified": all(h["verified"] for h in cl), "kinds": kinds,
           "genuine": [h for h in cl if h["kind"] == "genuine"],
           "seconds": round(time.time() - t0, 1)}
    if len(cl) <= 400:
        res["all"] = cl
    return res


if __name__ == "__main__":
    name, mode, ns = sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3:]]
    results = []
    for n in ns:
        r = run(n, mode)
        print(n, {k: r[k] for k in r if k not in ("genuine", "all")},
              "genuine:", len(r.get("genuine", [])), flush=True)
        results.append(r)
        json.dump(results, open(os.path.join(HERE, f"results_{name}.json"), "w"), indent=1)
