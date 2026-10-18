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


def test_the_atlas_tori_of_tori_lean_are_the_atlas_engines():
    """Tori.lean models the atlas's triangular torus of side n as Z/n x Z/(n/2), with
    (x, y) -> (x - y mod n, y mod n/2), and its hexagonal torus as Z/2n x Z/(n/2), with
    (q, r) -> (q + 2r mod 2n, r mod n/2). Each rule reads the negated exponents of its entries.
    These models must have the atlas engine's exact periods, and those periods must have the form
    the reduction theorems state, with the exact 2-parts of HexTwoPart.lean and TriTwoPart.lean."""
    _generator()
    import atlas3
    import eigen
    import numpy as np
    from lattices import AXIAL_STEPS

    def eventual_period(step):
        seen, power = {}, np.eye(step.shape[0], dtype=np.int64)
        for t in range(2000):
            key = np.packbits(power.astype(np.uint8)).tobytes()
            if key in seen:
                return t - seen[key]
            seen[key] = t
            power = (power @ step) % 2
        raise AssertionError("no repeat")

    def atlas_period(lattice, shells, n):
        _, step = atlas3.build(lattice, shells, n)
        seen, power = {}, step.identity()
        for t in range(2000):
            key = b"".join(np.asarray(x, dtype=np.uint8).tobytes() for r in power.e for x in r)
            if key in seen:
                return t - seen[key]
            seen[key] = t
            power = power * step
        raise AssertionError("no repeat")

    def model(group, omega, entries):
        cells = [(layer, g) for layer in range(len(entries)) for g in group]
        index = {c: i for i, c in enumerate(cells)}
        step = np.zeros((len(cells), len(cells)), dtype=np.int64)
        for layer, v in cells:
            for src, ds in enumerate(entries[layer]):
                for d in ds:
                    step[index[(src, omega(v, d))], index[(layer, v)]] += 1
        return step % 2

    def triangle(shells, n):
        group = [(a, b) for a in range(n) for b in range(n // 2)]
        uu, ud, du, dd = ([(-i, -j) for i, j in e] for e in atlas3._triangle_entries(shells))
        return model(
            group,
            lambda v, d: ((v[0] + d[0] - d[1]) % n, (v[1] + d[1]) % (n // 2)),
            [[uu, ud], [du, dd]],
        )

    def hexagon(n):
        group = [(a, b) for a in range(2 * n) for b in range(n // 2)]
        return model(
            group,
            lambda v, d: ((v[0] + d[0] + 2 * d[1]) % (2 * n), (v[1] + d[1]) % (n // 2)),
            [[list(AXIAL_STEPS)]],
        )

    def two_power(p, q):
        """a with p = 2^a q, or None."""
        a = 0
        while p % 2 == 0 and p != q:
            p, a = p // 2, a + 1
        return a if p == q else None

    for n in [6, 10, 12, 14]:
        v, m = (n & -n).bit_length() - 1, n // (n & -n)
        for shells, extra in [(("E",), 1), (("VO", "T13"), 1), (("E", "VO", "VS"), 0)]:
            p = atlas_period("triangle", shells, n)
            assert eventual_period(triangle(shells, n)) == p, (shells, n)
            a = two_power(p, eigen.odd_part(atlas3.polynomial("triangle", shells), m))
            assert a is not None and extra <= a <= v + 1, (shells, n, p)
            # TriTwoPart.lean: for E and E + VO + VS the 2-part is exactly 2^(v+1), m >= 3.
            assert shells == ("VO", "T13") or a == v + 1, (shells, n, p)
        p = atlas_period("hexagon", ("H1",), n)
        assert eventual_period(hexagon(n)) == p, n
        a = two_power(p, eigen.odd_part(atlas3.polynomial("hexagon", ("H1",)), m))
        assert a is not None and a <= v + 1, n
        # HexTwoPart.lean: the 2-part is exactly 2^(v+1) once m >= 5.
        assert m < 5 or a == v + 1, n


def test_the_xor_law_two_part_agrees_with_the_atlas():
    """TwoPart.lean: for n = 2^v m with m odd, m > 1 and v >= 1, the XOR rule B1357/S1357 and N4
    have period exactly 2^v P(m) on the square torus of side n."""
    _generator()
    import atlas3
    import numpy as np

    def period(shells, n):
        _, step = atlas3.build("square", shells, n)
        seen, power = {}, step.identity()
        for t in range(5000):
            key = np.asarray(power.e[0][0], dtype=np.uint8).tobytes()
            if key in seen:
                return t - seen[key]
            seen[key] = t
            power = power * step
        raise AssertionError("no repeat")

    for shells in [("N4", "D4"), ("N4",)]:
        for m in [3, 5, 7, 9, 11]:
            base = period(shells, m)
            for v in [1, 2]:
                assert period(shells, 2**v * m) == 2**v * base, (shells, m, v)
