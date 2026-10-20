"""Do any two class values of 4850 (or its relatives) coincide up to Frobenius or F_512* ?
(a hidden symmetry would make the eight conditions dependent).  Also the norm form of the
condition: lambda is a ninth power iff N_{F(2^18)/F_64}(lambda) lies in F_8 = mu_7 + {0}."""
from rlib import *
KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
for n, r in [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6)]:
    F = rule_F(n, r)
    vals = {k: val_t1(Q_dickson(F, k)) for k in KS}
    rel = []
    for k1 in KS:
        for k2 in KS:
            if k1 < k2:
                for j in range(18):
                    if f18_pow(vals[k1], 2 ** j) == vals[k2]:
                        rel.append((k1, k2, 'frob', j))
                    q = f18_mul(f18_pow(vals[k1], 2 ** j), f18_pow(vals[k2], N18 - 1))
                    if f18_pow(q, 512) == q:
                        rel.append((k1, k2, 'F512*', j))
    norms = {}
    for k in KS:
        N = f18_mul(f18_mul(vals[k], f18_pow(vals[k], 64)), f18_pow(vals[k], 4096))
        Nk = to64_from18(N)
        norms[k] = (LOG64[Nk], LOG64[Nk] % 9 == 0)
    print(n, 'relations:', rel)
    print('   norms to F_64 as w^e (in F_8 iff 9 | e):', norms)
