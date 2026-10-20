"""Step 8: full logs of the ratios rho = lambda(20982139)/lambda(10491524) (and 178279803) at the
11 classes, modulo 19 and 73 (their orders divide 1387 = 19*73), and a search over the radius-4
and radius-5 families for rules h with rho = h^e (one exponent e for all classes), i.e. the ratio
being a power of a small rule's eigenvalues; also rho = h1^e1 h2^e2 is not attempted (too loose)."""
import time
import numpy as np
from rlib import *
from fulllog import *

t0 = time.time()
LOG = log_table()
print('log table', round(time.time() - t0, 1), 's')
base = rule_class_values(10491524, 6)
lb = np.array([LOG[v] for v in base])
targets = {}
for n in (20982139, 178279803):
    lv = np.array([LOG[v] for v in rule_class_values(n, 6)])
    r = (lv - lb) % N18
    assert (r % 189 == 0).all()
    targets[n] = r
    print(n, 'rho logs/189 mod 1387:', list((r // 189) % 1387), ' mod 19:', list((r // 189) % 19), ' mod 73:', list((r // 189) % 73))
# log of rho mod 1387 in terms of the subgroup generator g^189: rho = (g^189)^(r/189)
for radius in (4, 5):
    t0 = time.time()
    V = family_values(radius)
    L = LOG[V]  # -1 where zero
    ok = (L >= 0).all(axis=0)
    print(f'radius {radius}: {V.shape[1]} rules, nonvanishing {ok.sum()}  ({time.time() - t0:.1f}s)')
    for n, r in targets.items():
        tgt = (r // 189) % 1387  # rho = G^tgt, G = g^189 of order 1387
        hits = []
        # h^e = rho  <=>  e * L_h = 189 * tgt  (mod N18) at each class.
        # Reduce: for p in (19, 73): e * L_h = 189 tgt (mod p) [189 invertible mod p], and
        # for the 3- and 7-parts: e * L_h = 0 (mod 27) and (mod 7).
        for p in (19, 73):
            pass
        Lh = L[:, ok]
        idx = np.flatnonzero(ok)
        good = np.ones(Lh.shape[1], dtype=bool)
        sols = {}
        for p in (19, 73):
            a = Lh % p
            b = (189 * tgt) % p
            # find e mod p with e*a = b for all classes: candidate from first class with a != 0
            es = np.full(Lh.shape[1], -1, dtype=np.int64)
            for c in range(a.shape[0]):
                need = (es < 0) & (a[c] != 0)
                es[need] = (b[c] * np.array([pow(int(x), -1, p) for x in a[c][need]], dtype=np.int64)) % p if need.any() else es[need]
            es[es < 0] = 0
            consistent = ((es[None, :] * a - b[:, None]) % p == 0).all(axis=0)
            good &= consistent
            sols[p] = es
        # 3- and 7-parts: need e*L_h = 0 mod 27 and mod 7 -> e can be chosen = 0 mod 189 always; fine.
        cand = idx[good]
        print(f'   target {n}: rules h of radius {radius} with rho = h^e: {len(cand)}', list(cand[:20]))
