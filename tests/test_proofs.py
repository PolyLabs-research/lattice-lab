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
