"""Vectorised eigenvalues of symmetric rules on the grid (j, k), 0 <= j, k <= 18 (the rest by sign
symmetry), with v27 (mu27 exponent, zeta27 = x) and s19 (mu19 exponent, canonical zeta19)."""
import functools
import numpy as np
import ff18 as F

R18 = 19  # grid size 0..18


def red(n):
    n %= 37
    return min(n, 37 - n)


@functools.cache
def orbit_table(radius):
    orbs = F.orbits(radius)
    ov = np.zeros((len(orbs), R18, R18), dtype=np.int64)
    for i, o in enumerate(orbs):
        for j in range(R18):
            for k in range(R18):
                ov[i, j, k] = F.orbit_value(o, j, k)
    return ov


def values(ns, radius):
    ov = orbit_table(radius)
    ns = np.asarray(ns, dtype=np.int64)
    out = np.zeros((len(ns), R18, R18), dtype=np.int64)
    for i in range(ov.shape[0]):
        bit = ((ns >> i) & 1).astype(bool)
        out[bit] ^= ov[i]
    return out


@functools.cache
def _consts():
    EXP, LOG = F.tables()
    L27 = int(LOG[F.zeta27()]) % 27
    L19 = int(LOG[F.zeta19()]) % 19
    return pow(L27, -1, 27), pow(L19, -1, 19)


def logs(vals):
    EXP, LOG = F.tables()
    return LOG[vals]  # -1 for zero


def v27(vals):
    i27, _ = _consts()
    L = logs(vals)
    return np.where(L < 0, -1, (L % 27) * i27 % 27)


def s19(vals):
    _, i19 = _consts()
    L = logs(vals)
    return np.where(L < 0, -1, (L % 19) * i19 % 19)


IDX27 = [red(27 * j) for j in range(R18)]
IDX26 = [red(26 * j) for j in range(R18)]
