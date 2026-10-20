"""Full discrete logarithms in F(2^18)* = (GF(2)[X]/m37)* (t_1 = X), and family-wide class values.

    LOG = log_table()          numpy int64 array: LOG[v] = log_g(v) for v != 0 (g = rlib.f18_generator()), -1 at 0
    family_values(radius)      (11, 2^#orbits) uint32 array of class values (census class order)
"""
import functools
import numpy as np
from rlib import *

CLASS_K = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 13]  # 0 means the axis (0,1); census order


@functools.cache
def log_table():
    g = f18_generator()
    m = m37()
    tab = np.full(1 << 18, -1, dtype=np.int64)
    x = 1
    for e in range(N18):
        tab[x] = e
        x <<= 0  # placeholder to keep the loop simple
        # multiply by g
        x = pmulmod(x, g, m)
    assert x == 1
    assert (tab[1:] >= 0).all()
    return tab


def class_value(F, k):
    return val_t1(subst_line(F, 0)) if k == 0 else val_t1(Q_dickson(F, k))


def family_values(radius):
    orbs = orbits(radius)
    vals = np.zeros((len(CLASS_K), 1 << len(orbs)), dtype=np.uint32)
    for i, o in enumerate(orbs):
        F = orbit_F(o)
        ov = np.array([class_value(F, k) for k in CLASS_K], dtype=np.uint32)
        vals[:, 1 << i: 2 << i] = vals[:, : 1 << i] ^ ov[:, None]
    return vals


def rule_class_values(n, radius):
    F = rule_F(n, radius)
    return [class_value(F, k) for k in CLASS_K]
