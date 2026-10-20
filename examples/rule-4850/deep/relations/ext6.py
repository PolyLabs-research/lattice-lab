"""
Extension of the relation search: M2 over the whole radius-6 family (268,435,455 rules),
M1 over the radius <= 4 family (32,767 rules), all Frobenius twists:
    2^gp L(f) = 2^dp L(M1) + L(M2)   (mod 513, on the classes of the mode).
The queries 2^gp F - 2^dp L(M1) (32768 * 324 = 10.6M vectors) are sorted once; the radius-6
family is streamed in 128 chunks of 2^21 rules (rule n = i + 2^21 j: radius-5 part i, radius-6
orbits j), each chunk's values being the radius-5 values XOR the chunk's radius-6 orbit values.
Every hit is verified by eigenvalues at the class representatives (run_targets.eig_classes).

    python ext6.py name mode n [n ...]   -> ext6_<name>.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_targets as R  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
CHARS = tables.CHARS
POW = S.POW
P2 = S.P2


def coords5():
    orbs = C.orbits(5)
    values = np.zeros((len(CHARS), 1 << len(orbs)), dtype=np.uint32)
    for i, o in enumerate(orbs):
        ov = np.array([C.coord(C._value(C.points(o), j, k)) for j, k in CHARS], dtype=np.uint32)
        values[:, 1 << i: 2 << i] = values[:, : 1 << i] ^ ov[:, None]
    return values


def coords6_extra():
    """(11, 128) coordinates of the XOR of each subset of the 7 radius-6 orbits."""
    orbs6 = C.orbits(6)[21:]
    out = np.zeros((len(CHARS), 128), dtype=np.uint32)
    for i, o in enumerate(orbs6):
        ov = np.array([C.coord(C._value(C.points(o), j, k)) for j, k in CHARS], dtype=np.uint32)
        out[:, 1 << i: 2 << i] = out[:, : 1 << i] ^ ov[:, None]
    return out


def key(V):
    k = np.zeros(V.shape[1], dtype=np.uint64)
    for i in range(S.KEYC):
        k += V[i].astype(np.uint64) * POW[i]
    return k


def run(targets, mode, name):
    cls = S.MODES[mode]
    L = tables.L5()[:, : 1 << 15]  # radius <= 4
    ok1 = (L[cls] >= 0).all(axis=0)
    m1ids = np.flatnonzero(ok1)
    V1 = L[cls][:, ok1].astype(np.int64)
    tab = tables.log_table()
    c5 = coords5()
    c6 = coords6_extra()
    allres = []
    for n in targets:
        t0 = time.time()
        f = R.expset(n)
        F = tables.logs513(f)[cls].astype(np.int64)
        qs, meta = [], []
        for dp in range(18):
            D = (P2[dp] * V1) % 513
            for gp in range(18):
                G = (P2[gp] * F) % 513
                qs.append((G[:, None] - D) % 513)
                meta.append((gp, dp))
        n1 = V1.shape[1]
        # single-rule relations with any exponent: alpha F = L(M2), alpha = 1..512 (M1 = 1)
        alphas = np.arange(1, 513)
        QA = (alphas[None, :] * F[:, None]) % 513
        QA = np.pad(QA, ((0, 0), (0, (-QA.shape[1]) % n1)), constant_values=-1)
        nA = QA.shape[1] // n1
        for b in range(nA):
            qs.append(QA[:, b * n1:(b + 1) * n1])
            meta.append(("alpha", b))
        Q = np.concatenate(qs, axis=1).astype(np.int16)  # (k, (324 + nA) * n1)
        qk = key(Q)
        order = np.argsort(qk)
        qk = qk[order]
        hits = []
        for j in range(128):
            vals = c5 ^ c6[:, j: j + 1]
            lg = tab[vals[cls]]
            okc = (lg >= 0).all(axis=0)
            V2 = (lg % 513).astype(np.int64)
            k2 = key(V2)
            lo = np.searchsorted(qk, k2, "left")
            hi = np.searchsorted(qk, k2, "right")
            for i in np.flatnonzero((hi > lo) & okc):
                for p in range(lo[i], hi[i]):
                    qi = order[p]
                    if (Q[:, qi] == V2[:, i]).all():
                        b, c = divmod(qi, n1)
                        gp, dp = meta[b]
                        if gp == "alpha":
                            hits.append(("alpha", int(alphas[dp * n1 + c]), 1,
                                         int(i + (j << 21))))
                        else:
                            hits.append((gp, dp, int(m1ids[c]), int(i + (j << 21))))
        out = []
        for gp, dp, m1, m2 in hits:
            if gp == "alpha":
                ev = eig_alpha(f, dp, m2)
                out.append({"alpha": dp, "M2": m2, "verified": all(ev[c] for c in cls),
                            "lines": [ev[0], ev[1]]})
                continue
            ev = eig6(f, gp, dp, m1, m2)
            out.append({"gp": gp, "dp": dp, "M1": m1, "M2": m2,
                        "verified": all(ev[c] for c in cls), "lines": [ev[0], ev[1]]})
        res = {"rule": n, "mode": mode, "hits": len(out), "list": out[:500],
               "seconds": round(time.time() - t0, 1)}
        print(n, mode, "hits", len(out), "verified", all(h["verified"] for h in out),
              res["seconds"], "s", flush=True)
        allres.append(res)
        json.dump(allres, open(os.path.join(HERE, f"ext6_{name}.json"), "w"), indent=1)
    return allres


def eig_alpha(f, alpha, m2):
    """(lambda_f^alpha / lambda_M2)^511 = 1 at each class representative (None if a zero)."""
    F36 = R.F36
    g2 = C.rule(m2, 6)
    out = []
    for j, k in CHARS:
        vf, v2 = R.value(f, j, k), R.value(g2, j, k)
        if vf == 0 or v2 == 0:
            out.append(None)
            continue
        out.append(F36.pow(F36.pow(vf, alpha), 511) == F36.pow(v2, 511))
    return out


def eig6(f, gp, dp, m1, m2):
    F36 = R.F36
    g1, g2 = C.rule(m1, 6), C.rule(m2, 6)
    out = []
    for j, k in CHARS:
        vf, v1, v2 = (R.value(h, j, k) for h in (f, g1, g2))
        if v1 == 0 or v2 == 0 or vf == 0:
            out.append(None)
            continue
        lhs = F36.pow(F36.pow(vf, 2**gp), 511)
        rhs = F36.pow(F36.mul(F36.pow(v1, 2**dp), v2), 511)
        out.append(lhs == rhs)
    return out


if __name__ == "__main__":
    name, mode, ns = sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3:]]
    run(ns, mode, name)
