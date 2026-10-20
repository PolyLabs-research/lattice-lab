"""
Independent check of the discrete-log pipeline (tables.py) against
examples/linear-atlas-3/eigen.py: odd_part(rule, 37), the lcm of the multiplicative orders of all
nonzero eigenvalues computed in eigen.py's own field arithmetic. From our class logs L (full,
mod 2^18 - 1) the same lcm is lcm over classes of (2^18-1)/gcd(L, 2^18-1).

    python checks.py
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/user/lattice-lab/examples/linear-atlas-3")
import eigen  # noqa: E402
import run_targets as RT  # noqa: E402
import tables  # noqa: E402

N18 = 2**18 - 1


def predicted(f):
    lg = tables.full_logs(f)
    out = 1
    for v in lg:
        if v >= 0:
            out = math.lcm(out, N18 // math.gcd(int(v), N18))
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    rules = [4850, 10491524, 20982139, 178279803, 482758, 8438150, 43250486, 57, 960,
             699738, 985232, 1431278, 1968276]
    rules += [int(x) for x in rng.integers(1, 1 << 21, 15)] + [int(x) for x in rng.integers(1 << 21, 1 << 28, 10)]
    bad = 0
    for n in rules:
        f = RT.expset(n)
        a, b = eigen.odd_part(f, 37), predicted(f)
        ninth = a > 0 and 29127 % a == 0
        print(n, "odd_part", a, "from logs", b, "ninth-power confined:", ninth, "OK" if a == b else "MISMATCH")
        bad += a != b
    print("mismatches:", bad)
