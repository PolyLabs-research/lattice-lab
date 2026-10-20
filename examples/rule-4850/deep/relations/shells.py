"""
The sparse products behind the trio (found by sigma_exact.py: g*ab has 12 terms).
Prints, in the Laurent ring (no reduction mod 37), the supports of 10491524*ab, 20982139*ab,
178279803*ab and of 4850(x^2,y^2) * t(xy) t(x/y), as unions of D4 shells, and checks that
dilation by 10 and 26 (the cube roots of 1 mod 37) permutes the shells mod 37.
    python shells.py
"""
import sys
from collections import Counter
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import run_targets as RT  # noqa: E402


def lmul(f, g):
    c = Counter()
    for p, q in f:
        for r, s in g:
            c[(p + r, q + s)] ^= 1
    return frozenset(k for k, v in c.items() if v)


def shells(S):
    out = Counter()
    for p, q in S:
        out[tuple(sorted((abs(p), abs(q)), reverse=True))] += 1
    return dict(out)


def dil(S, d, m=37):
    def red(v):
        v %= m
        return v - m if v > m // 2 else v
    return frozenset((red(d * p), red(d * q)) for p, q in S)


ab = RT.expset(4)
h = {}
for n in (10491524, 20982139, 178279803):
    h[n] = lmul(RT.expset(n), ab)
    print(n, "* ab:", len(h[n]), "terms, shells", shells(h[n]))
print("dil(h0, 10) == h1:", dil(h[10491524], 10) == h[20982139])
print("dil(h0, 26) == h2:", dil(h[10491524], 26) == h[178279803])
f2 = frozenset((2 * p, 2 * q) for p, q in RT.expset(4850))
u = RT.expset(8)  # a^2 + b^2 = t(xy) t(x/y)
k = lmul(f2, u)
print("4850(x^2,y^2) * t(xy)t(x/y):", len(k), "terms, shells", shells(k))
for n in (4850,):
    for un in (4, 8, 7, 13, 2, 3, 5, 6):
        P = lmul(RT.expset(n), RT.expset(un))
        print(f"  4850 * rule {un}: {len(P)} terms")
