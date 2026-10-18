"""
An independent check of round 3: odd parts of periods from eigenvalues. (Not registered.)

    uv run python examples/linear-atlas-3/eigen.py [--workers 4]

The registered checker (atlas3.OddExact) takes powers of the rule's matrix in the group ring.
This computes the same numbers another way. At odd part m, F2[T] modulo its radical is F2[(Z/m)^2],
a product of fields. The odd part of the period is the lcm of the multiplicative orders of the
rule's nonzero eigenvalues f(zeta^j, zeta^k), for zeta a primitive m-th root of unity in F(2^d),
d = ord_m(2). On the triangle, f is s, where M^2 = s I; the odd part of M's period is s's.
Eigenvalues at (j, k) and (2j, 2k) are Frobenius conjugates and have the same order, so one per
orbit is enough.

For every record of round 3 it computes the odd part and compares it with the record: the
predicted value when the check held, and the computed odd part otherwise. Writes eigen.json.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
from multiprocessing import Pool
from pathlib import Path

import atlas3
import sympy

HERE = Path(__file__).resolve().parent


@functools.cache
def field(m: int) -> tuple[int, int]:
    """(modulus, degree): F(2^d) as F2[z] modulo an irreducible factor of Phi_m."""
    z = sympy.Symbol("z")
    _, factors = sympy.Poly(sympy.cyclotomic_poly(m, z), z, modulus=2).factor_list()
    g = factors[0][0]
    mod = sum((int(c) % 2) << e for (e,), c in g.terms())
    return mod, mod.bit_length() - 1


def _mul(a: int, b: int, mod: int, top: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> top & 1:
            a ^= mod
    return r


def _pow(a: int, e: int, mod: int, top: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = _mul(r, a, mod, top)
        a, e = _mul(a, a, mod, top), e >> 1
    return r


@functools.cache
def _primes(N: int) -> tuple[int, ...]:
    return tuple(sympy.primefactors(N))


def odd_part(f: frozenset, m: int) -> int:
    if not f:
        return 1
    mod, d = field(m)
    top, N = d, 2**d - 1
    zeta = [_pow(2, e, mod, top) for e in range(m)]  # z = 2 is a primitive m-th root
    seen, period = set(), 1
    for j in range(m):
        for k in range(m):
            if (j, k) in seen:
                continue
            a, b = j, k
            while (a, b) not in seen:  # the Frobenius orbit of (j, k)
                seen.add((a, b))
                a, b = 2 * a % m, 2 * b % m
            value = 0
            for x, y in f:
                value ^= zeta[(x * j + y * k) % m]
            if value == 0:
                continue
            order = N
            for p in _primes(N):
                while order % p == 0 and _pow(value, order // p, mod, top) == 1:
                    order //= p
            period = math.lcm(period, order)
    return period


def _job(row):
    lattice, shells, m, recorded = row
    return (lattice, shells, m, recorded, odd_part(atlas3.polynomial(lattice, tuple(shells)), m))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    rows = []
    for line in (HERE / "records.jsonl").read_text().splitlines():
        r = json.loads(line)
        if "check" in r and r["check"]["is_odd_part"]:
            recorded = int(r["predicted"])
        else:
            recorded = int(r["odd part"])
        rows.append((r["lattice"], r["shells"], r["m"], recorded))
    rows.sort(key=lambda r: r[2])
    if args.limit:
        rows = rows[: args.limit]
    with Pool(args.workers) as pool:
        results = pool.map(_job, rows, chunksize=8)
    disagree = [
        {"rule": atlas3.name(lat, tuple(sh)), "m": m, "recorded": rec, "eigenvalues": eig}
        for lat, sh, m, rec, eig in results
        if rec != eig
    ]
    out = {"records": len(results), "agree": len(results) - len(disagree), "disagree": disagree}
    (HERE / "eigen.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "disagree"}), len(disagree), "disagree")


if __name__ == "__main__":
    main()
