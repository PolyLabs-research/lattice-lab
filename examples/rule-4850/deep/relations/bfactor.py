"""
The F(2^9)-valued factor of the trio relation as an explicit group-ring element.

With h0 = 10491524 * ab and h1 = 20982139 * ab, trio.py shows that
B(c) = lambda_{h0}(27c) / lambda_{h1}(c) lies in F(2^9) at every character off the axis class.
Put B = 0 on the axis lines (j = 0 or k = 0). B is Galois-equivariant (B(2c) = B(c)^2), so its
inverse Fourier transform b(p, q) = sum_c B(c) zeta^-(pj + qk) has coefficients in GF(2); it is
D4-symmetric and, being F(2^9)-valued, invariant under the dilation by 2^9 = -6. A sparse b would
be an explicit certificate of the same kind as the half-Frobenius identities (W(x^2)O_31 =
Sh(7,5), 8 terms). We report its number of terms. Control: the same construction for
W(x^2,y^2) * t(x)t(y)t(xy)t(x/y), which must return the 8-term Sh(7,5) (up to the lines where
the unit vanishes, which we zero: there b differs from Sh(7,5) by a function supported on the
two diagonals and the axes).

    python bfactor.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_targets as RT  # noqa: E402

F = RT.F36
M = 37
ZP = RT.ZP


def vals(rules_with_dil, j, k):
    """product over (rule, dilation) of lambda_rule(d*c)."""
    v = 1
    for n, d in rules_with_dil:
        v = F.mul(v, RT.value(RT.expset(n), d * j % M, d * k % M))
    return v


def bfactor(num, den, zero):
    B = {}
    for j in range(M):
        for k in range(M):
            if zero(j, k):
                continue
            vn, vd = vals(num, j, k), vals(den, j, k)
            if vd == 0:
                if vn != 0:
                    raise ValueError("pole")
                continue
            B[(j, k)] = F.mul(vn, F.inv(vd))
    # Galois/F(2^9) checks
    assert all(F.pow(v, 512) == v for v in B.values()), "not F(2^9)-valued"
    coeffs = {}
    for p in range(M):
        for q in range(M):
            s = 0
            for (j, k), v in B.items():
                s ^= F.mul(v, ZP[(-(p * j + q * k)) % M])
            if s not in (0, 1):
                raise ValueError("coefficient not in GF(2)")
            if s:
                coeffs[(p, q)] = 1
    return coeffs


def centred(c):
    return sorted(((p if p <= 18 else p - 37), (q if q <= 18 else q - 37)) for p, q in c)


if __name__ == "__main__":
    axis = lambda j, k: j == 0 or k == 0  # noqa: E731
    diag_or_axis = lambda j, k: j == 0 or k == 0 or j == k or j == (-k) % M  # noqa: E731
    # control: W(x^2) * O31 / 1, zero on axes and diagonals (where O31 vanishes)
    cw = bfactor([(57, 2), (128, 1)], [(1, 1)], lambda j, k: False)
    print("control W(x^2)*O31:", len(cw), "terms;", centred(cw)[:40])
    for g, j6 in ((20982139, 27), (178279803, 26)):
        c = bfactor([(10491524, j6), (4, j6)], [(g, 1), (4, 1)], axis)
        pts = centred(c)
        r = max(max(abs(p), abs(q)) for p, q in pts) if pts else 0
        print(f"B for {g}: {len(c)} terms of 1369, max |coord| {r}")
        inv = all((((-6 * p) % M), ((-6 * q) % M)) in c for p, q in c)
        print("   support invariant under x -> x^-6:", inv)
