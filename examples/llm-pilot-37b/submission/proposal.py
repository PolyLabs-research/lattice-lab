"""
Numerical checks of the unit-times-power mechanism (proposal.md).  Prints what it checks and
whether each check held.  Run with ./python proposal.py (about three minutes).
"""

from __future__ import annotations

import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))
sys.path.insert(0, os.path.join(HERE, "scratch"))

import mechanism  # noqa: E402
from eigen import Field, eigenvalues  # noqa: E402
from family import rule, rules  # noqa: E402
from halffrob import _rule90_powers, pmul, sord  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(f"[{'held' if ok else 'FAILED'}] {name}" + (f": {detail}" if detail else ""), flush=True)


def all_qth_powers(f, m, q):
    """Direct eigenvalue computation (for checking only)."""
    F = Field(m)
    return all(not v or F.pow(v, F.order // q) == 1 for v in eigenvalues(F, f).values())


def T(w):  # rule 90 along w
    return frozenset({w, (-w[0], -w[1])})


def add(*ps):
    out = set()
    for p in ps:
        out ^= set(p)
    return frozenset(out)


ONE = frozenset({(0, 0)})
A, B = T((1, 0)), T((0, 1))
UNITS = {"a+b": add(A, B), "ab": pmul(A, B), "(a+1)(b+1)": pmul(add(A, ONE), add(B, ONE))}
CUBES = {"a+b+1": add(A, B, ONE), "ab+1": add(pmul(A, B), ONE), "ab+a+b": add(pmul(A, B), A, B)}

print("=" * 78)
print("1. The nine products U * g^3 (U of bidegree (1,1) a unit, g of bidegree (1,1) not)")
print("=" * 78)
targets = json.load(open(os.path.join(HERE, "data", "targets.json")))
fam_of = {}
for bits, f in rules():
    fam_of[f] = bits
products = {}
for un, U in UNITS.items():
    for gn, g in CUBES.items():
        f = pmul(U, pmul(g, pmul(g, g)))
        products[fam_of.get(f)] = (un, gn)
        print(f"   {un:>10} * ({gn})^3 = family rule {fam_of.get(f)}")
target_ids = {t["id"] for t in targets}
check("all nine products are family rules and targets", set(products) <= target_ids and None not in products,
      str(sorted(products)))
check("they are exactly the targets the mechanism explains at 37",
      {t["id"] for t in targets if t["m"] == 37 and mechanism.explain(rule(t["id"]), 37)} == set(products))

print()
print("=" * 78)
print("2. The units at 37 and 61")
print("=" * 78)
r37 = _rule90_powers(37)
check("rule 90 is confined to the cubes at 37 (every t_j a cube in F(2^18))", r37.get(3, 1) % 3 == 0,
      f"3-part of rule 90's confinement: {r37.get(3)}")
r61 = _rule90_powers(61)
check("rule 90 is NOT confined to the cubes at 61", r61.get(3, 1) % 3 != 0, f"{r61.get(3)}")
A3 = mechanism._lemma3_exponent(3, 61)
check("at 61, 3 = 2^6, so Psi_3(t)^2 = t^A with A = 2^6 - 1 = 63, divisible by 3", A3 == 63 and pow(2, 6, 61) == 3,
      f"A_3 = {A3}")
check("unit (a+1)(b+1) is cube-valued at 61 by Lemma 3, a+b and ab are not claimed",
      mechanism._unit_ok(3, 61, 3) and not mechanism._unit_ok(1, 61, 3))

print()
print("=" * 78)
print("3. The 19 targets: condition, the witness, and the eigenvalues computed directly")
print("=" * 78)
for t in targets:
    f, m = rule(t["id"]), t["m"]
    q = mechanism.condition(f, m)
    w = mechanism.explain(f, m)
    lift = (2 ** (2 * sord(m)) - 1) // (2 ** sord(m) - 1)
    cube_q = 3 * lift
    claimed = q > 1 and q % cube_q == 0
    direct = all_qth_powers(f, m, cube_q)
    wit = products.get(t["id"], "")
    exact = True
    if wit:
        U, g = UNITS[wit[0]], CUBES[wit[1]]
        exact = pmul(U, pmul(g, pmul(g, g))) == f
    print(f"   m={m} rule {t['id']:>5}: condition q={q} ({'cubes' if claimed else 'no claim'}); "
          f"witness {wit or '-'}; exact identity {exact}; all eigenvalues cubes (direct) {direct}")
    if claimed:
        RESULTS.append(direct and exact)
n37 = sum(1 for t in targets if t["m"] == 37 and mechanism.condition(rule(t["id"]), 37) % 786435 == 0)
n61 = sum(1 for t in targets if t["m"] == 61 and mechanism.condition(rule(t["id"]), 61) % (3 * (2**30 + 1)) == 0)
check("condition explains 9 of the 16 at 37 and all 3 at 61", n37 == 9 and n61 == 3, f"{n37} at 37, {n61} at 61")

print()
print("=" * 78)
print("4. The census: what the mechanism explains at every size")
print("=" * 78)
fam = json.load(open(os.path.join(HERE, "data", "family.json")))
for s in fam["sizes"]:
    m = s["m"]
    if not s["hits"]:
        continue
    mine = [h["id"] for h in s["hits"] if mechanism.explain(rule(h["id"]), m)]
    prev = [h["id"] for h in s["hits"] if h["pilot4_q"] > 1 or h["pilot5_q"] > 1]
    left = [h["id"] for h in s["hits"] if h["id"] not in mine and h["id"] not in prev]
    print(f"   m={m}: {len(s['hits'])} hits, expected {s['expected']:.2f}; previous pilots {len(prev)}, "
          f"this mechanism {len(mine)} {mine}; left {len(left)}")

print()
print("=" * 78)
print("5. The chance model at 37: the axis and diagonal classes are not free")
print("=" * 78)
import sympy  # noqa: E402

F37 = Field(37)
tz = F37.pow(F37.zeta, 1) ^ F37.pow(F37.zeta, 36)
t_ = sympy.Symbol("t")
basis = [1, t_, t_**2, t_**3 + t_, t_**4]  # the axis value of a family rule is H(t_j), H in this span
noncube = []
for mask in range(1, 32):
    H = sympy.Poly(sum(b for i, b in enumerate(basis) if mask >> i & 1), t_, modulus=2)
    v = 0
    for (e,), c in H.terms():
        if int(c) % 2:
            v ^= F37.pow(tz, e)
    if not (v and F37.pow(v, F37.order // 786435) == 1):
        noncube.append(H.as_expr())
psi17 = sympy.Poly(sympy.Symbol("t") ** 8 + t_**7 + t_**6 + t_**4 + 1, t_, modulus=2)
halves = [g.as_expr() for g, _ in psi17.factor_list()[1]]
check("at 37, 29 of the 31 axis polynomials H(t), deg H <= 4, give cubes; the two that do not are the "
      "quartic halves of Psi_17", len(noncube) == 2 and set(map(str, noncube)) == set(map(str, halves)),
      f"non-cubes {noncube}")
try:
    import refchance  # noqa: E402

    t0 = time.time()
    R = refchance.analyse(37)
    p = R["p"]
    check("census chance model reproduced (independent classes, 1/3 each): about 0.62 at 37",
          abs(R["E_model"] - 0.62) < 0.05, f"{R['E_model']:.2f}")
    axis = [c for c in R["free"] if R["reps"][c] in ((0, 1), (1, 1))]
    print("   empirical cube rate per free class over the family at 37: "
          + ", ".join(f"{R['reps'][c]}: {p[c]:.3f}" for c in R["free"]))
    check("axis and diagonal classes are cubes in 93.5% of rules (model: 1/3)",
          all(abs(p[c] - 29 / 31) < 0.01 for c in axis))
    check("with the empirical rates (classes independent), the expected number of chance "
          "confinements at 37 is about 5.7, against 7 left unexplained", 4.5 < R["E_ref"] < 7,
          f"{R['E_ref']:.2f}  ({time.time() - t0:.0f} s)")
except Exception as exc:  # noqa: BLE001
    print("   (refined chance model skipped:", exc, ")")

print()
print("=" * 78)
print("6. Soundness spot checks against the eigenvalues")
print("=" * 78)
atlas = [frozenset(map(tuple, r["terms"])) for r in json.load(open(os.path.join(HERE, "data", "rules.json")))]
for m in (13, 25, 37, 61, 65, 101):
    claims = [(f, w["q"]) for f in atlas if (w := mechanism.explain(f, m))]
    bad = [q for f, q in claims if not all_qth_powers(f, m, q)]
    check(f"atlas, m={m}: every claim of the mechanism holds", not bad, f"{len(claims)} claims, {len(bad)} false")
import random  # noqa: E402

random.seed(6)
sample = [rule(b) for b in random.sample(range(1, 32768), 3000)]
for m in (37, 61, 85):
    claims = [(f, w["q"]) for f in sample if (w := mechanism.explain(f, m))]
    bad = [q for f, q in claims if not all_qth_powers(f, m, q)]
    check(f"family sample (3000 rules), m={m}: every claim holds", not bad, f"{len(claims)} claims, {len(bad)} false")

print()
print(f"{sum(RESULTS)} of {len(RESULTS)} checks held.")
