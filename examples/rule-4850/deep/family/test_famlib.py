"""Sanity checks for famlib: f_{2,5} = rule 4850, fast field agrees with eigen's arithmetic, odd parts."""
import random, time
import famlib as L
import census, eigen
f25 = L.hex_rule(2, 5)
print('f_{2,5} == rule 4850:', f25 == census.rule(4850, 4), L.rule_number(f25))
print('f_{1,1} == s:', L.hex_rule(1, 1) == frozenset({(1,0),(-1,0),(0,1),(0,-1)}))
for m in (37, 109, 211, 271):
    F = L.GF(m)
    mod, d = eigen.field(m)
    random.seed(m)
    ok = True
    for _ in range(200):
        a, b = random.getrandbits(d), random.getrandbits(d)
        if F.mul(a, b) != eigen._mul(a, b, mod, d): ok = False
        if F.sqr(a) != eigen._mul(a, a, mod, d): ok = False
    e = random.getrandbits(d)
    ok &= F.pow(a, e) == eigen._pow(a, e, mod, d)
    t0 = time.time()
    for _ in range(20): F.pow(a, F.N // 3)
    print(m, 'd', d, 'A', F.A, 'mul/sqr/pow agree:', ok, ' pow time %.2f ms' % ((time.time()-t0)/20*1000))
# odd part of 4850 at 37
print('odd_part(4850, 37) =', eigen.odd_part(census.rule(4850, 4), 37), ' expected 29127')
