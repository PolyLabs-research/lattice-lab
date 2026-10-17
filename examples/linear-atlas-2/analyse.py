"""
After round 2's verdict: are its failures explained by perfect powers? (Not registered.)

    uv run python examples/linear-atlas-2/analyse.py

The first failure was square A4+K8+C4+self at n = 197, a third of the predicted full bound. That
rule is (N4 + self)^3 exactly, and one other new rule is a cube, N4+K8+C4 = N4^3. At odd n, M is
diagonalisable over F(2^k) and its period is the lcm of its eigenvalues' orders. The eigenvalues of
g^3 are the cubes of g's, and ord(x^3) = ord(x) / gcd(ord(x), 3). So the period of g^3 is p /
gcd(p, 3), where p is g's period: the 3-part drops by one, through an eigenvalue with the largest
3-part.

This lists every rule that is a cube of another rule of the six shells, then checks every failed
prediction. Is each failure one of the cubes? Is its true period p / gcd(p, 3), with p the period
the pattern assigns to the cube root (the full bound for N4 + self, P90 for N4)? Writes
analysis.json.
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


def main() -> None:
    verdict = json.loads((HERE / "ledger.jsonl").read_text().splitlines()[-1])["body"]
    registered = {
        json.loads(line)["body"]["rule"]: json.loads(line)["body"]
        for line in (HERE / "ledger.jsonl").read_text().splitlines()
        if json.loads(line)["kind"] == "prediction"
    }
    roots = cubes()
    failures = []
    for rule, result in verdict["rules"].items():
        for f in result.get("failures", []):
            root = roots.get(rule)
            entry = {"rule": rule, **f, "a cube": root is not None}
            if root is not None:
                call = atlas2.classify(root)
                p = atlas2.predict(call, f["n"])
                entry["root"] = "+".join(root)
                entry["root's predicted period"] = p
                entry["p / gcd(p, 3)"] = p // math.gcd(p, 3)
                entry["matches"] = f["period"] == p // math.gcd(p, 3)
            failures.append(entry)
    cube_sizes = {}
    for rule in roots:
        if rule in registered:
            body, root = registered[rule], roots[rule]
            call = atlas2.classify(root)
            cube_sizes[rule] = {
                "root": "+".join(root),
                "sizes": len(body["predictions"]),
                "sizes where 3 divides the root's period": sum(
                    atlas2.predict(call, int(n)) % 3 == 0 for n in body["predictions"]
                ),
            }
    out = {
        "cubes among the six shells' rules": {k: "+".join(v) for k, v in roots.items()},
        "registered cubes": cube_sizes,
        "failures": failures,
        "every failure is a cube, with period p / gcd(p, 3)": all(
            f["a cube"] and f["matches"] for f in failures
        ),
        "failures at sizes where 3 divides the root's period": {
            rule: sum(f["rule"] == rule for f in failures) for rule in cube_sizes
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "failures"}, indent=1))
    print(len(failures), "failures")


if __name__ == "__main__":
    main()
