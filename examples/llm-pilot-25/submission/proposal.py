"""
Numerical checks of the mechanisms in proposal.md, with the tools.  Prints what it checks and
whether each check held.  Runs in a few minutes:  ./python proposal.py  (--full adds the whole
square family at 25 and a wider atlas grid; slower).
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))

import mechanism  # noqa: E402
from chance import analyse, partition, symmetries  # noqa: E402
from eigen import Field, eigenvalue, eigenvalues  # noqa: E402
from family import rule  # noqa: E402
from halffrob import _psi, pmul, preduce, pscale  # noqa: E402

FULL = "--full" in sys.argv
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(("  [ok]   " if ok else "  [FAIL] ") + name + (f"  ({detail})" if detail else ""))


def all_powers(f, m, q):
    F = Field(m)
    return all(v == 0 or F.pow(v, F.order // q) == 1 for v in eigenvalues(F, f).values())


def P(s):
    return frozenset(tuple(map(int, p.split(","))) for p in s.split())


def shell(a, b):
    return frozenset((s * x, t * y) for x, y in ((a, b), (b, a)) for s in (1, -1) for t in (1, -1))


RULES = json.load(open(os.path.join(HERE, "data", "rules.json")))
FAM25 = json.load(open(os.path.join(HERE, "data", "family25.json")))
ATLAS25 = {"+".join(r["shells"]): frozenset(map(tuple, r["terms"])) for r in RULES
           if r["lattice"] != "square" and "+".join(r["shells"]) in
           ("E+T7+self", "H1+H3+H13", "H3+H4+H5")}  # fmt: skip
SEVENTEEN = [(str(h["id"]), frozenset(map(tuple, h["terms"]))) for h in FAM25["hits"]]
SEVENTEEN += sorted(ATLAS25.items())

# ------------------------------------------------------------------------------------------------
print("1. The seventeen at m = 25: what condition() claims, and each claim against the eigenvalues")
explained = []
for name, f in SEVENTEEN:
    w = mechanism.explain(f, 25)
    q = w["q"] if w else 1
    kinds = [k for k, _, _ in w["found"]] if w else []
    if q > 1:
        explained.append(name)
        check(f"{name}: q = {q} via {kinds}", all_powers(f, 25, q))
    else:
        print(f"         {name}: no claim")
check("five of the seventeen explained (1227, 3096, 21029, 23608, 32184)",
      sorted(explained) == sorted(["1227", "3096", "21029", "23608", "32184"]))

# ------------------------------------------------------------------------------------------------
print("2. The identities behind them (exact, over GF(2))")
a, b = P("-1,0 1,0"), P("0,-1 0,1")
w = pmul(a, b)  # t(x) t(y), the rule-90 orbit product O_(1,0)
for fid, shells in ((3096, [(3, 1), (4, 1), (7, 1), (7, 3), (7, 4)]),
                    (23608, [(1, 1), (3, 1), (4, 1), (7, 3), (7, 4), (7, 7)])):
    B = frozenset().union(*(shell(*s) for s in shells))
    lhs = pmul(pmul(pmul(rule(fid), w), w), w)
    check(f"{fid} * (t(x) t(y))^3 = " + " + ".join("Sh%s" % (s,) for s in shells), lhs == B)
    Bm = preduce(B, 25)
    check(f"  that B is permuted by x -> x^7 (7 = 2^5 mod 25)",
          frozenset(((7 * p) % 25, (7 * r) % 25) for p, r in Bm) == Bm)
for fid, C in ((1227, P("0,0 1,0 -1,0 0,1 0,-1")), (21029, P("0,0 1,1 1,-1 -1,1 -1,-1")),
               (32184, P("1,0 -1,0 0,1 0,-1 1,1 1,-1 -1,1 -1,-1"))):
    check(f"{fid} = C(x, y) C(x^3, y^3), 3 = 2^7 mod 25", pmul(C, pscale(C, 3)) == rule(fid))
H = mechanism._sym_to_t([r for p, r in rule(3096)])  # 3096 on the line x = 1
check("3096 on the axes: t^2 Psi_3(t)^2, exponent A = 258 = 3 * 86 (t^129 = t t^(2^7))",
      mechanism.line_exponent(H, 25) == 258 and H == mechanism.halffrob._clmul(
          0b100, mechanism.halffrob._clmul(_psi(3), _psi(3))))
check("Psi_e(0) = 1 for odd e < 61 (used on the lines at j = 0)",
      all(_psi(e) & 1 for e in range(3, 61, 2)))

# ------------------------------------------------------------------------------------------------
print("3. Soundness: every claim of condition() against the eigenvalues")
ms = list(range(9, 62, 2)) + [63, 65, 69, 73, 75, 85, 99, 105, 127, 151] if FULL else [13, 21, 25, 29, 37]
for m in ms:
    t0 = time.time()
    claims = bad = 0
    for r in RULES:
        f = frozenset(map(tuple, r["terms"]))
        q = mechanism.condition(f, m)
        if q > 1:
            claims += 1
            bad += not all_powers(f, m, q)
    check(f"atlas, m = {m}: {claims} claims, {bad} false", bad == 0, "%.0f s" % (time.time() - t0))
random.seed(25)
sample = random.sample(range(1, 2**15), 1500)
for m in (21, 25, 27, 33, 35, 45, 49, 55, 63):
    claims = bad = 0
    for bits in sample:
        q = mechanism.condition(rule(bits), m)
        if q > 1:
            claims += 1
            bad += not all_powers(rule(bits), m, q)
    check(f"family sample (1500), m = {m}: {claims} claims, {bad} false", bad == 0)
if FULL:
    claims = bad = 0
    for bits in range(1, 2**15):
        q = mechanism.condition(rule(bits), 25)
        if q > 1:
            claims += 1
            bad += not all_powers(rule(bits), 25, q)
    check(f"whole square family, m = 25: {claims} claims, {bad} false", bad == 0)

# ------------------------------------------------------------------------------------------------
print("4. Census remainder (data/remainder.csv) explained by condition()")
idx = {(r["lattice"], "+".join(r["shells"])): r for r in RULES}
rows = list(csv.DictReader(open(os.path.join(HERE, "data", "remainder.csv"))))
got = []
for row in rows:
    f = frozenset(map(tuple, idx[(row["lattice"], row["shells"])]["terms"]))
    m = int(row["m"])
    q = mechanism.condition(f, m)
    if q > 1:
        got.append((m, row["lattice"], row["shells"]))
        assert all_powers(f, m, q)
by_m = {}
for m, _, _ in got:
    by_m[m] = by_m.get(m, 0) + 1
check(f"{len(got)} of {len(rows)} remainder rows explained, by size {by_m}", len(got) == 19)

# ------------------------------------------------------------------------------------------------
print("5. The fibre identity: N(lambda(c)) = lambda(5c) + E(c) at m = 25 (necklaces of length 5)")
F25 = Field(25)
Z = [F25.pow(F25.zeta, e) for e in range(25)]


def necklace_E(f, c):
    """Sum over non-constant 5-tuples of terms, one per cyclic orbit, with sum s = 0 mod 5, of
    zeta^S omega^T (S = sum of s_k, T = sum of k s_k)."""
    s = [(p * c[0] + r * c[1]) % 25 for p, r in f]
    out, seen = 0, set()
    for tup in itertools.product(range(len(s)), repeat=5):
        if len(set(tup)) == 1 or tup in seen:
            continue
        orbit = {tup[i:] + tup[:i] for i in range(5)}
        seen |= orbit
        S = sum(s[i] for i in tup)
        if S % 5:
            continue
        T = sum(k * s[i] for k, i in enumerate(tup))
        out ^= Z[(S + 5 * T) % 25]
    return out


random.seed(7)
ok = True
for _ in range(6):
    f = rule(random.randrange(1, 2**15))
    f = frozenset(random.sample(sorted(f), min(3, len(f))))  # keep the necklace sum small
    f = f | frozenset((-p, -r) for p, r in f)
    for c in ((0, 1), (1, 1), (1, 2), (1, 4)):
        lam = eigenvalue(F25, f, *c)
        N = F25.pow(lam, 341) if lam else 0
        ok &= N == eigenvalue(F25, f, (5 * c[0]) % 25, (5 * c[1]) % 25) ^ necklace_E(f, c)
check("N(lambda(c)) = lambda^341 = lambda(5c) + E(c) on random rules", ok)

# ------------------------------------------------------------------------------------------------
print("6. Refined chance model at 25 (fibres of c -> 5c as blocks, joint law from the family)")


def block_model(pop, m, exclude):
    F = Field(m)
    sym = symmetries(frozenset().union(*pop), m)
    cls = partition(m, sym)
    reps = [c for c, _, _ in cls]
    where = {}

    def act(M, x, y):
        return (M[0] * x + M[2] * y) % m, (M[1] * x + M[3] * y) % m

    for i, (c, _, _) in enumerate(cls):
        stack = [c]
        where[c] = i
        while stack:
            x, y = stack.pop()
            for nxt in [(2 * x % m, 2 * y % m)] + [act(M, x, y) for M in sym]:
                if nxt not in where:
                    where[nxt] = i
                    stack.append(nxt)
    parent = list(range(len(cls)))

    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for c in reps:
        pc = (5 * c[0] % m, 5 * c[1] % m)
        if pc != (0, 0):
            parent[find(where[c])] = find(where[pc])
    blocks = {}
    for i in range(len(cls)):
        blocks.setdefault(find(i), []).append(i)
    zeta = [F.pow(F.zeta, e) for e in range(m)]
    rows, confined = [], []
    for f in pop:
        okc = []
        for c in reps:
            v = 0
            for x, y in f:
                v ^= zeta[(x * c[0] + y * c[1]) % m]
            okc.append(v == 0 or F.pow(v, F.order // 3) == 1)
        if all(okc):
            confined.append(f)
        if f not in exclude:
            rows.append(okc)
    n = len(rows)
    naive = n * math.prod(sum(r[i] for r in rows) / n for i in range(len(cls)))
    blk = n * math.prod(sum(all(r[i] for i in bl) for r in rows) / n for bl in blocks.values())
    return naive, blk, confined, [sorted(reps[i] for i in bl) for bl in blocks.values()]


fam = [rule(bits) for bits in range(1, 2**15)] if FULL else None
for lattice in ("hexagon", "triangle", "square"):
    pop = [frozenset(map(tuple, r["terms"])) for r in RULES if r["lattice"] == lattice]
    _, _, conf, _ = block_model(pop, 25, set())
    expl = {f for f in conf if mechanism.condition(f, 25) > 1 or analyse(f, 25)["forced"]}
    naive, blk, conf, _ = block_model(pop, 25, expl)
    left = len([f for f in conf if f not in expl and f])
    print(f"         atlas {lattice}: unexplained confined {left}; expected: independent classes "
          f"{naive:.2f}, independent fibres {blk:.2f}")
if FULL:
    _, _, conf, blocks = block_model(fam, 25, set())
    expl = {f for f in conf if mechanism.condition(f, 25) > 1 or analyse(f, 25)["forced"]}
    naive, blk, conf, blocks = block_model(fam, 25, expl)
    print(f"         family: confined {len(conf)}, explained or forced {len(expl)}, unexplained "
          f"{len(conf) - len(expl)}; expected: independent classes {naive:.2f}, independent "
          f"fibres {blk:.2f}; fibres {blocks}")
    check("family at 25: unexplained count within 2 sd of the fibre model",
          abs((len(conf) - len(expl)) - blk) <= 2 * math.sqrt(blk))

print()
print("%d checks, %d failed" % (len(RESULTS), RESULTS.count(False)))
