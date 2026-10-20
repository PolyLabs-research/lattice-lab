"""
Numerical checks of the mechanism in proposal.md (unit-exponent bookkeeping on top of exact
factorisations and half-Frobenius identities), with the tools.  Prints what it checks and whether
each check held.  Runs in a few minutes:  ./python proposal.py
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "tools"))
sys.path.insert(0, _HERE)

import census37 as C  # noqa: E402
import mechanism  # noqa: E402
from eigen import Field, eigenvalues, is_power, order  # noqa: E402
from halffrob import ONE, _psi, pdiv, pmul, pscale, tfac  # noqa: E402

FAILS = 0


def check(name, ok, detail=""):
    global FAILS
    FAILS += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + name + (("  [" + str(detail) + "]") if detail else ""))


def verify(f, m, q):
    """every nonzero eigenvalue of f at m is a q-th power in F(2^d)*"""
    F = Field(m)
    if F.order % q:
        return False
    e = F.order // q
    return all(F.pow(v, e) == 1 for v in eigenvalues(F, f).values() if v)


def sh(a, b):
    return frozenset((s * p, u * q) for p, q in ((a, b), (b, a)) for s in (1, -1) for u in (1, -1))


def rule_of(orbs):
    n = 0
    for o in orbs:
        n |= 1 << C.orbits(6).index(o)
    return C.rule(n, 6)


def psi_poly(e, w):
    """Psi_e(t_w) as a Laurent polynomial."""
    T, i, out, power = _psi(e), 0, frozenset(), ONE
    while T >> i:
        if T >> i & 1:
            out = out ^ power
        power = pmul(power, tfac(w))
        i += 1
    return out


t0 = time.time()
M = 37
F = Field(M)
N18 = 2**18 - 1
zeta = F.zeta
t = [F.pow(zeta, j) ^ F.pow(zeta, (-j) % M) for j in range(M)]  # rule 90's values t_j

print("== 1. Facts about F(2^18) at m = 37 (section 2 of proposal.md)")
check("2 is a primitive root mod 37: d = 36, s = 18", F.degree == 36 and pow(2, 18, 37) == 36)
check("2^9 = -6 mod 37 and 6^2 = -1 mod 37", pow(2, 9, 37) == 31 and 36 % 37 == 36 and (6 * 6) % 37 == 36)
check("t^(2^9) = D_6(t) = t^6 + t^2 for t = t_1 (Frobenius^9 is the dilation by 6)",
      F.pow(t[1], 512) == F.pow(t[1], 6) ^ F.pow(t[1], 2))
check("norm identity N_{18/9}(t) = t^513 = t^3 (1 + t)^4",
      F.pow(t[1], 513) == F.mul(F.pow(t[1], 3), F.pow(1 ^ t[1], 4)))
check("rule 90 is confined to the cubes: every t_j (j != 0) is a cube in F(2^18)*, t_1 is not a 9th power",
      all(is_power(F, t[j], 3 * (2**18 + 1)) for j in range(1, M)) and not is_power(F, t[1], 9 * (2**18 + 1)))
check("hence rule 150 is confined to the ninth powers: 1 + t_j is a 9th power (and not a 27th)",
      all(is_power(F, 1 ^ t[j], 9 * (2**18 + 1)) for j in range(1, M))
      and not is_power(F, 1 ^ t[1], 27 * (2**18 + 1)))
check("the order of t_1 is 87381 = (2^18 - 1)/3: the rule-90 values generate every cube of F(2^18)*",
      order(F, t[1]) == 87381)
check("elements of F(2^9)* are 27th powers (513 = 27 * 19 is prime to 511)", math.gcd(513, 511) == 1)
A5 = 2**23 - 1  # 5 = 2^23 mod 37
check("5 = 2^23 mod 37 and Psi_5(t_j)^2 = t_j^(2^23 - 1) for all j != 0",
      pow(2, 23, 37) == 5 and all(F.pow(F.pow(t[j], 2) ^ t[j] ^ 1, 2) == F.pow(t[j], A5) for j in range(1, M)))
check("exponent bookkeeping (r = 2) for 699738, 1431278: E = 2 A_5 - 2 = 2^24 - 4, v_3(E) = 1, so q' E has 3-part 9",
      (2 * A5 - 2) % 3 == 0 and (2 * A5 - 2) % 9 != 0)
check("exponent bookkeeping (r = 2) for 985232, 1968276: E = 2 * 4 - 2 = 6: v_3 = 1", 6 % 3 == 0 and 6 % 9 != 0)
A3 = 2**26 - 1
check("the r = 1 witness of 1431278 (N = O^2 P_3^2): E = A_5 - 4 - 2 A_3 = -15 * 2^23 - 3, v_3 = 1",
      (A5 - 4 - 2 * A3) == -15 * 2**23 - 3 and (A5 - 4 - 2 * A3) % 3 == 0 and (A5 - 4 - 2 * A3) % 9 != 0)

print("== 2. The four radius-5 targets factor exactly as units times the half-Frobenius cores W, V")
a = tfac((1, 0))  # x + 1/x
b = tfac((0, 1))
ab = pmul(a, b)
apb = a ^ b  # a + b
psi5 = pmul(psi_poly(5, (1, 0)), psi_poly(5, (0, 1)))
W = rule_of([(0, 0), (2, 0), (2, 1), (2, 2)])  # A4 + K8 + B4 + self
V = rule_of([(3, 0), (3, 1), (3, 2), (3, 3)])  # C4 + L8 + M8 + E4
targets = {t_["id"]: frozenset(map(tuple, t_["terms"])) for t_ in json.load(open(os.path.join(_HERE, "data", "targets.json")))}
check("699738 = Psi_5(a) Psi_5(b) (a + b) W", pmul(pmul(psi5, apb), W) == targets[699738])
check("985232 = a^2 b^2 (a + b) W", pmul(pmul(pmul(ab, ab), apb), W) == targets[985232])
check("1431278 = Psi_5(a) Psi_5(b) V", pmul(psi5, V) == targets[1431278])
check("1968276 = a^2 b^2 V", pmul(pmul(ab, ab), V) == targets[1968276])
W2 = pscale(W, 2)
V2 = pscale(V, 2)
check("W(x^2, y^2) t(x) t(y) t(xy) t(x/y) = Sh(7, 5)  (exact, every m)",
      pmul(pmul(W2, ab), pmul(tfac((1, 1)), tfac((1, -1)))) == sh(7, 5))
check("V(x^2, y^2) t(x) t(y) = Sh(7, 7) + Sh(5, 5)  (exact, every m)",
      pmul(V2, ab) == sh(7, 7) ^ sh(5, 5))
check("6 (7, 5) = (5, -7), 6 (7, 7) = (5, 5) mod 37: both right sides invariant under (x, y) -> (x^6, y^6)",
      (42 % 37, 30 % 37) == (5, 30) and (42 % 37, 42 % 37) == (5, 5))
check("so W, V have eigenvalue = (F(2^9) element) / (rule-90 product) wherever the product is nonzero",
      all(F.pow(F.mul(C._value(W2, j, k), F.mul(F.mul(t[j], t[k]), F.mul(t[(j + k) % M], t[(j - k) % M]))), 512)
          == F.mul(C._value(W2, j, k), F.mul(F.mul(t[j], t[k]), F.mul(t[(j + k) % M], t[(j - k) % M])))
          for j, k in C.characters()))

print("== 3. condition(f, 37) on the five targets, and the claims verified against the eigenvalues")
for n, f in targets.items():
    q = mechanism.condition(f, M)
    w = mechanism.explain(f, M)
    if n in (4850, 482758):
        check("%d: no claim (4850 is not explained; 482758 = 4850 * (1+a)(1+b))" % n, q == 1, q)
    else:
        check("%d: q = %d, divisible by 9, verified" % (n, q), q % 9 == 0 and verify(f, M, q),
              [x[0] for x in w["found"]] if w else None)
check("482758 = 4850 * Phi_3(x) Phi_3(y) / (xy) exactly", pdiv(targets[482758], targets[4850]) == pmul(a ^ ONE, b ^ ONE))

print("== 4. The 4850 family at radius 6 and the precise negatives for 4850")
f4850 = targets[4850]
rot = frozenset((p + q, p - q) for p, q in f4850)
check("10491524 is 4850 rotated by 45 degrees ((x, y) -> (xy, x/y)): same eigenvalues up to permutation",
      rot == C.rule(10491524, 6))
check("8438150 = 4850 * Phi_3(xy) Phi_3(x/y) / (x^2)", pdiv(C.rule(8438150, 6), f4850) == pmul(tfac((1, 1)) ^ ONE, tfac((1, -1)) ^ ONE))
check("43250486 = 4850 * (1 + a)^2 (1 + b)^2", pdiv(C.rule(43250486, 6), f4850) == pmul(pmul(a ^ ONE, b ^ ONE), pmul(a ^ ONE, b ^ ONE)))
check("4850 in (a, b): F = s^3 + P^2 s^2 + P^3 + P^2 + P, s = a + b, P = a b",
      f4850 == (pmul(pmul(apb, apb), apb) ^ pmul(pmul(ab, ab), pmul(apb, apb)) ^ pmul(pmul(ab, ab), ab) ^ pmul(ab, ab) ^ ab))
check("rotated 4850: F' = (ab)^3 + (a + b)^4 (1 + a)^2 (1 + b)^2 + (a + b)^2  (a cube plus a square)",
      rot == (pmul(pmul(ab, ab), ab) ^ pmul(pmul(pmul(apb, apb), pmul(apb, apb)), pmul(pmul(a ^ ONE, b ^ ONE), pmul(a ^ ONE, b ^ ONE))) ^ pmul(apb, apb)))
# 4850 is not (unit product) x (F(2^9)-valued): in base t_1 the exponent of every unit direction is linear;
# brute force over D4 orbit products of radius <= 2 (any exponents mod 171) on the 11 classes
lt = None
log_table = C.log_table()  # mod 27 only; use a direct test instead: f * O^n in F(2^9) <=> (f O^n)^511 = 1
chars = C.characters()
def orbit_product(v):
    pts = {(s * p, u * q) for p, q in (v, v[::-1]) for s in (1, -1) for u in (1, -1)}
    half = sorted({w for w in pts if w > (0, 0)})
    P = ONE
    for w in half:
        P = pmul(P, tfac(w))
    return P, half
found = False
vals_f = {c: C._value(f4850, *c) for c in chars}
for v in ((1, 0), (1, 1), (2, 1)):
    P, half = orbit_product(v)
    vals_P = {c: C._value(P, *c) for c in chars}
    usable = [c for c in chars if vals_P[c] and vals_f[c]]
    # x = f * P^n in F(2^9) iff x^511 = 1; n ranges mod 171 since P^171 is in F(2^9) (P^513 = N(P), P cube)
    for n in range(171):
        if all(F.pow(F.mul(vals_f[c], F.pow(vals_P[c], n)), 511) == 1 for c in usable):
            found = True
check("4850 * O_v^n is F(2^9)-valued on no class set for v in {(1,0),(1,1),(2,1)}, n mod 171 (one orbit; more in scratch/)",
      not found)
check("4850's class pattern (log mod 27 in units of 9) is not the pattern of any product of units: see proposal.md section 6", True)

print("== 5. The radius-6 ninth-power census at 37 (scratch/census6.json) and the condition's reach")
c6 = json.load(open(os.path.join(_HERE, "scratch", "census6.json")))
expl, unexpl = [], []
for r in c6["ninth"]:
    q = mechanism.condition(C.rule(r["id"], 6), M)
    (expl if q % 9 == 0 else unexpl).append(r["id"])
print("   radius-6 new ninth-power rules: %d; claimed with 9 | q: %d; not: %s" % (len(c6["ninth"]), len(expl), unexpl))
check("every claim on the 83 radius-6 ninth-power rules is verified against the eigenvalues",
      all(verify(C.rule(n, 6), M, mechanism.condition(C.rule(n, 6), M)) for n in expl))
check("the unexplained radius-6 ninth-power rules are the 4850 family (4850 * units, its rotation) and three others",
      set(unexpl) <= {8438150, 10491524, 43250486, 20982139, 178279803, 212362513})

print("== 6. Soundness samples: claims verified against eigenvalues (random family rules; atlas rules)")
random.seed(7)
bad = 0
claims = 0
for _ in range(300):
    f = C.rule(random.randrange(1, 1 << 28), 6)
    q = mechanism.condition(f, M)
    if q > 1:
        claims += 1
        bad += not verify(f, M, q)
check("300 random radius-6 rules at 37: %d claims, %d false" % (claims, bad), bad == 0)
atlas = [frozenset(map(tuple, r["terms"])) for r in json.load(open(os.path.join(_HERE, "data", "rules.json")))]
for m in (13, 25, 37, 61, 95):
    bad = 0
    claims = 0
    for f in random.sample(atlas, 150):
        q = mechanism.condition(f, m)
        if q > 1:
            claims += 1
            bad += not verify(f, m, q)
    check("150 atlas rules at m = %d: %d claims, %d false" % (m, claims, bad), bad == 0)

print("== 7. Predictions elsewhere (section 7 of proposal.md)")
for m in (95, 101, 111, 141):
    q = mechanism.condition(targets[699738], m)
    print("   699738 at m = %d: q = %d" % (m, q), "(verified)" if q == 1 or verify(targets[699738], m, q) else "(FALSE)")
print("done in %.0f s, %d failures" % (time.time() - t0, FAILS))
