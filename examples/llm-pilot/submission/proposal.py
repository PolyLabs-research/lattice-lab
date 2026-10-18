"""
Numerical check of the mechanism behind the hexagon law's 2-part (proposal.md).

    /home/user/pilot-sandbox/python proposal.py

Let n = 2^v m, m odd, v >= 1, G the atlas's hexagonal torus of side n and H1 the hexagon's parity
rule. The checks, each printed with whether it held:

  1. The embedding. iota(a, b) = (2^v a, 2^v b) maps G' = Z/2m x Z/m, with
     omega'(q, r) = (q + 2r mod 2m, r mod m), injectively onto 2^v G, and
     iota(omega'(d)) = omega(2^v d).
  2. The reduction. P / gcd(P, 2^v) = P(G'), where P is H1's period on G and P(G') on G'.
  3. The Jordan block on G'. psi1(a, b) = zeta^(a + b) and psi2 = psi1 * [a even] satisfy
     adj psi1 = lam psi1 and adj psi2 = lam psi2 + mu psi1, with lam, mu nonzero (tools'
     check_jordan), and zeta^3 lam = (1 + zeta)(1 + zeta^2)(1 + zeta^3),
     zeta^2 mu = (1 + zeta)(1 + zeta^3). At m = 3 the block degenerates (lam = mu = 0).
  4. The consequences. P(G') = 2 P(m), and P = 2^(v+1) P(m), at every (m, v) small enough to
     run; at m = 3 the 2-part is smaller, as the law's hypothesis m >= 5 says.
"""

from __future__ import annotations

import math
import os
import random
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools"))


# --- gf2.py needs sympy only to find an irreducible factor of the m-th cyclotomic polynomial
# over GF(2). The pilot's interpreter has no sympy, so when it is missing we supply that one
# function in pure Python (equal-degree factorisation) and leave the rest of gf2.Field as is.

def _pmod(a: int, b: int) -> int:
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        a ^= b << (a.bit_length() - 1 - db)
    return a


def _pmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a, b = a << 1, b >> 1
    return r


def _pdiv(a: int, b: int) -> int:
    q, db = 0, b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        s = a.bit_length() - 1 - db
        q, a = q ^ (1 << s), a ^ (b << s)
    return q


def _pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, _pmod(a, b)
    return a


def _cyclotomic_mod2(m: int) -> int:
    def zdiv(a, b):  # exact division of integer polynomials, lowest degree first
        a, q = a[:], [0] * (len(a) - len(b) + 1)
        for i in range(len(q) - 1, -1, -1):
            c = a[i + len(b) - 1] // b[-1]
            q[i] = c
            for j, bj in enumerate(b):
                a[i + j] -= c * bj
        assert not any(a)
        return q

    phi = {}
    for k in (k for k in range(1, m + 1) if m % k == 0):
        p = [-1] + [0] * (k - 1) + [1]
        for j in (j for j in range(1, k) if k % j == 0):
            p = zdiv(p, phi[j])
        phi[k] = p
    return sum((c % 2) << i for i, c in enumerate(phi[m]))


def _modulus(m: int) -> int:
    f, d = _cyclotomic_mod2(m), next(k for k in range(1, m + 1) if pow(2, k, m) == 1 % m)
    rng, stack, out = random.Random(m), [f], []
    while stack:
        g = stack.pop()
        if g.bit_length() - 1 == d:
            out.append(g)
            continue
        while True:  # the trace map splits g with probability about 1/2
            t, s = 0, rng.randrange(2, 1 << (g.bit_length() - 1))
            for _ in range(d):
                t, s = t ^ s, _pmod(_pmul(s, s), g)
            h = _pgcd(g, t)
            if 0 < h.bit_length() - 1 < g.bit_length() - 1:
                stack += [h, _pdiv(g, h)]
                break
    return min(out)


try:
    import sympy  # noqa: F401

    SHIM = False
except ModuleNotFoundError:
    sys.modules["sympy"] = types.ModuleType("sympy")
    SHIM = True

import gf2  # noqa: E402
from gf2 import Field  # noqa: E402
from tori import H1, check_jordan, hexagon, period, square, torus  # noqa: E402

if SHIM:
    gf2._modulus = _modulus

RESULTS: list[bool] = []


def report(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append(ok)
    print(f"  [{'held' if ok else 'FAILED'}] {label}" + (f": {detail}" if detail else ""))


def sub_torus(m: int):
    """G' = Z/2m x Z/m with omega'(q, r) = (q + 2r mod 2m, r mod m) (Lean: hexSubHom m)."""
    return torus(2 * m, m, lambda d: (d[0] + 2 * d[1], d[1]))


def check_embedding(m: int, v: int) -> None:
    n = 2**v * m
    G, S, N = hexagon(n), sub_torus(m), 2**v

    def iota(w):
        return ((N * w[0]) % G.a, (N * w[1]) % G.b)

    image = {iota(w) for w in S.cells()}
    sub = {((N * x[0]) % G.a, (N * x[1]) % G.b) for x in G.cells()}  # 2^v G
    box = [(q, r) for q in range(-6, 7) for r in range(-6, 7)]
    compat = all(iota(S.image(d)) == G.image((N * d[0], N * d[1])) for d in box)
    report(
        f"m={m} v={v}: iota injective onto 2^v G, iota(omega'(d)) = omega(2^v d)",
        len(image) == len(S.cells()) and image == sub and compat,
        f"|G'| = {len(S.cells())}, |2^v G| = {len(sub)}",
    )


def check_block(m: int, expect_ok: bool) -> None:
    F = Field(m)
    z = F.zeta
    assert F.pow(z, m) == 1 and all(F.pow(z, k) != 1 for k in range(1, m))

    def psi1(w):
        return F.pow(z, w[0] + w[1])

    def psi2(w):
        return psi1(w) if w[0] % 2 == 0 else 0

    lam = F.sum(F.pow(z, e) for e in (1, -1, 2, -2, 3, -3))
    mu = F.sum(F.pow(z, e) for e in (1, -1, 2, -2))
    res = check_jordan(sub_torus(m), H1, psi1, psi2, lam, mu, F)

    def one_plus(k):
        return F.add(1, F.pow(z, k))

    lam_closed = F.mul(F.pow(z, 3), lam) == F.mul(F.mul(one_plus(1), one_plus(2)), one_plus(3))
    mu_closed = F.mul(F.pow(z, 2), mu) == F.mul(one_plus(1), one_plus(3))
    relations = not res["eigen_fails_at"] and not res["block_fails_at"]
    if expect_ok:
        report(f"m={m}: Jordan block on G' (check_jordan, F(2^{F.degree}))", res["ok"],
               f"lam != 0: {res['lam_nonzero']}, mu != 0: {res['mu_nonzero']}")
    else:
        report(f"m={m}: block relations hold but degenerate (lam = mu = 0)",
               relations and not res["lam_nonzero"] and not res["mu_nonzero"])
    report(f"m={m}: zeta^3 lam = (1+z)(1+z^2)(1+z^3), zeta^2 mu = (1+z)(1+z^3)",
           lam_closed and mu_closed)


def check_periods(m: int, vs: list[int], law: bool) -> None:
    Pm = period(square(m), H1)
    PS = period(sub_torus(m), H1)
    if law:
        report(f"m={m}: P(G') = 2 P(m)", PS == 2 * Pm, f"P(m) = {Pm}, P(G') = {PS}")
    else:
        report(f"m={m}: P(G') = P(m) (no doubling)", PS == Pm, f"P(m) = {Pm}, P(G') = {PS}")
    for v in vs:
        n = 2**v * m
        t0 = time.time()
        P = period(hexagon(n), H1)
        dt = time.time() - t0
        report(f"m={m} v={v} n={n}: P / gcd(P, 2^v) = P(G')", P // math.gcd(P, 2**v) == PS,
               f"P = {P}")
        if law:
            report(f"m={m} v={v} n={n}: P = 2^(v+1) P(m)", P == 2 ** (v + 1) * Pm,
                   f"{P} = 2^{v + 1} * {Pm}  ({dt:.1f}s)")
        else:
            report(f"m={m} v={v} n={n}: P = 2^v P(m), below the law's 2^(v+1)",
                   P == 2**v * Pm, f"{P} = 2^{v} * {Pm}")


def main() -> int:
    print("Hexagon law's 2-part: numerical check of the mechanism")
    if SHIM:
        print("(sympy is not installed: gf2's cyclotomic factor is computed in pure Python)")
    print("\n1. The embedding G' -> 2^v G")
    for m, v in [(3, 1), (5, 1), (5, 2), (5, 3), (7, 1), (7, 2), (9, 2), (15, 1)]:
        check_embedding(m, v)
    print("\n3. The Jordan block on G'")
    for m in [5, 7, 9, 11, 13, 15, 17, 21, 25, 27]:
        check_block(m, expect_ok=True)
    check_block(3, expect_ok=False)
    print("\n2 and 4. Periods")
    check_periods(5, [1, 2], law=True)
    check_periods(7, [1, 2], law=True)
    check_periods(9, [1], law=True)
    check_periods(11, [1], law=True)
    check_periods(13, [1], law=True)
    check_periods(3, [1, 2, 3], law=False)
    held = sum(RESULTS)
    print(f"\n{held} of {len(RESULTS)} checks held.")
    return 0 if held == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
