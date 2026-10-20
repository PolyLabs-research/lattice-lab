"""The 3x3 'D-orbit' arrays L[p][q] = lambda(27^p j, 27^q k) and their row/column/diagonal
products, for 10491524 and relatives (and baselines)."""
import ff18 as F
from partialnorm2 import lamfun

def arrays(n, r, reps=((1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 7), (1, 8), (1, 10), (1, 13))):
    L = lamfun(n, r)
    for j, k in reps:
        A = [[L(pow(27, p, 37) * j, pow(27, q, 37) * k) for q in range(3)] for p in range(3)]
        V = [[F.v27(A[p][q]) for q in range(3)] for p in range(3)]
        S = [[F.z19pows().index(F.pw(A[p][q], F.E19)) for q in range(3)] for p in range(3)]
        rows = []
        for q in range(3):
            v = 1
            for p in range(3):
                v = F.mul(v, A[p][q])
            rows.append(v)
        rowinfo = [(F.v27(v), F.z19pows().index(F.pw(v, F.E19))) for v in rows]
        print('  (%d,%d) v27 %s  s19 %s  colprod(v27,s19) %s' % (j, k, V, S, rowinfo))

for n, r in [(10491524, 6), (20982139, 6), (4850, 4), (31234, 4)]:
    print('rule', n)
    arrays(n, r)
