"""
Step 2c: what are the full mod-27 pattern collisions (clusters.npz from pairs.py)?

For every pair of rules in a cluster (both in the same family), the polynomial relation over GF(2)
(tested by specialising y to three random elements of GF(2^16)): gcd degree > 0 (they share a factor: a unit multiple f*U = g, or
g1*U1, g1*U2) or coprime. A coprime pair has no polynomial relation of small radius at all; its
classes agree mod 27 either by chance or by a genuinely mod-37 identity (the relatives' kind).
Also marks clusters whose rules are ninth-power or 27th-power confined.
Writes gcd_clusters.json.
"""
from __future__ import annotations

import itertools
import json
import sys
import time

import random

import numpy as np

sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import census  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
# GF(2^16) = F2[z]/(z^16 + z^12 + z^3 + z + 1), z primitive; exp/log tables
POLY16 = 0x1100B
EXP = [0] * (2 * 65535)
LOG = [0] * 65536
_v = 1
for _i in range(65535):
    EXP[_i] = EXP[_i + 65535] = _v
    LOG[_v] = _i
    _v <<= 1
    if _v >> 16:
        _v ^= POLY16
assert _v == 1


def gmul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def ginv(a):
    return EXP[65535 - LOG[a]]


def specialise(rid, y0):
    """x^r y^r f(x, y) at y = y0, as a list of GF(2^16) coefficients in x (r the rule's radius)."""
    f = census.rule(rid, 6)
    r = max(max(abs(p), abs(q)) for p, q in f)
    coeffs = [0] * (2 * r + 1)
    for p, q in f:
        e = q + r
        coeffs[p + r] ^= EXP[(LOG[y0] * e) % 65535]
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def pgcd_deg(a, b):
    """Degree of gcd(a, b) in GF(2^16)[x] (lists, low degree first)."""
    a, b = a[:], b[:]
    while b:
        while len(a) >= len(b) and a:
            c = gmul(a[-1], ginv(b[-1]))
            sh = len(a) - len(b)
            for i, bi in enumerate(b):
                a[i + sh] ^= gmul(c, bi)
            while a and a[-1] == 0:
                a.pop()
        a, b = b, a
    return len(a) - 1


RNG = random.Random(4850)
Y0 = [RNG.randrange(2, 65536) for _ in range(3)]


def gcd_degree(r1, r2):
    """min over three random y0 of deg gcd_x(F(x, y0), G(x, y0)): > 0 iff F, G share a factor
    involving x (by symmetry every common factor does), up to a chance <= (288/65536)^3."""
    return min(pgcd_deg(specialise(r1, y0), specialise(r2, y0)) for y0 in Y0)


def decode(code):
    return [(code // 28**c) % 28 for c in range(11)]


def main():
    t0 = time.time()
    Z = np.load(f"{HERE}/clusters.npz")
    pj = json.load(open(f"{HERE}/pairs.json"))
    out = {}
    for fam in ("r4", "r5n", "r6n"):
        sel = np.flatnonzero(Z["fam"] == fam)
        stats = {"pairs": 0, "common_factor": 0, "coprime": 0, "coprime_ninth": 0,
                 "coprime_pairs_listed": []}
        clusters = []
        for i in sel:
            ids = [int(v) for v in str(Z["ids"][i]).split(",")]
            logs = decode(int(Z["code"][i]))
            nonzero = [v for v in logs if v != 27]
            ninth = all(v % 9 == 0 for v in nonzero)
            q27 = all(v % 27 == 0 for v in nonzero)
            rel = []
            for a, b in itertools.combinations(ids, 2):
                d = gcd_degree(a, b)
                stats["pairs"] += 1
                if d > 0:
                    stats["common_factor"] += 1
                else:
                    stats["coprime"] += 1
                    stats["coprime_ninth"] += int(ninth)
                    if len(stats["coprime_pairs_listed"]) < 400:
                        stats["coprime_pairs_listed"].append([a, b, logs])
                rel.append([a, b, d])
            clusters.append({"ids": ids, "logs": logs, "ninth": ninth, "q27": q27, "gcd_degrees": rel})
        stats["exp_independent"] = pj[fam]["full_pairs_exp"]
        out[fam] = {"stats": stats, "clusters": clusters}
        print(fam, {k: v for k, v in stats.items() if k != "coprime_pairs_listed"}, round(time.time() - t0, 1), flush=True)
        for c in clusters:
            if c["ninth"]:
                print("   ninth cluster", c["ids"], c["logs"], [r[2] for r in c["gcd_degrees"]][:10], flush=True)
    json.dump(out, open(f"{HERE}/gcd_clusters.json", "w"))
    print("done", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
