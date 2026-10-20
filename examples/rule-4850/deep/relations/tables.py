"""
Log-mod-513 class vectors for every symmetric square rule of radius <= 5 at m = 37.

The census method (census37.class_logs) with a full discrete-log table instead of mod 27:
a rule's value at a class representative is the XOR of its orbits' values, so all 2^21 rules'
values come from the 21 orbits' by doubling. Each value lies in F(2^18); it is reduced to
18-bit coordinates and looked up in a table of discrete logs to the generator of
pilot-37c-round2/scratch/f18.py. L mod 513 is the coordinate on F(2^18)*/F(2^9)*.

    python tables.py      # builds logtab.npy (full logs, -1 at 0) and L5.npy ((11, 2^21) int16)

Library use: logs513(f) for one rule given as an exponent set (any radius).
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")

import census37 as C  # noqa: E402
import f18  # noqa: E402

M = 37
N18 = 2**18 - 1
CHARS = C.characters()  # census class order
TAB = os.path.join(HERE, "logtab.npy")
L5F = os.path.join(HERE, "L5.npy")


def log_table() -> np.ndarray:
    if os.path.exists(TAB):
        return np.load(TAB)
    t = f18.full_log_table().astype(np.int32)  # -1 at the zero coordinate
    np.save(TAB, t)
    return t


def coords_of(f) -> np.ndarray:
    return np.array([C.coord(C._value(f, j, k)) for j, k in CHARS], dtype=np.int64)


def full_logs(f) -> np.ndarray:
    """full discrete logs (mod 2^18-1) at the 11 class representatives, -1 for zero."""
    return log_table()[coords_of(f)].astype(np.int64)


def logs513(f) -> np.ndarray:
    lg = full_logs(f)
    return np.where(lg < 0, -1, lg % 513)


def build_L5(radius: int = 5) -> np.ndarray:
    orbs = C.orbits(radius)
    values = np.zeros((len(CHARS), 1 << len(orbs)), dtype=np.uint32)
    for i, o in enumerate(orbs):
        ov = np.array([C.coord(C._value(C.points(o), j, k)) for j, k in CHARS], dtype=np.uint32)
        values[:, 1 << i: 2 << i] = values[:, : 1 << i] ^ ov[:, None]
    tab = log_table()
    lg = tab[values]
    out = np.where(lg < 0, -1, lg % 513).astype(np.int16)
    return out


def L5() -> np.ndarray:
    if os.path.exists(L5F):
        return np.load(L5F)
    a = build_L5(5)
    np.save(L5F, a)
    return a


if __name__ == "__main__":
    t0 = time.time()
    tab = log_table()
    print("log table", time.time() - t0, "s; generator", f18.generator())
    a = L5()
    print("L5", a.shape, time.time() - t0, "s")
    # checks against the dossier
    r4850 = C.rule(4850, 5)
    v = logs513(r4850)
    print("4850 logs mod 513:", v.tolist())
    assert v.tolist() == [18, 198, 9, 234, 162, 63, 0, 495, 9, 387, 180]
    assert a[:, 4850].tolist() == v.tolist()
    # mod 27 against the census tool (census37.class_logs(4), own mod-27 table)
    c4 = C.class_logs(4)
    m27 = np.where(a[:, : 1 << 15] < 0, 255, a[:, : 1 << 15] % 27)
    assert (m27 == c4).all(), "mod-27 mismatch with census37"
    print("mod 27 agrees with census37.class_logs(4) on all 32768 rules")
    # class (1,6) is always F(2^9)-valued
    nz = a[6] >= 0
    assert (a[6][nz] == 0).all()
    print("class (1,6) is 0 mod 513 for every zero-free radius-5 value: ok")
    zero_free = (a >= 0).all(axis=0)
    print("zero-free rules (nonzero at all 11 classes):", int(zero_free.sum()))
