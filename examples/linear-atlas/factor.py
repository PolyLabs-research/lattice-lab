"""
Do the square and hexagon rules' polynomials split into one-dimensional factors? (Not registered.)

    uv run python examples/linear-atlas/factor.py

A rule on the square or hexagonal lattice is a Laurent polynomial f(x, y) over GF(2). A factor
is one-dimensional when it is a polynomial g(u) in a single monomial u = x^a y^b: one pass of a
1D linear rule along the lattice direction (a, b). The hexagon's parity rule, for instance, is
(1 + x)(1 + y)(1 + x/y) / x: a pass of rule 60 along each of its three directions.

sympy cannot factor polynomials of two variables over GF(2), so this searches. For each
primitive direction (a, b) with |a|, |b| <= 2, a unimodular change of variables makes u = x^a y^b
a coordinate X, with Y the other. Then g(X) divides f exactly when f is zero in
GF(2)[Y^+-1][X] / g(X). Here g runs over the irreducible polynomials of degree 1 to 3, and every
factor found is divided out. A rule "splits" when what is left is a monomial. Writes
factors.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import engine
from lattices import Matrix, _tau

HERE = Path(__file__).resolve().parent
IRREDUCIBLE = {"1+u": (0, 1), "1+u+u^2": (0, 1, 2), "1+u+u^3": (0, 1, 3), "1+u^2+u^3": (0, 2, 3)}
DIRECTIONS = sorted(
    {
        (a, b) if (a, b) > (0, 0) else (-a, -b)
        for a in range(-2, 3)
        for b in range(-2, 3)
        if (a, b) != (0, 0) and math.gcd(a, b) == 1
    }
)


def polynomial(lattice: str, shells: tuple[str, ...]) -> set[tuple[int, int]]:
    """The rule's Laurent polynomial on the plane, as the set of exponents with coefficient 1."""
    terms: dict[tuple[int, int], int] = {}
    for shell in shells:
        steps = ((0, 0),) if shell == "self" else engine.SHELLS[lattice][shell]
        for step in steps:
            terms[step] = terms.get(step, 0) ^ 1
    return {e for e, c in terms.items() if c}


def _basis(a: int, b: int) -> tuple[int, int]:
    """(c, d) with a d - b c = 1."""
    for c in range(-3, 4):
        for d in range(-3, 4):
            if a * d - b * c == 1:
                return c, d
    raise ValueError((a, b))


def _to_xy(terms, a, b, c, d):
    """Exponents (i, j) in x, y as exponents (p, q) in X = x^a y^b, Y = x^c y^d."""
    return {(i * d - j * c, -i * b + j * a) for i, j in terms}


def _from_xy(terms, a, b, c, d):
    return {(p * a + q * c, p * b + q * d) for p, q in terms}


def _divide(terms: set, g: tuple[int, ...]) -> set | None:
    """terms / g(X) over GF(2)[Y^+-1], or None if g does not divide it.

    Long division of each power of Y's coefficient, a Laurent polynomial in X, from the top. g has
    a constant term, so it is prime to X: g divides the coefficient exactly when the division
    leaves nothing once what is left spans less than g's degree."""
    by_q: dict[int, set[int]] = {}
    for p, q in terms:
        by_q.setdefault(q, set()).add(p)
    top = max(g)
    quotient = set()
    for q, ps in by_q.items():
        rest, out = set(ps), set()
        while rest and max(rest) - min(rest) >= top:
            shift = max(rest) - top
            rest ^= {shift + e for e in g}
            out ^= {shift}
        if rest:
            return None
        quotient |= {(p, q) for p in out}
    return quotient


def _times(f: set, g: set) -> set:
    out: set = set()
    for i, j in f:
        for k, m in g:
            out ^= {(i + k, j + m)}
    return out


def split(f: set) -> dict:
    """Divide out every one-dimensional factor found, until none is left."""
    original, factors = f, []
    changed = True
    while changed and len(f) > 1:
        changed = False
        for a, b in DIRECTIONS:
            c, d = _basis(a, b)
            for gname, g in IRREDUCIBLE.items():
                q = _divide(_to_xy(f, a, b, c, d), g)
                if q is not None and q:
                    f = _from_xy(q, a, b, c, d)
                    factors.append({"direction": [a, b], "factor": gname})
                    changed = True
                    break
            if changed:
                break
    product = f
    for factor in factors:
        a, b = factor["direction"]
        g = {(e * a, e * b) for e in IRREDUCIBLE[factor["factor"]]}
        product = _times(product, g)
    assert product == original  # the factors multiply back
    return {
        "terms": len(original),
        "factors": factors,
        "left": sorted(f),
        "splits": len(f) == 1,
    }


def triangle_square(shells: tuple[str, ...]) -> set | None:
    """A triangle rule is a 2 x 2 matrix [[uu, ud], [du, dd]] of polynomials on the translation
    lattice (engine.build's entries, on the plane). Its square is s I for a polynomial s, which
    is returned (None if the square is not scalar)."""
    uu, ud, du, dd = set(), set(), set(), set()
    for shell in shells:
        if shell == "self":
            uu ^= {(0, 0)}
            dd ^= {(0, 0)}
            continue
        for dr, dc in engine.TRIANGLE_SHELLS[shell]["up"]:
            i, j = _tau(dr, dc) if (dr + dc) % 2 == 0 else _tau(dr, dc - 1)
            (uu if (dr + dc) % 2 == 0 else ud).symmetric_difference_update({(-i, -j)})
        for dr, dc in engine.TRIANGLE_SHELLS[shell]["down"]:
            i, j = _tau(dr, dc) if (dr + dc) % 2 == 0 else _tau(dr, dc + 1)
            (dd if (dr + dc) % 2 == 0 else du).symmetric_difference_update({(-i, -j)})
    a, b = _times(uu, uu) ^ _times(ud, du), _times(uu, ud) ^ _times(ud, dd)
    c, d = _times(du, uu) ^ _times(dd, du), _times(du, ud) ^ _times(dd, dd)
    return a if not b and not c and a == d else None


def family(rule: dict) -> str | None:
    """Which kind of law survived the registered test: a 1D rule's period, or the full bound."""
    if rule["status"] == "no law":
        return None
    survivors = " ".join(rule["survivors"])
    if "P90" in survivors or "P150" in survivors:
        return "a 1D rule's period"
    return "the full bound" if "sord" in survivors else "constant"


BASE = {"square": ("N4",), "hexagon": ("H1",), "triangle": ("E",)}


def _add(*terms):
    k = len(terms[0].e)
    return Matrix(
        terms[0].ring,
        [[sum(t.e[i][j] for t in terms) % 2 for j in range(k)] for i in range(k)],
    )


QUADRATICS = {
    "R^2": lambda R: R * R,
    "(1+R)^2": lambda R: _add(R.identity(), R) * _add(R.identity(), R),
    "R(1+R)": lambda R: R * _add(R.identity(), R),
    "1+R+R^2": lambda R: _add(R.identity(), R, R * R),
}


def _matrix(lattice: str, shells: tuple[str, ...], n: int):
    return engine.build(lattice, shells, n)[1]


def relations() -> dict:
    """Which rules are a quadratic in the lattice's nearest-neighbour rule R? Checked as matrices
    on the 12 and 16 tori, where no shell wraps onto another, and for the squares, whether the
    period is that of R (or 1 + R) halved when even: the period of M^2 is p / gcd(p, 2)."""
    rows = [json.loads(line) for line in (HERE / "discovery.jsonl").read_text().splitlines()]
    periods = {(r["lattice"], tuple(r["shells"]), r["n"]): r["period"] for r in rows}
    out = {}
    for lattice, shells in engine.rules():
        base = BASE[lattice]
        for form, h in QUADRATICS.items():
            same = True
            for n in (12, 16):
                same = same and h(_matrix(lattice, base, n)) == _matrix(lattice, shells, n)
            if not same:
                continue
            entry = {"rule": engine.name(lattice, shells), "is": form.replace("R", base[0])}
            if form in ("R^2", "(1+R)^2"):
                root = base if form == "R^2" else (*base, "self")
                entry["period is the root's halved when even"] = all(
                    p == periods[(lattice, root, n)] // math.gcd(periods[(lattice, root, n)], 2)
                    for (lat, sh, n), p in periods.items()
                    if lat == lattice and sh == shells
                )
            out[engine.name(lattice, shells)] = entry
    return out


def main() -> None:
    verdict = json.loads((HERE / "ledger.jsonl").read_text().splitlines()[-1])["body"]["rules"]
    out = {}
    for lattice, shells in engine.rules():
        key = engine.name(lattice, shells)
        if lattice == "triangle":
            s = triangle_square(shells)
            assert s is not None, key
            r = {"square of the matrix": "s I", **split(s)}
        else:
            r = split(polynomial(lattice, shells))
        r["registered law that held"] = family(verdict[key])
        out[key] = r
        print(
            f"{key:26s} splits={r['splits']!s:5s} {r['registered law that held']!s:20s}",
            [(f["factor"], tuple(f["direction"])) for f in r["factors"]],
        )
    quadratic = relations()
    for entry in quadratic.values():
        print(entry)
    (HERE / "factors.json").write_text(
        json.dumps({"one-dimensional factors": out, "quadratics": quadratic}, indent=1) + "\n"
    )


if __name__ == "__main__":
    main()
