"""Candidate identity: for M = diag(27, 11) (order 3 in SL2(Z/37) mod sign), is
   Q(c) = G(Mc) / G(c)  in F(2^9)  for G = lambda' * m, m a simple multiplier?"""
import itertools, random
import numpy as np
import ff18 as F
import vec

T = F.tvec()
MULTS = {
    '1': lambda a, b: 1,
    'ab': lambda a, b: F.mul(T[a], T[b]),
    '(ab)^2': lambda a, b: F.pw(F.mul(T[a], T[b]), 2),
    '(ab)^-1': lambda a, b: F.inv(F.mul(T[a], T[b])),
    'a+b': lambda a, b: T[a] ^ T[b],
}


def test(n, r, Mdiag=(27, 11), mult='ab'):
    V = vec.values([n], r)[0]
    good = 0; tot = 0; bad_examples = []
    for al in range(1, 37):
        for be in range(1, 37):
            c = (al, be); Mc = (Mdiag[0] * al % 37, Mdiag[1] * be % 37)
            g1 = F.mul(int(V[vec.red(c[0]), vec.red(c[1])]), MULTS[mult](*c))
            g2 = F.mul(int(V[vec.red(Mc[0]), vec.red(Mc[1])]), MULTS[mult](*Mc))
            if g1 == 0 or g2 == 0:
                continue
            tot += 1
            q = F.mul(g2, F.inv(g1))
            if F.in_F512(q):
                good += 1
    return good, tot


for n, r in [(10491524, 6), (20982139, 6), (178279803, 6), (7, 4), (41, 4), (31234, 4)]:
    res = {m: test(n, r, mult=m) for m in MULTS}
    print(n, {m: '%d/%d' % v for m, v in res.items()})
