"""
The two ninth-power-confined 2-term sparse numerators over x + y (sparse.py):
  4850:  [B(0,*) + B(17,3)]/(x+y)  ~  (Sh(1,0) + Sh(18,8))/(a+b), a Frobenius twist of
          (Sh(4,0) + Sh(5,2))/(a+b) = 4850;
  other: [B(0,*) + B(11,0)]/(x+y)  =  (Sh(1,0) + Sh(13,1))/(a+b).
Is the other one a GL2(Z/37) transport of 4850 (same multiset of eigenvalues up to Frobenius)?
We compare the multisets of logs mod 513 over all 1368 nonzero characters, and find a small
representative: the shells' images under dilations d (d*(13,1), d*(1,0) mod 37).
    python second.py
"""
import sys
from collections import Counter
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import tables  # noqa: E402
import run_targets as RT  # noqa: E402

F = tables.C.F
f18 = tables.f18
M = 37


def shell(p, q):
    return tables.C.points((max(abs(p), abs(q)), min(abs(p), abs(q))))


def eigs_quot(numer_shells, j, k):
    v = 0
    for p, q in numer_shells:
        for a, b in shell(p, q):
            v ^= RT.ZP[(a * j + b * k) % M]
    d = f18.t(j) ^ f18.t(k)
    return v, d


def multiset(numer):
    c = Counter()
    for j in range(M):
        for k in range(M):
            if (j, k) == (0, 0):
                continue
            v, d = eigs_quot(numer, j, k)
            if d == 0:
                continue  # the diagonal lines (a + b = 0): skip in both
            lg = f18.log(F.mul(v, F.inv(d)))
            c[lg % 513 if lg is not None else None] += 1
    return c


A = multiset([(4, 0), (5, 2)])
B = multiset([(1, 0), (13, 1)])
same = [s for s in range(18) if Counter({(None if k is None else k * pow(2, s, 513) % 513): v
                                         for k, v in B.items()}) == A]
print("4850 off the diagonal lines: ninth powers:", all(k is None or k % 9 == 0 for k in A))
print("other off the diagonal lines: ninth powers:", all(k is None or k % 9 == 0 for k in B))
print("multisets equal up to a Frobenius twist 2^s, s in", same)
for d in range(1, 19):
    sh = [tuple(sorted(((d * p + 18) % M - 18, (d * q + 18) % M - 18), key=abs, reverse=True))
          for p, q in [(1, 0), (13, 1)]]
    print("dilation", d, "->", sh)
