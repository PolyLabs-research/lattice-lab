"""
Numerical checks of the half-Frobenius confinement mechanism (proposal.md, mechanism.py).

Run:  ./python proposal.py          (a few minutes)
Prints each check and whether it held.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

import mechanism as M  # noqa: E402
from eigen import Field, full_bound, odd_part, orbits  # noqa: E402

RULES = json.load(open(os.path.join(ROOT, "data", "rules.json")))
BYNAME = {(r["lattice"], "+".join(r["shells"])): frozenset(map(tuple, r["terms"])) for r in RULES}
SIX = [("square", "A4+K8+B4+self"), ("square", "K8+M8+E4"), ("square", "C4+L8+M8"),
       ("square", "C4+L8+M8+E4"), ("square", "A4+B4+C4+L8+E4+self"),
       ("triangle", "VS+T9+T13+self")]  # fmt: skip

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"[{'held' if ok else 'FAILED'}] {name}" + (f"  ({detail})" if detail else ""), flush=True)


def t(*w):
    return M.tfac(w)


def prod(*polys):
    out = M.ONE
    for P in polys:
        out = M.pmul(out, P)
    return out


def sq_shell(u, v):
    return frozenset((a * x, b * y) for x, y in ((u, v), (v, u)) for a in (1, -1) for b in (1, -1))


def hex_orbit(v):
    S, (p, q) = set(), v
    for _ in range(6):
        S |= {(p, q), (q, p)}
        p, q = p - q, p
    return frozenset(S)


def all_qth_powers(f, m, q):
    """Independent check with the tools: every nonzero eigenvalue of f at m is a q-th power."""
    F = Field(m)
    zt = [1] * m
    for i in range(1, m):
        zt[i] = F.mul(zt[i - 1], F.zeta)
    e = F.order // q
    for (j, k), _ in orbits(m):
        v = 0
        for x, y in f:
            v ^= zt[(x * j + y * k) % m]
        if v and F.pow(v, e) != 1:
            return False
    return True


def main():
    t0 = time.time()
    W, V = BYNAME[SIX[0]], BYNAME[SIX[3]]
    S = BYNAME[SIX[5]]
    O10, O11 = prod(t(1, 0), t(0, 1)), prod(t(1, 1), t(1, -1))
    a, b = t(1, 0), t(0, 1)

    print("== 1. exact identities over GF(2)")
    check("W(x^2,y^2) * t(x) t(y) t(xy) t(x/y) = Sh(7,5)",
          prod(M.pscale(W, 2), O10, O11) == sq_shell(7, 5))
    check("V(x^2,y^2) * t(x) t(y) = Sh(7,7) + Sh(5,5)",
          prod(M.pscale(V, 2), O10) == sq_shell(7, 7) ^ sq_shell(5, 5))
    check("K8+M8+E4 = a b W", BYNAME[SIX[1]] == prod(a, b, W))
    check("C4+L8+M8 = (a + b) W", BYNAME[SIX[2]] == prod(a ^ b, W))
    check("A4+B4+C4+L8+E4+self = (a+1)(b+1) W",
          BYNAME[SIX[4]] == prod(a ^ M.ONE, b ^ M.ONE, W))
    Oh1 = prod(t(1, 0), t(0, 1), t(1, 1))
    Oh2 = prod(t(2, 1), t(1, 2), t(1, -1))
    hexB = M.pscale(hex_orbit((7, 6)) | hex_orbit((6, 5)), 2)
    check("triangle s: S(x^2,y^2) * O(1,0) O(2,1) = Hex(14,12) + Hex(12,10)",
          prod(M.pscale(S, 2), Oh1, Oh2) == hexB)
    check("2^9 = -6 and 6^2 = -1 mod 37", pow(2, 9, 37) == 37 - 6 and 36 % 37 == 37 - 1)
    for name, B in [("Sh(7,5)", sq_shell(7, 5)), ("Sh(7,7)+Sh(5,5)", sq_shell(7, 7) ^ sq_shell(5, 5)),
                    ("Hex(14,12)+Hex(12,10)", hexB)]:  # fmt: skip
        Bm = M.preduce(B, 37)
        check(f"{name} invariant under x 2^9 mod 37", M.preduce(M.pscale(Bm, 2**9), 37) == Bm)

    print("== 2. condition on the six rules at m = 37, and the eigenvalues")
    q37 = 3 * (2**18 + 1)
    for key in SIX:
        f = BYNAME[key]
        w = M.explain(f, 37)
        q = w["q"] if w else 1
        check(f"condition({key[1]}, 37) = {q}", q == q37,
              f"r={w['r']}, units={w['units']}, N={w['N']}, g={w['g']}" if w else "")
        check(f"  all eigenvalues of {key[1]} are {q37}-th powers in F(2^36) (cubes of F(2^18))",
              all_qth_powers(f, 37, q37))
        check(f"  odd part of {key[1]} at 37 is 87381", odd_part(f, 37) == 87381)

    print("== 3. closed forms at 37 (p = t_{(j+k)/2}, q = t_{(j-k)/2})")
    F = Field(37)
    h = 19  # 1/2 mod 37

    def tv(j):
        return F.pow(F.zeta, j % 37) ^ F.pow(F.zeta, (-j) % 37)

    okW = okV = True
    cnt = 0
    for (j, k), _ in orbits(37):
        p, qq = tv(h * (j + k)), tv(h * (j - k))
        den = F.mul(p, F.mul(qq, p ^ qq))
        if not den:
            continue
        cnt += 1
        lamW = 0
        for x, y in W:
            lamW ^= F.pow(F.zeta, (x * j + y * k) % 37)
        lamV = 0
        for x, y in V:
            lamV ^= F.pow(F.zeta, (x * j + y * k) % 37)
        Q = 2**9
        tr = F.mul(F.pow(p, Q), qq) ^ F.mul(p, F.pow(qq, Q))
        okW &= F.mul(lamW, den) == tr
        nrm = F.pow(p, Q + 1) ^ F.pow(qq, Q + 1)
        okV &= F.mul(lamV, p ^ qq) == nrm
    check(f"lambda_W = Tr(p^(2^9) q) / (pq(p+q)) at all {cnt} orbit characters with pq(p+q) != 0", okW)
    check("lambda_V = (N(p) + N(q)) / (p + q) there", okV)

    print("== 4. rule 90 at 37")
    QR = sorted({x * x % 37 for x in range(1, 37)})
    pr = 1
    for hh in QR:
        pr = F.mul(pr, 1 ^ F.pow(F.zeta, hh))
    check("prod over squares h mod 37 of (1 + zeta^h) = 1  (N_{F(2^18)/F_4}(t_1) = 1)", pr == 1)
    check("rule 90's odd part at 37 is 87381 = (2^18-1)/3",
          odd_part(frozenset({(1, 0), (-1, 0)}), 37) == 87381 == full_bound(37) // 3)

    print("== 5. soundness: every claim of condition, at several m, checked by eigenvalues")
    for m in (13, 21, 37, 101, 111):
        tm = time.time()
        claims = bad = 0
        for r in RULES:
            f = frozenset(map(tuple, r["terms"]))
            q = M.condition(f, m)
            if q > 1:
                claims += 1
                if not all_qth_powers(f, m, q):
                    bad += 1
                    print("   false claim:", r["lattice"], r["shells"], m, q)
        check(f"m = {m}: {claims} claims, all hold", bad == 0, f"{time.time() - tm:.0f}s")

    print("== 6. census entries explained")
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "unexplained.csv"))))
    expl = []
    for row in rows:
        m = int(row["m"])
        f = BYNAME[(row["lattice"], row["shells"])]
        q = M.condition(f, m)
        if q > 1:
            # the claim must imply the census's q-th powers in F(2^sord)
            s, d = M.sord(m), M.ord2(m)
            implied = q // ((2**d - 1) // (2**s - 1))
            expl.append((m, row["lattice"], row["shells"], implied))
    print(f"   {len(expl)} of {len(rows)} census entries are claimed by condition:")
    for e in expl:
        print("    ", e)
    check("the six rules at 37 are among them",
          all((37, k[0], k[1]) in {(e[0], e[1], e[2]) for e in expl} for k in SIX))

    print("== 7. the six rules at the other odd m in 9..161: no claim (they reach the full bound)")
    ok = True
    for m in range(9, 162, 2):
        if m == 37:
            continue
        for key in SIX:
            if M.condition(BYNAME[key], m) > 1:
                ok = False
                print("   claim at", m, key)
    check("condition claims nothing for the six away from 37", ok)

    print(f"\n{sum(RESULTS)} of {len(RESULTS)} checks held  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
