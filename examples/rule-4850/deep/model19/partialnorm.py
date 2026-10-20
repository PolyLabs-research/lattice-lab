"""Explore the partial norms N_x(c) = prod_{h in <27>} lambda(h j, k) for 10491524 & co.
(<27> = {1, 27, 26} mod 37 is the order-3 subgroup; dilation by 27 = 2^6 is Frob^6.)"""
import sys
import ff18 as F

H3 = [1, 27, 26]
def lam(n, r):
    cache = {}
    def f(j, k):
        key = (j % 37, k % 37)
        if key not in cache:
            cache[key] = F.rule_value(n, r, *key)
        return cache[key]
    return f

for n, r in [(10491524, 6), (20982139, 6), (178279803, 6), (4850, 4), (12345, 4)]:
    L = lam(n, r)
    print('rule', n)
    for k in (1, 2, 3, 5):
        row = []
        for j in (1, 2, 3, 4, 5, 6, 7):
            v = 1
            for h in H3:
                v = F.mul(v, L(h * j, k))
            a, w, z = F.comps(v)
            row.append((F.v27(v), F.z19pows().index(z), F.in_F512(v)))
        # compare with t_k components
        print('  k=%d' % k, row, ' s(t_k)=', F.z19pows().index(F.pw(F.tvec()[k], F.E19)))
