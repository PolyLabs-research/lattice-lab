"""
Sparse numerators: 4850 * (a + b) = Sh(5,2) + Sh(4,0) and 10491524 * ab = Sh(7,3) + Sh(4,4)
(shells.py). At m = 37 every t_{nj} is a Frobenius power of t_j (n = +-2^alpha), so with
x = t_j, y = t_k the eigenvalue of any shell sum is a sum of "binomials"
    B(al, be) = x^(2^al) y^(2^be) + x^(2^be) y^(2^al)   (shell (p,q), p = +-2^al, q = +-2^be),
    B(al, al) = (xy)^(2^al)                              (shell (p,p)),
    B(al, *)  = x^(2^al) + y^(2^al)                      (shell (p,0)),   and 1 (the origin),
and 4850 = [B(5,1) + B(2,*)] / (x + y),  10491524 = [B(14,8) + B(2,2)] / (xy).
This script checks those closed forms against the census logs, then runs a census of all
numerators made of 2 or 3 such terms over the denominators x + y and xy (each quotient is a
symmetric rule): which are ninth-power confined at the 9 classes where the denominator is
nonzero and which are not forced? Chance level is about 3^-8 per numerator for confinement given
cube confinement... we just count, and look at the confined ones' shapes (is 4850's an
isolated case or a member of a structured family?).

    python sparse.py    -> sparse.json
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tables  # noqa: E402

C = tables.C
F = C.F
f18 = tables.f18
TAB = tables.log_table()  # full logs, -1 at 0
CH = tables.CHARS
STAR = 18  # index for "y^0"
CONST = 19


def tval(j):
    return f18.t(j)


def term_value(term, x, y):
    al, be = term
    if term == (CONST, CONST):
        return 1
    X = lambda e: F.pow(x, 2**e)  # noqa: E731
    Y = lambda e: F.pow(y, 2**e)  # noqa: E731
    if be == STAR:
        return X(al) ^ Y(al)
    if al == be:
        return F.mul(X(al), Y(al))
    return F.mul(X(al), Y(be)) ^ F.mul(X(be), Y(al))


def terms():
    out = [(CONST, CONST)]
    for al in range(18):
        out.append((al, STAR))
        for be in range(al + 1):
            out.append((al, be))
    return out


def main():
    res = {}
    T = terms()
    nT = len(T)
    # coordinates (GF(2)-linear) of every term at every class rep
    pts = [(tval(j), tval(k)) for j, k in CH]
    coords = np.zeros((len(CH), nT), dtype=np.int64)
    for ci, (x, y) in enumerate(pts):
        for ti, tm in enumerate(T):
            coords[ci, ti] = C.coord(term_value(tm, x, y))
    dens = {"x+y": [C.coord(x ^ y) for x, y in pts], "xy": [C.coord(F.mul(x, y)) for x, y in pts]}
    dlog = {k: np.array([TAB[c] for c in v]) for k, v in dens.items()}
    idx = {tm: i for i, tm in enumerate(T)}

    def logs_of(tlist, den):
        c = np.zeros(len(CH), dtype=np.int64)
        for tm in tlist:
            c ^= coords[:, idx[tm]]
        ln = TAB[c]
        ld = dlog[den]
        out = np.where((ln < 0) | (ld < 0), -1, (ln - ld) % (2**18 - 1))
        return out

    # 1. closed forms vs the census
    for name, tl, den, rule in (("4850", [(5, 1), (2, STAR)], "x+y", 4850),
                                ("10491524", [(14, 8), (2, 2)], "xy", 10491524)):
        lg = logs_of(tl, den)
        ref = tables.full_logs(tables.C.rule(rule, 6))
        ok = [bool(a == b) for a, b in zip(lg, ref) if a >= 0]
        print(f"closed form {name}: {tl}/{den}: matches census logs at {sum(ok)}/{len(ok)} classes")
        res[f"closed_form_{name}"] = {"terms": tl, "den": den, "matches": sum(ok), "of": len(ok)}

    # 2. census of 2- and 3-term numerators
    found = {}
    for den in ("x+y", "xy"):
        zero_cls = [ci for ci in range(len(CH)) if dlog[den][ci] < 0]
        # admissible terms: divisible by the denominator
        if den == "xy":
            adm = [tm for tm in T if tm[1] not in (STAR, CONST)]
        else:
            adm = [tm for tm in T if tm != (CONST, CONST)]
        A = np.array([idx[tm] for tm in adm])
        for r in (2, 3):
            n_conf = n_cube = n_tot = 0
            examples = []
            combos = np.array(list(itertools.combinations(range(len(adm)), r)))
            # normalise the overall Frobenius twist: require the smallest finite index to be 0
            c = np.zeros((len(CH), len(combos)), dtype=np.int64)
            for col in range(r):
                c ^= coords[:, A[combos[:, col]]]
            ln = TAB[c]  # (11, n)
            ld = dlog[den][:, None]
            keep = [ci for ci in range(len(CH)) if ci not in zero_cls]
            lnk, ldk = ln[keep], ld[keep]
            nz = (lnk >= 0).all(axis=0)
            q = (lnk - ldk) % (2**18 - 1)
            cube = nz & (q % 3 == 0).all(axis=0)
            ninth = nz & (q % 9 == 0).all(axis=0)
            n_tot = int(nz.sum())
            n_cube = int(cube.sum())
            n_conf = int(ninth.sum())
            sel = np.flatnonzero(ninth)
            for s in sel[:400]:
                examples.append([adm[i] for i in combos[s]])
            found[f"{den} r={r}"] = {"numerators_nonzero": n_tot, "cube_confined": n_cube,
                                     "ninth_confined": n_conf, "examples": examples}
            print(den, "terms", r, ": nonzero", n_tot, "cube", n_cube, "ninth", n_conf, flush=True)
    res["census"] = found
    json.dump(res, open(os.path.join(HERE, "sparse.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
