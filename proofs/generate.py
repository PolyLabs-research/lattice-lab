"""
Write LatticeProofs/Identities.lean: the atlas's polynomial identities, with certificates.

    uv run python proofs/generate.py

Each identity is between Laurent polynomials over GF(2) in x and y. It is stated for x, x^-1, y,
y^-1 in any commutative ring of characteristic 2: four variables x, xi, y, yi with x * xi = 1
and y * yi = 1. That is where a rule's eigenvalues live (x, y roots of unity in a field of
characteristic 2), so a statement there is a statement about every eigenvalue at once.

The proof of each is `linear_combination q1 * hx + q2 * hy + Q * h2`. Here lhs - rhs = q1 (x xi
- 1) + q2 (y yi - 1) + 2 Q over the integers. sympy finds q1 and q2 by division by the two
relations, and Q is half the remainder. Lean's `ring` rechecks the whole equation, so nothing
here is trusted. The polynomials come from the atlas code itself (`atlas3.polynomial` and
`atlas3._triangle_entries`), so the theorems are about the rules as the experiments computed
them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "examples" / "linear-atlas-3"))

import atlas3  # noqa: E402

X, XI, Y, YI = sp.symbols("x xi y yi")
GENS = (X, XI, Y, YI)
RELATIONS = [X * XI - 1, Y * YI - 1]


def monomial(i: int, j: int) -> sp.Expr:
    return (X**i if i >= 0 else XI ** (-i)) * (Y**j if j >= 0 else YI ** (-j))


def laurent(terms) -> sp.Expr:
    """A Laurent polynomial over GF(2), given by its exponents, as a sum of monomials."""
    return (
        sp.Add(*(monomial(i, j) for i, j in sorted(terms)), evaluate=False)
        if terms
        else sp.Integer(0)
    )


def dilate(expr: sp.Expr, d: int) -> sp.Expr:
    return expr.xreplace({X: X**d, XI: XI**d, Y: Y**d, YI: YI**d})


def lean(expr: sp.Expr) -> str:
    text = sp.sstr(expr, order="none").replace("**", "^")
    return text


def certificate(lhs: sp.Expr, rhs: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    f = sp.expand(lhs - rhs)
    if f == 0:
        return sp.Integer(0), sp.Integer(0), sp.Integer(0)
    (q1, q2), r = sp.reduced(f, RELATIONS, *GENS, order="lex")
    r = sp.Poly(r, *GENS)
    if any(c % 2 for c in r.coeffs()):
        raise ArithmeticError(f"not an identity over GF(2): remainder {r.as_expr()}")
    return sp.expand(q1), sp.expand(q2), sp.expand(r.as_expr() / 2)


# --- the polynomials, from the atlas -----------------------------------------------------------

P = {
    "hexH1": laurent(atlas3.polynomial("hexagon", ("H1",))),
    "sqN4": laurent(atlas3.polynomial("square", ("N4",))),
    "sqD4": laurent(atlas3.polynomial("square", ("D4",))),
    "sqK8": laurent(atlas3.polynomial("square", ("K8",))),
    "sqN4D4self": laurent(atlas3.polynomial("square", ("N4", "D4", "self"))),
    "sqD4A4self": laurent(atlas3.polynomial("square", ("D4", "A4", "self"))),
    "sqN4K8C4": laurent(atlas3.polynomial("square", ("N4", "K8", "C4"))),
    "sqA4K8C4self": laurent(atlas3.polynomial("square", ("A4", "K8", "C4", "self"))),
    "sqC4self": laurent(atlas3.polynomial("square", ("C4", "self"))),
    "sqA4C4": laurent(atlas3.polynomial("square", ("A4", "C4"))),
}
_, udE, duE, _ = atlas3._triangle_entries(("E",))
_, udVT, duVT, _ = atlas3._triangle_entries(("VO", "T13"))
uuVS, _, _, _ = atlas3._triangle_entries(("VS",))
P["triUdE"], P["triDuE"] = laurent(udE), laurent(duE)
P["triUdVOT13"], P["triDuVOT13"] = laurent(udVT), laurent(duVT)
P["triVS"] = laurent(uuVS)

DOCS = {
    "hexH1": "The hexagon's parity rule H1 (B135/S135): the six nearest cells, axial coordinates.",
    "sqN4": "The square's four nearest cells (the sigma automaton).",
    "sqD4": "The square's four diagonal cells.",
    "sqK8": "The square's eight cells at distance sqrt 5 (knight moves).",
    "sqN4D4self": "The square's nine-cell parity rule with the cell itself (B1357/S02468).",
    "sqD4A4self": "The square rule D4 + A4 + self.",
    "sqN4K8C4": "The square rule N4 + K8 + C4 (round 2).",
    "sqA4K8C4self": "The square rule A4 + K8 + C4 + self (round 2's first failure).",
    "sqC4self": "The square rule C4 + self (round 2).",
    "sqA4C4": "The square rule A4 + C4 (round 2's accident at n = 13).",
    "triUdE": "The triangle rule E's up-from-down entry (its matrix is [[0, ud], [du, 0]]).",
    "triDuE": "The triangle rule E's down-from-up entry.",
    "triUdVOT13": "The triangle rule VO + T13's up-from-down entry (no same-orientation part).",
    "triDuVOT13": "The triangle rule VO + T13's down-from-up entry.",
    "triVS": "The triangle shell VS, same orientation: a scalar on the translation lattice.",
}

a, b = X + XI, Y + YI  # rule 90 along each axis


def q(t):
    return t**3 + t**2 + t


IDENTITIES = [
    (
        "hexagon_two_steps",
        "Two steps of the hexagon's parity rule are three passes of rule 90, one along each "
        "lattice direction: H1^2 = (x + 1/x)(y + 1/y)(x/y + y/x). This is the identity behind the "
        "hexagon theorem (docs/parity-lattices.md).",
        sp.Symbol("hexH1") ** 2,
        (X + XI) * (Y + YI) * (X * YI + XI * Y),
    ),
    (
        "hexagon_split",
        "H1 splits into three passes of rule 60: H1 = (1 + x)(1 + y)(1 + x/y) / x.",
        sp.Symbol("hexH1"),
        (1 + X) * (1 + Y) * (1 + X * YI) * XI,
    ),
    (
        "square_D4_tensor",
        "D4 is rule 90 along each axis: D4 = (x + 1/x)(y + 1/y).",
        sp.Symbol("sqD4"),
        a * b,
    ),
    (
        "square_N4D4self_tensor",
        "N4 + D4 + self is rule 150 along each axis: (1 + x + 1/x)(1 + y + 1/y).",
        sp.Symbol("sqN4D4self"),
        (1 + X + XI) * (1 + Y + YI),
    ),
    (
        "square_D4A4self_diagonals",
        "D4 + A4 + self is rule 150 along each diagonal: (1 + xy + 1/(xy))(1 + x/y + y/x).",
        sp.Symbol("sqD4A4self"),
        (1 + X * Y + XI * YI) * (1 + X * YI + XI * Y),
    ),
    (
        "square_K8_product",
        "The knight shell is N4 D4.",
        sp.Symbol("sqK8"),
        sp.Symbol("sqN4") * sp.Symbol("sqD4"),
    ),
    (
        "square_N4K8C4_cube",
        "N4 + K8 + C4 = N4^3: a perfect cube (round 2).",
        sp.Symbol("sqN4K8C4"),
        sp.Symbol("sqN4") ** 3,
    ),
    (
        "square_A4K8C4self_cube",
        "A4 + K8 + C4 + self = (1 + N4)^3: a perfect cube (round 2).",
        sp.Symbol("sqA4K8C4self"),
        (1 + sp.Symbol("sqN4")) ** 3,
    ),
    (
        "square_C4self_dilation",
        "C4 + self = (1 + N4)(x^3, y^3): a dilation by 3 (round 2).",
        sp.Symbol("sqC4self"),
        1 + sp.Symbol("sqN4@3"),
    ),
    (
        "square_A4C4_separable",
        "A4 + C4 = q(x + 1/x) + q(y + 1/y), with q(t) = t^3 + t^2 + t (round 2's accident at 13).",
        sp.Symbol("sqA4C4"),
        q(a) + q(b),
    ),
    (
        "triangle_E_square",
        "The triangle's edge rule squares to (1 + VS) I: ud du = 1 + VS.",
        sp.Symbol("triUdE") * sp.Symbol("triDuE"),
        1 + sp.Symbol("triVS"),
    ),
    (
        "triangle_VOT13_twisted",
        "VO + T13 squares to s I with s = s_E(x, y) s_E(x^3, y^3), s_E = ud_E du_E: the twisted "
        "power of round 3.",
        sp.Symbol("triUdVOT13") * sp.Symbol("triDuVOT13"),
        sp.Symbol("triUdE") * sp.Symbol("triDuE") * sp.Symbol("triUdE@3") * sp.Symbol("triDuE@3"),
    ),
]


def _unfold(expr: sp.Expr) -> sp.Expr:
    """Replace each named polynomial, and each `name@d` (it with x -> x^d), by its expression."""
    out = {sp.Symbol(k): v for k, v in P.items()}
    for s in expr.free_symbols:
        if "@" in str(s):
            name, d = str(s).split("@")
            out[s] = dilate(P[name], int(d))
    return expr.xreplace(out)


def _call(expr: sp.Expr) -> str:
    """Lean text, with named polynomials as applications: `name x xi y yi`, or at x^d."""
    out = {}
    for s in expr.free_symbols:
        if str(s) in P:
            out[s] = sp.Symbol(f"({s} x xi y yi)")
        elif "@" in str(s):
            name, d = str(s).split("@")
            out[s] = sp.Symbol(f"({name} (x^{d}) (xi^{d}) (y^{d}) (yi^{d}))")
    return lean(expr.xreplace(out))


def render() -> str:
    lines = [
        "/-",
        "Generated by proofs/generate.py from the atlas code; do not edit by hand.",
        "",
        "Laurent polynomial identities over GF(2), stated in any commutative ring of",
        "characteristic 2 for x, x⁻¹ = xi, y, y⁻¹ = yi. Each proof is a certificate that",
        "Lean's `ring` rechecks.",
        "-/",
        "import Mathlib.Algebra.CharP.Lemmas",
        "import Mathlib.Tactic.LinearCombination",
        "",
        "namespace LatticeProofs",
        "",
        "variable {R : Type*} [CommRing R]",
        "",
    ]
    for name, expr in P.items():
        lines += [
            f"/-- {DOCS[name]} -/",
            f"def {name} (x xi y yi : R) : R :=",
            f"  {lean(expr)}",
            "",
        ]
    for name, doc, lhs, rhs in IDENTITIES:
        q1, q2, Q = certificate(_unfold(lhs), _unfold(rhs))
        names = {str(s).split("@")[0] for s in lhs.free_symbols | rhs.free_symbols}
        used = sorted(names & set(P))
        lines += [
            f"/-- {doc} -/",
            f"theorem {name} (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) "
            "(hy : y * yi = 1) :",
            f"    {_call(lhs)} =",
            f"      {_call(rhs)} := by",
        ]
        if used:
            lines.append(f"  unfold {' '.join(used)}")
        lines.append(
            f"  linear_combination ({lean(q1)}) * hx + ({lean(q2)}) * hy + ({lean(Q)}) * h2"
        )
        lines.append("")
    lines += ["end LatticeProofs", ""]
    return "\n".join(lines)


def main() -> None:
    out = HERE / "LatticeProofs" / "Identities.lean"
    out.write_text(render())
    print(f"wrote {out} ({len(IDENTITIES)} identities)")


if __name__ == "__main__":
    main()
