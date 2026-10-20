"""
sigma-partners: rules g of radius <= 6 with
    L(g) = 2^(6j) L(f) + c L(U)   (mod 513) on the 8 classes i = 1..8,
j in {0, 1, 2} (sigma = Frobenius x -> x^(2^6) = dilation by 27 = -10 mod 37, of order 3 on
F(2^18), fixing F(2^6)), U a small unit (rule 4 = ab = t(x)t(y), rule 8 = t(xy)t(x/y),
rule 7 = (1+a)(1+b)) to any power c (mod 171), or U = 1. That is,
    g = sigma^j(f) * U^c * (F(2^9)-valued)   off the lines where U vanishes.
Found for f = 10491524 by ext6.py/trio.py (g = 20982139, j = 1, U = ab, c = 63 = 2^6 - 1; and
g = 178279803, j = 2, c = 504 = 2^12 - 1). Here: is this common? Targets: the 125 ninth-power
rules of radius <= 6 and the random sets of calib.py. Every hit is verified by eigenvalues at
the class representatives; we also record whether it extends to the axis and the diagonal.

    python sigma.py   -> sigma.json
"""
from __future__ import annotations

import collections
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calib  # noqa: E402
import ext6  # noqa: E402
import patterns  # noqa: E402
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
OFF = S.MODES["off"]
UNITS = [1, 4, 8, 7]


def logs(n):
    return tables.logs513(RT.expset(n)).astype(np.int64)


def check(f, g, j, u, c):
    """eigenvalue check at the 11 class reps: (l_g / (l_f^(2^6j) l_u^c))^511 = 1."""
    F36 = RT.F36
    ff, gg, uu = RT.expset(f), RT.expset(g), RT.expset(u)
    out = []
    for jj, kk in tables.CHARS:
        vf, vg, vu = RT.value(ff, jj, kk), RT.value(gg, jj, kk), RT.value(uu, jj, kk)
        if 0 in (vf, vg, vu):
            out.append(None)
            continue
        rhs = F36.mul(F36.pow(vf, 2 ** (6 * j)), F36.pow(vu, c))
        out.append(F36.pow(vg, 511) == F36.pow(rhs, 511))
    return out


def main():
    recs = patterns.records()
    r6, cube6, r5 = calib.random_sets()
    groups = {"ninth125": [i for i, _, _ in recs], "random6": r6, "cube6": cube6, "random5": r5}
    targets, tgroup = [], {}
    for g, ns in groups.items():
        for n in ns:
            v = logs(n)
            if (v[OFF] < 0).any() or n in tgroup:
                continue
            targets.append(n)
            tgroup[n] = g
    Lu = {u: logs(u) for u in UNITS}
    qs, meta = [], []
    for n in targets:
        F = logs(n)
        for j in range(3):
            base = (pow(2, 6 * j, 513) * F) % 513
            for u in UNITS:
                for c in (range(171) if u != 1 else [0]):
                    if u != 1 and c == 0:
                        continue
                    qs.append(((base + c * Lu[u]) % 513)[OFF])
                    meta.append((n, j, u, c))
    Q = np.array(qs, dtype=np.int64).T  # (8, nq)
    qk = ext6.key(Q)
    order = np.argsort(qk)
    qk = qk[order]
    print("targets", len(targets), "queries", Q.shape[1], flush=True)
    tab = tables.log_table()
    c5 = ext6.coords5()
    c6 = ext6.coords6_extra()
    hits = []
    t0 = time.time()
    for ch in range(128):
        lg = tab[c5 ^ c6[:, ch: ch + 1]].astype(np.int64)
        sub = lg[OFF]
        ok = (sub >= 0).all(axis=0)
        V = sub % 513
        k2 = ext6.key(V)
        lo = np.searchsorted(qk, k2, "left")
        hi = np.searchsorted(qk, k2, "right")
        for i in np.flatnonzero((hi > lo) & ok):
            for p in range(lo[i], hi[i]):
                qi = order[p]
                if (Q[:, qi] == V[:, i]).all():
                    hits.append(meta[qi] + (int(i + (ch << 21)),))
        if ch % 32 == 31:
            print("chunk", ch, len(hits), f"{time.time() - t0:.0f}s", flush=True)
    # dedupe (n, j, u, g) keeping the smallest c; drop g == f with j == 0
    best = {}
    for n, j, u, c, g in hits:
        if j == 0 and g == n:
            continue
        key = (n, j, u, g)
        if key not in best or c < best[key]:
            best[key] = c
    rows = []
    for (n, j, u, g), c in sorted(best.items()):
        ev = check(n, g, j, u, c)
        rows.append({"f": n, "group": tgroup[n], "j": j, "U": u, "c": c, "g": g,
                     "verified_off": all(ev[k] for k in OFF), "axis": ev[0], "diag": ev[1]})
    out = {"targets": {g: sum(1 for n in targets if tgroup[n] == g) for g in groups},
           "hits": rows}
    # summary per group: targets with a partner g != f (any j), and with j != 0
    summ = {}
    for g in groups:
        ts = [n for n in targets if tgroup[n] == g]
        p_any = {r["f"] for r in rows if r["group"] == g and r["g"] != r["f"]}
        p_sig = {r["f"] for r in rows if r["group"] == g and r["j"] != 0 and r["g"] != r["f"]}
        p_self = {r["f"] for r in rows if r["group"] == g and r["j"] != 0 and r["g"] == r["f"]}
        summ[g] = {"targets": len(ts), "partner_any": len(p_any), "partner_sigma": len(p_sig),
                   "sigma_self": len(p_self)}
    out["summary"] = summ
    print(json.dumps(summ, indent=1))
    for n in (4850, 10491524, 20982139, 178279803, 482758, 8438150, 43250486):
        print(n, [(r["j"], r["U"], r["c"], r["g"], r["verified_off"], r["axis"], r["diag"])
                  for r in rows if r["f"] == n][:20])
    json.dump(out, open(os.path.join(HERE, "sigma.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
