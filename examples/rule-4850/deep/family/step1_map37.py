"""Step 1. The hexagon family f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T)/s at m = 37 for 1 <= p, q <= 20:
exact odd part of the period (linear-atlas-3/eigen.odd_part), confinement level relative to 2^18 - 1,
and the bookkeeping data: type (-3: q = +-16p, +3: q = +-12p... i.e. q^2 = 3p^2, 'pp': q = p),
Legendre symbol of p, k = ind_2(p) mod 18 (p up to sign), parities, zero classes."""
import json, math, time
import famlib as L
import sympy

M = 37
N18 = 2 ** 18 - 1
IND = {pow(2, k, M): k for k in range(36)}


def kind(p, q):
    if (q * q + 3 * p * p) % M == 0:
        return '-3'
    if (q * q - 3 * p * p) % M == 0:
        return '+3'
    if (q - p) % M == 0 or (q + p) % M == 0:
        return 'pp'
    return ''


out = []
t0 = time.time()
for p in range(1, 21):
    for q in range(1, 21):
        f = L.hex_rule(p, q)
        op = L.odd_part(f, M)
        rn = L.rule_number(f)
        rec = dict(p=p, q=q, kind=kind(p, q), terms=len(f), radius=max(max(abs(a), abs(b)) for a, b in f),
                   rule=rn[0] if rn else None, odd_part=op, level3=int(sympy.multiplicity(3, N18 // op)) if N18 % op == 0 else None,
                   divides=N18 % op == 0, chi_p=L.legendre(p, M), chi_q=L.legendre(q, M),
                   k=IND[p % M] % 18 if p % M else None, parity=(p % 2, q % 2))
        out.append(rec)
print('time %.1f s' % (time.time() - t0))
json.dump(out, open('step1_map37.json', 'w'), indent=1)
from collections import Counter
print('odd parts over all 400:', Counter(r['odd_part'] for r in out).most_common())
for kd in ('-3', '+3', 'pp'):
    print('--- kind', kd)
    for r in out:
        if r['kind'] == kd:
            print('  (%2d,%2d) chi_p=%+d k=%2d par=%s terms=%4d odd_part=%6d level3=%s' % (
                r['p'], r['q'], r['chi_p'], r['k'], r['parity'], r['terms'], r['odd_part'], r['level3']))
print('--- other kinds with level3 >= 1 (cube-confined or better):')
for r in out:
    if r['kind'] == '' and r['level3'] and r['level3'] >= 1:
        print('  ', (r['p'], r['q']), r['odd_part'], r['level3'], 'gcd', math.gcd(r['p'], r['q']))
