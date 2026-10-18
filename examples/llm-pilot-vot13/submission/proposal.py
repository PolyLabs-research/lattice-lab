"""Numerical check of the VO + T13 2-part law and its mechanism (see proposal.md).

Law: on the atlas's triangular torus of side n = 2^v m (m odd, v >= 1, n >= 4),
    period(VO + T13) = 2^e(v, m) * P(m),   e = v - 1 if m == 1 else v + 1,
where P(m) = period of triSVOT13Offsets on the square torus of side m.
"""
import csv
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
from gf2 import Field  # noqa: E402
from tori import S_VOT13, TRI_VOT13, period, square, torus, tri_period, triangle  # noqa: E402

ok_all = True


def report(name, ok):
    global ok_all
    ok_all &= bool(ok)
    print(("HOLDS " if ok else "FAILS ") + name)


def two_exp(v, m):
    return v - 1 if m == 1 else v + 1


here = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(here, "data", "vot13_periods.csv"))))
Pm = {}
for r in rows:
    m = int(r["m"])
    if m not in Pm and m <= 21:
        Pm[m] = period(square(m), S_VOT13)

# 1. The law against the engine's data (P(m) computed by the tools for m <= 21; for larger m,
#    the law predicts the odd part, which we check is odd and the 2-part is exactly 2^e).
for r in rows:
    n, v, m, p = int(r["n"]), int(r["v"]), int(r["m"]), int(r["period"])
    e = two_exp(v, m)
    if m in Pm:
        report(f"n={n}: period {p} == 2^{e} * P({m})={Pm[m]}", p == 2**e * Pm[m])
    else:
        odd = p >> e
        report(f"n={n}: period {p} has 2-part exactly 2^{e} (odd part {odd})",
               p % 2**e == 0 and odd % 2 == 1)

# 2. Independent recomputation on small atlas tori with the tools.
for n in range(4, 23, 2):
    v = (n & -n).bit_length() - 1
    m = n >> v
    p = tri_period(triangle(n), TRI_VOT13)
    report(f"tri_period(triangle({n})) = {p} == 2^{two_exp(v, m)} * P({m})",
           p == 2 ** two_exp(v, m) * Pm[m])

# 3. Mechanism, m >= 3: on the sub-torus Z/2m x Z/m, psi1 = zeta^a zeta^b, psi2 = psi1 [a even]
#    is a Jordan block with lam = sum zeta^-d1 = 1 and mu = sum zeta^-d1 [d1-d2 odd]
#    = (zeta + 1/zeta)^3, nonzero for m >= 3.
lam, mu = Counter(), Counter()
for d1, d2 in S_VOT13:
    lam[-d1] += 1
    if (d1 - d2) % 2:
        mu[-d1] += 1
lam = {k for k, c in lam.items() if c % 2}
mu = {k for k, c in mu.items() if c % 2}
report("lam(zeta) = 1 as a Laurent polynomial over GF(2)", lam == {0})
report("mu(zeta) = zeta^3 + zeta + zeta^-1 + zeta^-3 = (zeta + 1/zeta)^3", mu == {3, 1, -1, -3})
for m in (3, 5, 7, 9, 11, 13, 15):
    F = Field(m)
    z = F.zeta
    T = torus(2 * m, m, lambda d: (d[0] - d[1], d[1]))

    def psi1(w, F=F, z=z):
        return F.mul(F.pow(z, w[0]), F.pow(z, w[1]))

    def psi2(w, F=F, z=z, psi1=psi1):
        return psi1(w) if w[0] % 2 == 0 else 0

    from tori import check_jordan
    muv = F.add(F.add(F.pow(z, 3), z), F.add(F.inv(z), F.pow(z, -3)))
    res = check_jordan(T, S_VOT13, psi1, psi2, F.one, muv, F)
    report(f"m={m}: Jordan block on Z/{2*m} x Z/{m}", res["ok"])
    pT = period(T, S_VOT13)
    report(f"m={m}: period on the sub-torus ({pT}) is even, = 2 P(m)", pT == 2 * Pm[m])

# 4. Mechanism, m = 1: on Z/4 x Z/2 the 49 translations land an odd number of times only on 0
#    (so S is the identity there); on Z/8 x Z/4 they do not (S has period 2 there).
for M, expect_identity in ((2, True), (4, False)):
    c = Counter(((d1 - d2) % (2 * M), d2 % M) for d1, d2 in S_VOT13)
    odd = {g for g, k in c.items() if k % 2}
    report(f"S on Z/{2*M} x Z/{M} is {'the identity' if expect_identity else 'not the identity'}",
           (odd == {(0, 0)}) == expect_identity)
    c2 = Counter(((2 * (d1 - d2)) % (2 * M), (2 * d2) % M) for d1, d2 in S_VOT13)
    odd2 = {g for g, k in c2.items() if k % 2}
    report(f"2S on Z/{2*M} x Z/{M} is the identity (S is an involution there)", odd2 == {(0, 0)})
pT = period(torus(4, 2, lambda d: (d[0] - d[1], d[1])), S_VOT13)
report(f"period of S on Z/4 x Z/2 = {pT} == 1", pT == 1)
pT = period(torus(8, 4, lambda d: (d[0] - d[1], d[1])), S_VOT13)
report(f"period of S on Z/8 x Z/4 = {pT} == 2", pT == 2)

print("ALL CHECKS HOLD" if ok_all else "SOME CHECK FAILED")
