"""
One pass over the whole radius-6 square family at m = 37 (2^28 rules, ids as in census.py), collecting
everything the calibration needs, per family:

    r4   = ids 1 .. 2^15 - 1           (the radius-4 family, 32,767 rules)
    r5n  = ids 2^15 .. 2^21 - 1        (the new rules of radius 5, 2,064,384)
    r6n  = ids 2^21 .. 2^28 - 1        (the new rules of radius 6, 266,338,304)

Outputs (in this directory):
    sweep_stats.npz   marg[fam]  (11, 28) counts of log mod 27 per class (symbol 27 = zero value)
                      ind9[fam]  (2048,)  counts of the 11-bit vector "class c is a ninth power or 0"
                      ind3[fam]  (2048,)  the same for cubes
    h9_hist.npz       h9_<fam>: (9^8,) counts of the mod-9 pattern of the eight generic classes
                      (census indices 2,3,4,5,7,8,9,10), rules whose axis and diagonal are ninth-OK;
                      h9all_<fam>: the same over all rules of the family
    cubes.npz         ids and 11 logs mod 27 of every cube-confined rule (zeros allowed)
    code27.npy        int64 per rule id: the 11 class logs mod 27 in base 28 (27 = zero); temporary,
                      read by pairs.py and deleted afterwards (2 GB)

Independent of the census's own code path only in the bookkeeping; the field and the log table are
census.py's (checked against the registered counts: 110/21/4 at radius 4, 415/21/3 new at radius 5,
23,722/83/29 new at radius 6).
"""
from __future__ import annotations

import sys
import time

import numpy as np

sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import census  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
GEN = [2, 3, 4, 5, 7, 8, 9, 10]  # the eight generic classes (i = 1..8); 0 axis, 1 diagonal, 6 forced
NB = 9**8
FAMS = ("r4", "r5n", "r6n")


def ocoords(orbit, zeta, chars):
    out = []
    for j, k in chars:
        v = 0
        for p, q in census.points(orbit):
            v ^= zeta[(p * j + q * k) % census.M]
        out.append(census.coord(v))
    return np.array(out, dtype=np.uint32)


def main():
    t0 = time.time()
    zeta = [census.power(2, e) for e in range(census.M)]
    chars = census.characters()
    orbs = census.orbits(6)
    assert len(orbs) == 28 and census.orbits(5) == orbs[:21] and census.orbits(4) == orbs[:15]
    low = 21
    base = np.zeros((11, 1 << low), dtype=np.uint32)
    for i, o in enumerate(orbs[:low]):
        base[:, 1 << i: 2 << i] = base[:, : 1 << i] ^ ocoords(o, zeta, chars)[:, None]
    high = [ocoords(o, zeta, chars) for o in orbs[low:]]
    table = census.log_table()
    print("setup", round(time.time() - t0, 1), flush=True)

    marg = {f: np.zeros((11, 28), dtype=np.int64) for f in FAMS}
    ind9 = {f: np.zeros(2048, dtype=np.int64) for f in FAMS}
    ind3 = {f: np.zeros(2048, dtype=np.int64) for f in FAMS}
    h9 = {f: np.zeros(NB, dtype=np.int32) for f in FAMS}
    h9all = {f: np.zeros(NB, dtype=np.int32) for f in FAMS}
    zero_gen = {f: 0 for f in FAMS}
    cube_ids, cube_logs = [], []
    code_mm = np.lib.format.open_memmap(f"{HERE}/code27.npy", mode="w+", dtype=np.int64, shape=(1 << 28,))
    pow9 = (9 ** np.arange(8)).astype(np.int64)
    pow28 = (28 ** np.arange(11)).astype(np.int64)
    lo_ids = np.arange(1 << low, dtype=np.int64)

    for hi in range(128):
        off = np.zeros(11, dtype=np.uint32)
        for i, v in enumerate(high):
            if hi >> i & 1:
                off ^= v
        logs = table[base ^ off[:, None]]  # (11, 2^21) uint8
        zero = logs == census.ZERO
        sym = np.where(zero, 27, logs).astype(np.int64)
        code_mm[hi << low: (hi + 1) << low] = pow28 @ sym
        ok9 = zero | (logs % 9 == 0)
        ok3 = zero | (logs % 3 == 0)
        bits = (1 << np.arange(11))[:, None]
        i9 = (ok9 * bits).sum(axis=0)
        i3 = (ok3 * bits).sum(axis=0)
        r9 = np.where(zero, 0, logs % 9).astype(np.int64)
        code9 = pow9 @ r9[GEN]
        zg = zero[GEN].any(axis=0)
        ad = ok9[0] & ok9[1]
        if hi == 0:
            masks = {"r4": (lo_ids >= 1) & (lo_ids < 1 << 15), "r5n": lo_ids >= 1 << 15}
        else:
            masks = {"r6n": np.ones(1 << low, dtype=bool)}
        for fam, mk in masks.items():
            for c in range(11):
                marg[fam][c] += np.bincount(sym[c][mk], minlength=28)
            ind9[fam] += np.bincount(i9[mk], minlength=2048)
            ind3[fam] += np.bincount(i3[mk], minlength=2048)
            h9all[fam] += np.bincount(code9[mk], minlength=NB)
            h9[fam] += np.bincount(code9[mk & ad], minlength=NB)
            zero_gen[fam] += int((zg & mk).sum())
        cmask = np.all(ok3, axis=0)
        if hi == 0:
            cmask &= lo_ids >= 1
        idx = np.flatnonzero(cmask)
        cube_ids.append((hi << low) | idx)
        cube_logs.append(logs[:, idx].T.copy())
        if hi % 16 == 0:
            print("chunk", hi, round(time.time() - t0, 1), flush=True)
    code_mm.flush()
    del code_mm
    np.savez(f"{HERE}/sweep_stats.npz",
             **{f"marg_{f}": marg[f] for f in FAMS}, **{f"ind9_{f}": ind9[f] for f in FAMS},
             **{f"ind3_{f}": ind3[f] for f in FAMS},
             zero_gen=np.array([zero_gen[f] for f in FAMS]))
    np.savez_compressed(f"{HERE}/h9_hist.npz", **{f"h9_{f}": h9[f].astype(np.uint16) for f in FAMS},
                        **{f"h9all_{f}": h9all[f].astype(np.uint16) for f in FAMS})
    np.savez(f"{HERE}/cubes.npz", ids=np.concatenate(cube_ids), logs=np.concatenate(cube_logs))
    # the registered counts
    ids = np.concatenate(cube_ids)
    L = np.concatenate(cube_logs)
    z = L == census.ZERO
    for name, lo, hi_ in (("r4", 1, 1 << 15), ("r5n", 1 << 15, 1 << 21), ("r6n", 1 << 21, 1 << 28)):
        m = (ids >= lo) & (ids < hi_)
        c = {q: int(np.all(z[m] | (L[m] % q == 0), axis=1).sum()) for q in (3, 9, 27)}
        print(name, c, "zero at a generic class:", zero_gen[name], flush=True)
    print("done", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
