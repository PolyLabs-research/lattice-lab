"""
Relations with an arbitrary exponent on M1:
    2^gp L(f) = beta L(M1) + L(M2)  (mod 513),  beta in Z/513 (all 513 values),
M1 of radius <= 4, M2 of radius <= 5 (index of search.py), modes "all" and "off".
This is f^(2^gp) = M1^beta * M2 * (F(2^9)-valued): it contains g^3 * U * F(2^9) for every g of
radius <= 4 and every U of radius <= 5 (pilot 7 tried g of radius <= 6 with seven units U), and
f = M1^beta * F(2^9) (M2 = 1). Every hit is verified by eigenvalues at the class
representatives; hits that pass through a Laurent multiple of 4850 (or of f) are flagged.

    python gen_beta.py name n [n ...]   -> genbeta_<name>.json
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
F4850 = RT.expset(4850)


def eig_beta(f, gp, beta, m1, m2):
    F36 = RT.F36
    g1, g2 = C.rule(m1, 5), C.rule(m2, 5)
    out = []
    for j, k in tables.CHARS:
        vf, v1, v2 = (RT.value(h, j, k) for h in (f, g1, g2))
        if 0 in (vf, v1, v2):
            out.append(None)
            continue
        lhs = F36.pow(F36.pow(vf, 2**gp), 511)
        rhs = F36.pow(F36.mul(F36.pow(v1, beta), v2), 511)
        out.append(lhs == rhs)
    return out


def run(n, mode):
    t0 = time.time()
    f = RT.expset(n)
    F = tables.logs513(f)
    if (F[S.MODES[mode]] < 0).any():
        return None
    betas = list(range(1, 513))  # beta = 0 is the single-rule case (search.py with M1 = 1)
    raw = S.index(mode).search(F, m1max=1 << 15, m1mults=betas)
    hits = [(gp, betas[i], m1, m2) for gp, i, m1, m2 in raw if m1 != 1]
    small = RT.radius_of(n) <= 5
    cache = {}

    def through(m):
        if m not in cache:
            g = C.rule(m, 5)
            cache[m] = RT.divides(F4850, g) or (small and RT.divides(f, g))
        return cache[m]

    rows = []
    for gp, beta, m1, m2 in hits:
        ev = eig_beta(f, gp, beta, m1, m2)
        triv = None
        if beta in S.P2:  # beta a power of 2: exact identities as in run_targets
            triv = RT.exact_kind(f, gp, S.P2.index(beta), m1, m2)
        rows.append({"gp": gp, "beta": beta, "M1": m1, "M2": m2,
                     "verified": all(ev[c] for c in S.MODES[mode]),
                     "exact": triv, "via_4850_or_self": through(m1) or through(m2)})
    clean = [r for r in rows if not r["exact"] and not r["via_4850_or_self"]]
    return {"rule": n, "mode": mode, "hits": len(rows), "all_verified": all(r["verified"] for r in rows),
            "clean": clean[:200], "n_clean": len(clean), "seconds": round(time.time() - t0, 1)}


if __name__ == "__main__":
    name, ns = sys.argv[1], [int(a) for a in sys.argv[2:]]
    out = []
    for n in ns:
        for mode in ("all", "off"):
            r = run(n, mode)
            if r is None:
                continue
            print(n, mode, {k: v for k, v in r.items() if k != "clean"},
                  r["clean"][:5], flush=True)
            out.append(r)
            json.dump(out, open(os.path.join(HERE, f"genbeta_{name}.json"), "w"), indent=1)
