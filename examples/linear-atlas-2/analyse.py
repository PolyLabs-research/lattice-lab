"""
After round 2's verdict: are its failures explained by perfect powers? (Not registered.)

    uv run python examples/linear-atlas-2/analyse.py

The first failure was square A4+K8+C4+self at n = 197, a third of the predicted full bound. That
rule is (N4 + self)^3 exactly, and one other new rule is a cube, N4+K8+C4 = N4^3. At odd n, M is
diagonalisable over F(2^k) and its period is the lcm of its eigenvalues' orders. The eigenvalues of
g^3 are the cubes of g's, and ord(x^3) = ord(x) / gcd(ord(x), 3). So the period of g^3 is p /
gcd(p, 3), where p is g's period: the 3-part drops by one, through an eigenvalue with the largest
3-part.

The second mechanism showed up at C4+self, n = 141. C4 + self is (N4 + self)(x^3, y^3), and when
3 divides n, x -> x^3 maps the n-torus's group ring onto the n/3-torus's. The rest is a free
module of rank 9 over that image, so the rule has its root's period on the n/3 torus.

This finds the cubes and the dilations among the six shells' rules. For each one registered, it
checks every size against the period these give: p / gcd(p, 3) for a cube, and the root's period
at n/3 for a dilation when 3 divides n, where p is the root's predicted period. It lists every other
failure as unforeseen. Writes analysis.json.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import atlas2
import factor

HERE = Path(__file__).resolve().parent


def all_square_rules() -> list[tuple[str, ...]]:
    names = list(atlas2.SQUARE)
    out = []
    for r in range(1, len(names) + 1):
        for combo in itertools.combinations(names, r):
            out += [combo, (*combo, "self")]
    return out


def cubes() -> dict[str, tuple[str, ...]]:
    """Rules of the six shells that are the cube of another such rule."""
    polys = {r: frozenset(atlas2.square_polynomial(r)) for r in all_square_rules()}
    by_poly = {p: r for r, p in polys.items()}
    out = {}
    for root, p in polys.items():
        cube = frozenset(factor._times(factor._times(set(p), set(p)), set(p)))
        if cube in by_poly:
            out["square " + "+".join(by_poly[cube])] = root
    return out


def dilations() -> dict[str, tuple[str, ...]]:
    """Rules of the six shells that are another rule in x^3, y^3."""
    polys = {r: frozenset(atlas2.square_polynomial(r)) for r in all_square_rules()}
    by_poly = {p: r for r, p in polys.items()}
    out = {}
    for rule, p in polys.items():
        if all(i % 3 == 0 and j % 3 == 0 for i, j in p):
            root = by_poly.get(frozenset((i // 3, j // 3) for i, j in p))
            if root is not None:
                out["square " + "+".join(rule)] = root
    return out


def expected(rule: str, n: int) -> int | None:
    """The period a cube or a dilation must have at odd n, from its root's predicted period."""
    if rule in CUBES:
        p = atlas2.predict(atlas2.classify(CUBES[rule]), n)
        return p // math.gcd(p, 3)
    if rule in DILATIONS and n % 3 == 0:
        return atlas2.predict(atlas2.classify(DILATIONS[rule]), n // 3)
    return None


CUBES, DILATIONS = cubes(), dilations()


def main() -> None:
    lines = [json.loads(line) for line in (HERE / "ledger.jsonl").read_text().splitlines()]
    verdict = lines[-1]["body"]
    registered = {e["body"]["rule"]: e["body"] for e in lines if e["kind"] == "prediction"}
    records = {
        ("square " + "+".join(r["shells"]), r["n"]): r
        for r in map(json.loads, (HERE / "records.jsonl").read_text().splitlines())
    }
    explained, unforeseen = {}, []
    for rule in {**CUBES, **DILATIONS}:
        body = registered.get(rule)
        if body is None or not body["predictions"]:
            continue
        rows = []
        for n, value in body["predictions"].items():
            n = int(n)
            want = expected(rule, n) or int(value)
            r = records[(rule, n)]
            period = int(value) if r["check"]["is_period"] else r["period"]
            rows.append({"n": n, "expected": want, "period": period, "matches": want == period})
        explained[rule] = {
            "is": ("cube of " + "+".join(CUBES[rule]))
            if rule in CUBES
            else ("(" + "+".join(DILATIONS[rule]) + ")(x^3, y^3)"),
            "sizes": len(rows),
            "registered prediction failed": len(verdict["rules"][rule]["failures"]),
            "every size as expected": all(row["matches"] for row in rows),
        }
    for rule, result in verdict["rules"].items():
        if rule in explained:
            continue
        for f in result.get("failures", []):
            p, q = int(f["predicted"]), int(f["period"])
            unforeseen.append({"rule": rule, **f, "predicted / period": p // q})
    out = {
        "cubes among the six shells' rules": {k: "+".join(v) for k, v in CUBES.items()},
        "dilations among the six shells' rules": {k: "+".join(v) for k, v in DILATIONS.items()},
        "explained": explained,
        "unforeseen failures": unforeseen,
        "no prediction": {
            rule: r["periods"]
            for rule, r in verdict["rules"].items()
            if r["status"] == "no prediction"
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "no prediction"}, indent=1))


if __name__ == "__main__":
    main()
