"""The rule-4850 deep dive's proof, rechecked by the orchestrator with its own field
(examples/qec-bb/bb.py: F(2^36) with a primitive 37th root of 1), not the investigators' code.

The chain (examples/rule-4850/deep/REPORT.md, section 3):
- the hexagon identity 4850 * (a + b) = Sh(4,0) + Sh(5,2);
- the closed form lambda * t_al t_be = W^4 off the diagonals (al = (j+k)/2, be = (j-k)/2);
- the Gauss period eta_0 = sum_{u in mu6} zeta^u satisfies eta_0^24 + eta_0^9 + 1 = 0 and has
  order 21, so it is a cube of F64*;
- the norm N = N_{F(2^18)/F64} of every off-diagonal eigenvalue is (eta(al) eta(be))^(4n(d) - 2),
  with n = (2, -1, -4, 2, -4, -1) and d = log2(be/al) mod 6, an element of F8*;
- and a nonzero lambda is a ninth power iff N(lambda) lies in F8*."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "rule-4850"))

import bb  # noqa: E402
import census  # noqa: E402

M = 37
F = bb.Field(M)  # F(2^36), zeta of order 37
Z = [F.pow(F.zeta, e) for e in range(M)]
LOG2 = {pow(2, i, M): i for i in range(36)}
MU6 = [u for u in range(1, M) if pow(u, 6, M) == 1]
MU3 = [u for u in range(1, M) if pow(u, 3, M) == 1]
N_OF_D = (2, -1, -4, 2, -4, -1)
Q = 2**18 - 1


def t(n):
    return Z[n % M] ^ Z[-n % M]


def value(f, j, k):
    v = 0
    for p, q in f:
        v ^= Z[(p * j + q * k) % M]
    return v


def norm(z):  # to F64 = F(2^36)'s subfield of order 64, from F(2^18): z * z^64 * z^4096
    return F.mul(z, F.mul(F.pow(z, 64), F.pow(z, 4096)))


def eta(x):
    v = 0
    for u in MU6:
        v ^= Z[(u * x) % M]
    return v


def f64_pow(z, e):  # exponents mod 63 on F64*
    return F.pow(z, e % 63)


def in_f8(z):
    return z != 0 and F.pow(z, 7) == 1


def test_mu_groups_and_hexagon_identity():
    assert sorted(MU6) == [1, 10, 11, 26, 27, 36] and sorted(MU3) == [1, 10, 26]
    f = census.rule(4850, 4)
    s = census.points((1, 0))  # a + b as exponents: {(±1, 0), (0, ±1)}
    prod: dict = {}
    for p, q in f:
        for r, w in s:
            prod[(p + r, q + w)] = prod.get((p + r, q + w), 0) ^ 1
    assert {e for e, c in prod.items() if c} == census.points((4, 0)) | census.points((5, 2))


def test_eta0_is_a_cube_of_order_21():
    e0 = eta(1)
    assert e0 != 0 and F.pow(e0, 63) == 1 and F.pow(e0, 7) != 1  # in F64, not in F8
    assert F.pow(e0, 24) ^ F.pow(e0, 9) ^ 1 == 0
    assert F.pow(e0, 21) == 1  # order 21: a cube of F64* that is not a ninth power


def test_closed_form_and_norm_formula_at_every_off_diagonal_character():
    f = census.rule(4850, 4)
    half = pow(2, -1, M)
    checked = 0
    for j in range(M):
        for k in range(M):
            al, be = (j + k) * half % M, (j - k) * half % M
            lam = value(f, j, k)
            if al == 0 or be == 0:
                if (j, k) != (0, 0):
                    # on the diagonals lambda = t_j t_{5j}, a ninth power too
                    assert lam == F.mul(t(j), t(5 * j)) and in_f8(norm(lam))
                continue
            w = 0
            for u in MU3:
                w ^= F.mul(t(u * al), t(be * pow(u, -1, M)))
            assert F.mul(lam, F.mul(t(al), t(be))) == F.pow(w, 4)
            n = N_OF_D[(LOG2[be] - LOG2[al]) % 6]
            assert norm(lam) == f64_pow(F.mul(eta(al), eta(be)), 4 * n - 2)
            assert in_f8(norm(lam))
            # and the criterion: lambda is a ninth power of F(2^18)* (lambda^(Q/9) = 1)
            assert F.pow(lam, Q // 9) == 1
            checked += 1
    assert checked == 36 * 36
