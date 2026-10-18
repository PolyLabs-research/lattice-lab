"""
Numerical check of the mechanism in proposal.md.

For n = 2^v m (m odd >= 3, v >= 1):
 1. the sub-torus G' = Z/2m x Z/m with omega'(x, y) = (x - y mod 2m, y mod m) embeds in the
    atlas's triangular torus G of side n by multiplication by 2^(v-1), with
    mu(omega'(d)) = omega(2^(v-1) d), injectively;
 2. on G', the weights psi1(a, b) = zeta^(a + b), psi2 = psi1 * [a even] form a Jordan block of
    the adjoint of s (both s_E and s_EVOVS), with lam = 1, mu = zeta + 1/zeta for s_E and
    lam = mu = zeta^2 + 1/zeta^2 for s_EVOVS (both nonzero for m >= 3);
 3. consequently every period of s on G' is even; we also compute the periods directly;
 4. the end result: tri_period(triangle(n), R) == 2^(v+1) * period(square(m), s).
"""
import sys

sys.path.insert(0, "tools")
from gf2 import Field  # noqa: E402
import tori  # noqa: E402

ok_all = True


def report(name, ok):
    global ok_all
    ok_all &= bool(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {name}")


def sub_torus(m):
    return tori.torus(2 * m, m, lambda d: (d[0] - d[1], d[1]))


# 1. the embedding
for m in [3, 5, 7, 9]:
    for v in [1, 2, 3]:
        n = 2 ** v * m
        N = 2 ** (v - 1)
        G, Gp = tori.triangle(n), sub_torus(m)
        mu = lambda c: ((N * c[0]) % G.a, (N * c[1]) % G.b)
        img = {mu(c) for c in Gp.cells()}
        inj = len(img) == len(Gp.cells())
        hom = all(
            mu(Gp.image(d)) == G.image((N * d[0], N * d[1]))
            for d in [(1, 0), (0, 1), (3, -2), (-5, 7)]
        )
        report(f"embedding G'(m={m}) -> G(n={n}) by 2^(v-1): injective={inj}, compatible={hom}",
               inj and hom)

# 2. the Jordan block
for m in [3, 5, 7, 9, 11, 13, 15, 21]:
    F = Field(m)
    z = F.zeta
    zi = F.inv(z)
    Gp = sub_torus(m)
    psi1 = lambda w: F.pow(z, w[0] + w[1])
    psi2 = lambda w: psi1(w) if w[0] % 2 == 0 else 0
    lamE, muE = 1, F.add(z, zi)
    r = tori.check_jordan(Gp, tori.S_E, psi1, psi2, lamE, muE, F)
    report(f"m={m}: Jordan block for s_E on G' (lam=1, mu=z+1/z): {r}", r["ok"])
    z2 = F.add(F.pow(z, 2), F.pow(z, -2))
    r = tori.check_jordan(Gp, tori.S_EVOVS, psi1, psi2, z2, z2, F)
    report(f"m={m}: Jordan block for s_EVOVS on G' (lam=mu=z^2+1/z^2): {r}", r["ok"])

# 3. periods on G' are even, while P(m) is odd
for m in [3, 5, 7, 9, 11]:
    for name, S in [("s_E", tori.S_E), ("s_EVOVS", tori.S_EVOVS)]:
        pG = tori.period(sub_torus(m), S)
        pm = tori.period(tori.square(m), S)
        report(f"m={m}: period of {name} on G' = {pG} (even), on square m = {pm} (odd), "
               f"ratio {pG / pm}", pG % 2 == 0 and pm % 2 == 1 and pG == 2 * pm)

# 4. the law
for m in [3, 5, 7, 9]:
    for v in [1, 2, 3]:
        n = 2 ** v * m
        if n > 28:
            continue
        for name, R, S in [("triE", tori.TRI_E, tori.S_E), ("triEVOVS", tori.TRI_EVOVS, tori.S_EVOVS)]:
            P = tori.tri_period(tori.triangle(n), R)
            pm = tori.period(tori.square(m), S)
            report(f"n={n} (m={m}, v={v}) {name}: period {P} = 2^{v + 1} * {pm}? ",
                   P == 2 ** (v + 1) * pm)

print("ALL OK" if ok_all else "SOME CHECK FAILED")
