"""The Lean proofs (proofs/): the identities file is generated from the atlas code, so it must
match what the generator writes now; and every certificate must hold over the integers modulo
the relations x xi = 1, y yi = 1 and 2 = 0, which is what Lean's `ring` checks."""

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


def test_every_certificate_closes_its_identity():
    g = _generator()
    for name, _, lhs, rhs in g.IDENTITIES:
        left, right = g._unfold(lhs), g._unfold(rhs)
        q1, q2, Q = g.certificate(left, right)
        residue = sp.expand(left - right - q1 * (g.X * g.XI - 1) - q2 * (g.Y * g.YI - 1) - 2 * Q)
        assert residue == 0, name
