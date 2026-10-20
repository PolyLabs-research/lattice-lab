"""The two ways of counting a bivariate bicycle code's logical qubits (examples/qec-bb/bb.py), on
the development sizes only (l, m <= 4): the registered study's sizes are kept out of the tests."""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))

import bb  # noqa: E402


def test_the_character_count_agrees_with_linear_algebra_on_small_tori():
    rng = random.Random(7)
    for ell in range(1, 5):
        for m in range(1, 5):
            for _ in range(40):
                A = [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(1, 4))]
                B = [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(1, 4))]
                assert bb.k_characters(A, B, ell, m) == bb.k_linalg(A, B, ell, m), (ell, m, A, B)


def test_extreme_codes():
    # A = B = 0 keeps every qubit pair; A = 1 kills them all
    assert bb.k_linalg([], [], 3, 4) == bb.k_characters([], [], 3, 4) == 2 * 12
    assert bb.k_linalg([(0, 0)], [], 3, 4) == bb.k_characters([(0, 0)], [], 3, 4) == 0


def test_at_odd_sizes_every_term_is_a_common_zero():
    # L = F at odd sizes, so each character contributes 0 or 1: A and B both vanish there
    A, B = [(1, 0), (0, 1), (0, 0)], [(2, 0), (0, 2), (0, 0)]
    terms = bb.local_terms(A, B, 3, 3)
    assert terms and all(t == 1 for _, t in terms)
    assert 2 * len(terms) == bb.k_linalg(A, B, 3, 3)


def test_the_fields_hold_primitive_roots_of_unity():
    for N in (1, 3, 5, 7, 9, 15, 21):
        F = bb.Field(N)
        assert F.pow(F.zeta, N) == 1
        assert all(F.pow(F.zeta, e) != 1 for e in range(1, N))
