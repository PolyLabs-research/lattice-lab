"""
Calibration of the two-rule relation search (search.py) with M1 restricted to radius <= 4 and
M2 over radius <= 5, in mode "off" (the 8 classes i = 1..8) and "all" (10 free classes):
  - the 125 ninth-power rules of radius <= 6 (the dossier's records),
  - random rules of radius 6 (non-confined), random cube-confined radius-6 rules (not ninth),
    random radius-5 rules.
For each rule: number of hits, of non-exact ("genuine") hits, and of genuine hits not passing
through a multiple of 4850 or of the rule itself. This measures (b) vacuity and the coverage of
the relation idea on rules whose confinement is explained. For each rule the hits are examined in
random order until three "clean" ones (non-exact and not through a Laurent multiple of 4850 or
of the rule itself) are found; each examined non-exact hit is verified by eigenvalues.

    python calib.py   -> calib.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext6  # noqa: E402
import patterns  # noqa: E402
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
F4850 = RT.expset(4850)


def analyse(n, mode, m1max=1 << 15):
    f = RT.expset(n)
    F = tables.logs513(f)
    if (F[S.MODES[mode]] < 0).any():
        return None
    hits = S.index(mode).search(F, m1max=m1max, max_hits=20000)
    small = RT.radius_of(n) <= 5
    cache = {}

    def through(m):
        if m not in cache:
            g = C.rule(m, 5)
            cache[m] = RT.divides(F4850, g) or (small and RT.divides(f, g))
        return cache[m]

    rng = np.random.default_rng(n)
    order = rng.permutation(len(hits)) if hits else []
    gen, gen_clean, checked, ver = 0, 0, 0, True
    examples = []
    for idx in order:  # stop after 3 clean (non-exact, not via 4850 or self) hits
        gp, dp, m1, m2 = hits[idx]
        checked += 1
        if RT.exact_kind(f, gp, dp, m1, m2):
            continue
        gen += 1
        ev = RT.eig_classes(f, gp, dp, m1, m2)
        ver = ver and all(ev[c] for c in S.MODES[mode])
        if not (through(m1) or through(m2)):
            gen_clean += 1
            examples.append((gp, dp, m1, m2))
            if gen_clean >= 3:
                break
    return {"hits": len(hits) if len(hits) < 20000 else ">=20000", "checked": checked, "genuine_seen": gen,
            "clean_found": gen_clean, "verified": ver, "examples": examples}


def random_sets(seed=1):
    rng = np.random.default_rng(seed)
    t27 = C.log_table()
    c5 = ext6.coords5()
    c6 = ext6.coords6_extra()
    r6, cube6 = [], []
    for j in rng.choice(np.arange(1, 128), size=12, replace=False):
        lg = t27[c5 ^ c6[:, j: j + 1]]
        ok8 = (lg[S.MODES["off"]] != 255).all(axis=0)
        cube = ((lg == 255) | (lg % 3 == 0)).all(axis=0) & ~((lg == 255) | (lg % 9 == 0)).all(axis=0)
        idx = rng.choice(np.flatnonzero(ok8), size=3, replace=False)
        r6 += [int(i + (j << 21)) for i in idx]
        ci = np.flatnonzero(cube & ok8)
        cube6 += [int(i + (j << 21)) for i in rng.choice(ci, size=min(4, len(ci)), replace=False)]
    L = tables.L5()
    ok5 = (L[S.MODES["off"]] >= 0).all(axis=0)
    r5 = [int(i) for i in rng.choice(np.flatnonzero(ok5[1 << 15:]) + (1 << 15), 30, replace=False)]
    return r6, cube6, r5


def main():
    recs = patterns.records()
    r6, cube6, r5 = random_sets()
    groups = {"ninth125": [(i, e) for i, _, e in recs], "random6": [(i, None) for i in r6],
              "cube6": [(i, None) for i in cube6], "random5": [(i, None) for i in r5]}
    out = {}
    t0 = time.time()
    for g, items in groups.items():
        out[g] = []
        for n, e in items:
            row = {"rule": n, "explained": e}
            for mode in ("off", "all"):
                row[mode] = analyse(n, mode)
            out[g].append(row)
            print(g, n, e, {m: (row[m] and (row[m]["hits"], row[m]["clean_found"]))
                            for m in ("off", "all")}, f"{time.time() - t0:.0f}s", flush=True)
        json.dump(out, open(os.path.join(HERE, "calib.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
