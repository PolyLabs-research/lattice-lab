"""Step 6: is 4850's 3-orbit solution mod 9 (step 5) special?  Calibration of the minimal unit support.

Null model: the obstruction digit d of a ninth-power rule is uniform on the 10-dimensional space of
symmetric scaling-odd functions (class (1,6) = 0); target log_t = 3 d (mod 9).  Same allowance as for
4850: units may vanish on the three line-explained classes (0,1), (1,1), (1,2).  We compute the
distribution of the minimal number of direction orbits T (V subset T) with
      sum_{O in T} ell_O Phi_O = -3 d   (mod 9)   on the classes outside V and (1,6),
and also the same for the mod-171 (F(2^9)-valued) problem with a uniform random 19-part.
Also: the real ninth-power rules of radius <= 5 (step 3) with their own cyclotomic classes.
Writes step6_calib.json.
"""
import itertools
import json
import time

import numpy as np

import sbasis
import zsolve
from step5_support import Phi_matrix, ORB_VECS

P9, P19 = Phi_matrix(9), Phi_matrix(19)


def min_orbits(t9, t19, allowed_V, mods=("9",), cap=11):
    best = None
    for vsize in range(len(allowed_V) + 1):
        for V in itertools.combinations(allowed_V, vsize):
            cls = [c for c in range(11) if c not in V and c != 6]
            rest = [o for o in range(11) if o not in V]
            for tsize in range(0, 12 - vsize):
                tot = vsize + tsize
                if (best is not None and tot >= best) or tot > cap:
                    break
                hit = False
                for Textra in itertools.combinations(rest, tsize):
                    T = list(V) + list(Textra)
                    ok = True
                    if "9" in mods:
                        A = P9[np.ix_(T, cls)].T if T else np.zeros((len(cls), 0), dtype=np.int64)
                        ok = zsolve.solvable(A, [-t9[c] for c in cls], 3, 2)
                    if ok and "19" in mods:
                        A = P19[np.ix_(T, cls)].T if T else np.zeros((len(cls), 0), dtype=np.int64)
                        ok = zsolve.solvable(A, [-t19[c] for c in cls], 19, 1)
                    if ok:
                        hit = True
                        break
                if hit:
                    best = tot if best is None else min(best, tot)
                    break
    return best


def random_digit(rng):
    S = sbasis.S_matrix()
    eps = rng.integers(0, 3, 11)
    eps[6] = 0
    return (eps @ S) % 3


if __name__ == "__main__":
    t0 = time.time()
    rng = np.random.default_rng(2026)
    allowed = [0, 1, 2]  # classes (0,1), (1,1), (1,2)
    res = {"ninth_mod9": [], "ninth_mod171": [], "cube_mod9": []}
    NS = 300
    for i in range(NS):
        d = random_digit(rng)
        t9 = (3 * d) % 9
        t19 = rng.integers(0, 19, 11)
        t19[6] = 0
        res["ninth_mod9"].append(min_orbits(t9, t19, allowed, ("9",)))
        if i < 100:
            res["ninth_mod171"].append(min_orbits(t9, t19, allowed, ("9", "19")))
            # a cube-level target: log_t mod 9 with digit1 random too
            d1 = random_digit(rng)
            res["cube_mod9"].append(min_orbits((d1 + 3 * d) % 9, t19, allowed, ("9",)))
    summ = {}
    for k, v in res.items():
        h = {int(x): int(sum(1 for y in v if y == x)) for x in sorted(set(v))}
        summ[k] = dict(n=len(v), hist=h, frac_le3=float(np.mean([x <= 3 for x in v])),
                       frac_le2=float(np.mean([x <= 2 for x in v])))
        print(k, summ[k])
    # the ninth-power rules of radius <= 5 (zero-free), with V allowed on their own cyclotomic classes
    import tlib
    from step5_support import logt_classes, cyclotomic_lines
    st3 = json.load(open("step3_census.json"))
    real = []
    for x in st3["cube"]:
        if "w2" not in x:
            continue
        n, r = x["id"], x["radius"]
        t9 = logt_classes(n, r, 9)
        t19 = logt_classes(n, r, 19)
        cyc = [c for c, e in enumerate(cyclotomic_lines(n, r)) if e and c != 6]
        real.append(dict(id=n, explained=x["nine_explained"], w2=x["w2"], cyclotomic=cyc,
                         min9=min_orbits(t9, t19, cyc, ("9",)), min171=min_orbits(t9, t19, cyc, ("9", "19"))))
        print(real[-1])
    out = dict(summary=summ, raw=res, real_r5=real, seconds=round(time.time() - t0, 1))
    json.dump(out, open("step6_calib.json", "w"), indent=1, default=int)
    print("done", out["seconds"], "s")
