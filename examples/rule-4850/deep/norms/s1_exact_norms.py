"""Step 1 (norms): N(al, be) = N_{K/F64}(W(al, be)) at EVERY character (al, be) in (F37*)^2, exactly.

Method 1 (exact, no field): the char-0 group-ring element  Ntilde = prod_{c in <27>} W(c al, c be)  in Z[Z/37]
(1728 exponents, integer counts), whose reduction mod 2 (and mod J = sum x^i) is N.  It is invariant under
multiplication by mu6 (Galois sigma), so  Ntilde = c0 + sum_i c_i eta_i, eta_i = sum_{u in mu6} zeta^(2^i u).
Method 2 (field): N computed in a self-built GF(2^36) as W * sigma(W) * sigma^2(W), sigma = Frob^6,
compared with the period expansion.  Then the formula on (Z/6)^2, (i, j) = (log2 al, log2 be) mod 6."""
import json
import collections
import numpy as np
import nlib

p = 37
S = nlib.Setting(p)
assert S.sig_k == 6 and pow(2, 6, p) == 27
lg = S.two
cos = {x: lg[x] % 6 for x in range(1, p)}
eta = [S.eta(pow(2, i, p)) for i in range(6)]
theta = [eta[i] ^ eta[i + 3] for i in range(3)]
mu6 = S.mu6

out = {'char0': {}, 'mod2': {}, 'checks': {}}
table = {}
ok_field = True
for al in range(1, p):
    for be in range(1, p):
        v, orb = nlib.NW_groupring(al, be, p, 10)  # mu3 = <10>: sigma = Frob^6 acts as x27 = x(-10), W even
        assert sorted(orb) == sorted(nlib.mu(3, p))
        # Galois invariance: counts constant on mu6-cosets
        per = collections.defaultdict(set)
        for x in range(1, p):
            per[cos[x]].add(int(v[x]))
        assert all(len(s) == 1 for s in per.values())
        c = [int(v[0])] + [per[i].pop() for i in range(6)]
        key = (cos[al], cos[be])
        table.setdefault(key, set()).add(tuple(c))
        # mod 2, normalised c0 = 0 (relation 1 + sum eta_i = 0)
        c2 = [x % 2 for x in c]
        if c2[0]:
            c2 = [1 - x for x in c2]
        # field check
        val = 0
        for i in range(6):
            if c2[i + 1]:
                val ^= eta[i]
        N = S.norm_Kk(S.W(al, be))
        if N != val:
            ok_field = False
out['checks']['period expansion == field norm at all 1296 characters'] = ok_field
print('period expansion == field norm at all 1296 characters:', ok_field)
assert all(len(s) == 1 for s in table.values())
print('N(al, be) depends only on (log2 al, log2 be) mod 6:', all(len(s) == 1 for s in table.values()))

# tabulate char-0 coefficient vectors and mod-2 values
def name_mod2(c):
    c2 = [x % 2 for x in c]
    if c2[0]:
        c2 = [1 - x for x in c2]
    s = [i for i in range(6) if c2[i + 1]]
    return s


rows = []
for i in range(6):
    for j in range(6):
        c = list(table[(i, j)])[0]
        s = name_mod2(c)
        kind = 'QR' if (i - j) % 2 == 0 else 'NQR'
        if s == []:
            desc = '0'
        elif len(s) == 1:
            desc = 'eta_%d' % s[0]
        elif len(s) == 2 and s[1] - s[0] == 3:
            desc = 'theta_%d' % s[0]
        else:
            desc = '+'.join('eta_%d' % x for x in s)
        rows.append(dict(i=i, j=j, kind=kind, char0=c, mod2_support=s, desc=desc))
for r in rows:
    print(r['i'], r['j'], r['kind'], 'char0 (c0; c_0..c_5) =', r['char0'], ' mod 2:', r['desc'])

# formulas
qr_ok = all(r['desc'] == 'eta_%d' % ((2 + 2 * r['i'] - r['j']) % 6) for r in rows if r['kind'] == 'QR')
print('QR (i - j even):  N = eta_{2 + 2i - j} = eta(4 al^2 / be):', qr_ok)
nqr = {(r['i'], r['j']): r['desc'] for r in rows if r['kind'] == 'NQR'}
is_theta = all(v.startswith('theta') for v in nqr.values())
print('NQR (i - j odd): N is an index-3 period theta_k:', is_theta)
kappa = collections.defaultdict(set)
for (i, j), v in nqr.items():
    k = int(v.split('_')[1])
    kappa[(j - i) % 6].add((k - i) % 3)
print('k - i mod 3 as a function of d = j - i mod 6:', dict(kappa))
out['mod2'] = {'%d,%d' % (r['i'], r['j']): r['desc'] for r in rows}
out['char0'] = {'%d,%d' % (r['i'], r['j']): r['char0'] for r in rows}
out['checks']['QR formula eta(4 al^2/be)'] = qr_ok
out['checks']['NQR all theta'] = is_theta
out['kappa'] = {str(k): sorted(v) for k, v in kappa.items()}
json.dump(out, open('s1_exact_norms.json', 'w'), indent=1)
