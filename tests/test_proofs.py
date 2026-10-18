"""The Lean proofs (proofs/): the identities and rules files are generated from the atlas code,
so they must match what the generator writes now; and every certificate must hold over the
integers modulo the relations x xi = 1, y yi = 1 and 2 = 0, which is what Lean's `ring` checks."""

import importlib.util
from pathlib import Path

import sympy as sp

PROOFS = Path(__file__).resolve().parent.parent / "proofs"


def _generator():
    spec = importlib.util.spec_from_file_location("lean_generate", PROOFS / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_identities_file_is_what_the_generator_writes():
    generated = _generator().render()
    assert (PROOFS / "LatticeProofs" / "Identities.lean").read_text() == generated


def test_the_rules_file_is_what_the_generator_writes():
    generated = _generator().render_rules()
    assert (PROOFS / "LatticeProofs" / "Rules.lean").read_text() == generated


def test_each_rule_neighbourhood_is_its_polynomial():
    g = _generator()
    for name in g.RULES:
        assert g.laurent(g.offsets(name)) == g.P[name], name


def test_every_certificate_closes_its_identity():
    g = _generator()
    for name, _, lhs, rhs in g.IDENTITIES:
        left, right = g._unfold(lhs), g._unfold(rhs)
        q1, q2, Q = g.certificate(left, right)
        residue = sp.expand(left - right - q1 * (g.X * g.XI - 1) - q2 * (g.Y * g.YI - 1) - 2 * Q)
        assert residue == 0, name


def test_the_period_theorems_agree_with_the_atlas():
    """Periods.lean's three theorems, checked against eigen.py at odd sizes: a check that the
    formal definitions mean what the atlas means."""
    _generator()  # puts the round-3 atlas on sys.path
    import math

    import atlas3
    import eigen

    def period(shells, m):
        return eigen.odd_part(atlas3.polynomial("square", shells), m) if m > 1 else 1

    for m in range(3, 62, 2):
        n4, n4self = period(("N4",), m), period(("N4", "self"), m)
        assert period(("N4", "K8", "C4"), m) == n4 // math.gcd(n4, 3), m
        assert period(("A4", "K8", "C4", "self"), m) == n4self // math.gcd(n4self, 3), m
        assert period(("C4", "self"), m) == period(("N4", "self"), m // math.gcd(m, 3)), m


def _twist(m):
    """The least k with 3 = +-2^k mod m, if there is one."""
    return next((k for k in range(1, 2 * m) if (2**k - 3) % m == 0 or (2**k + 3) % m == 0), None)


def test_the_triangle_theorems_agree_with_the_atlas():
    """Periods.lean's triangle theorems, checked against the atlas. On the triangular torus of
    odd side m (Z^2 / m Z^2, two cells per unit cell, the atlas's own matrix entries), E and
    VO + T13 have period exactly 2 P(s); and wherever 3 = +-2^k mod m, P(s) for VO + T13 is
    P(s_E) / gcd(P(s_E), 1 + 2^k)."""
    _generator()
    import math

    import atlas3
    import eigen
    import sympy
    from lattices import GroupRing, Matrix

    def matrix(shells, m):
        ring = GroupRing((m, 0), (0, m))
        entries = []
        for part in atlas3._triangle_entries(shells):
            e = ring.zero()
            for i, j in part:
                e[ring.index(i, j)] += 1
            entries.append(e % 2)
        uu, ud, du, dd = entries
        return Matrix(ring, [[uu, ud], [du, dd]])

    def repeats(M, p, t=2):
        return M.power(t + p) == M.power(t)

    def s_period(shells, m):
        return eigen.odd_part(atlas3.polynomial("triangle", shells), m)

    for m in range(3, 14, 2):
        for shells in [("E",), ("VO", "T13")]:
            M, P = matrix(shells, m), 2 * s_period(shells, m)
            assert repeats(M, P), (shells, m)
            assert not any(repeats(M, P // q) for q in sympy.primefactors(P)), (shells, m)
    twisted = 0
    for m in range(5, 102, 2):
        k = _twist(m)
        if k is None:
            continue
        twisted += 1
        pe = s_period(("E",), m)
        assert s_period(("VO", "T13"), m) == pe // math.gcd(pe, 1 + 2**k), m
    assert twisted > 20
