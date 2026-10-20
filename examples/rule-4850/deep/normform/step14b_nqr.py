"""Step 14b: tabulate, for chi(be/al) = -1, the index-3 period theta_k = N(W)(al, be): k as a function of
(i, j) = (log2 al mod 6, log2 be mod 6); also (log2 al mod 12, log2 be mod 12) to see if mu6 x mu6 is the right group."""
import nf
from step14_NWformula import NW, theta, eta, m
lg2 = {pow(2, k, m): k for k in range(36)}
tk = {}
for k in range(3):
    tk[theta(pow(2, k, m))] = k
tab = {}
for al in range(1, m):
    for be in range(1, m):
        if nf.legendre(be * pow(al, -1, m)) == -1:
            key = (lg2[al] % 6, lg2[be] % 6)
            tab.setdefault(key, set()).add(tk[NW(al, be)])
print('k(i, j) for i - j odd (sets: should be singletons):')
for i in range(6):
    print('  i=%d:' % i, ['%s' % (tab.get((i, j), '-')) for j in range(6)])
