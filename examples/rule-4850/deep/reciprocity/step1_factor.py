"""Step 1: the line polynomials and their factorisations over GF(2).

For each rule: Q_i(T) = F(T, D_{2^i}(T)) = F(T, T^(2^i)) for i = 0..9 (the class (1, 2^i)), and
G_k(T) = F(T, D_k(T)) for the census representatives k (the same class values up to Frobenius).
Each irreducible factor P is labelled by the smallest e with P | Psi_e (cyclotomic) or '-', and by
the log mod 9 of P(t_1) in F(2^18)* (generator rlib.f18_generator()).  The class value's log mod 9 is
the multiplicity-weighted sum.  Output: step1_factor.txt (human) and step1_factor.json."""
import json, sys, time
from rlib import *

RULES = [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)]
KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
POW2 = [pow(2, i, 37) for i in range(10)]

def canon(k):
    """census representative of the class of (1, k)"""
    orb = {k % 37, -k % 37, pow(k, -1, 37), -pow(k, -1, 37) % 37}
    for kk in KS:
        if kk in orb:
            return kk

def describe(Q):
    cyc = cyclo_table()
    out = []
    tot = 0
    for p, e in factor2(Q):
        v = val_t1(p)
        l = None if v == 0 else log9(v)
        lab = ('T' if p == 2 else f'Psi{cyc[p]}') if p in cyc else '-'
        out.append({'poly': p, 'deg': deg(p), 'mult': e, 'cyc': lab, 'log9': l})
        if l is not None:
            tot += e * l
    return out, tot % 9

if __name__ == '__main__':
    res = {}
    lines = []
    t0 = time.time()
    for n, r in RULES:
        F = rule_F(n, r)
        lines.append(f'=== rule {n} (radius {r}); F(a,b) = {F_str(F)}')
        rec = {'F': sorted(F), 'Q': {}, 'G': {}}
        for i in range(10):
            Q = Q_dickson(F, 2 ** i)
            facs, tot = describe(Q)
            rec['Q'][i] = {'deg': deg(Q), 'factors': facs, 'log9': tot}
            s = ', '.join(f"{f['deg']}{'^%d' % f['mult'] if f['mult'] > 1 else ''}[{f['cyc']}:{f['log9']}]" for f in facs)
            lines.append(f'  Q_{i} (class k={canon(POW2[i])}) deg {deg(Q)}: {s}  => log9 {tot}')
        for k in KS:
            G = Q_dickson(F, k)
            facs, tot = describe(G)
            rec['G'][k] = {'deg': deg(G), 'factors': facs, 'log9': tot}
            s = ', '.join(f"{f['deg']}{'^%d' % f['mult'] if f['mult'] > 1 else ''}[{f['cyc']}:{f['log9']}]" for f in facs)
            lines.append(f'  G_{k} deg {deg(G)}: {s}  => log9 {tot}')
        res[n] = rec
        lines.append(f'  ({time.time() - t0:.1f}s)')
        print('\n'.join(lines[-22:]), flush=True)
    open('step1_factor.txt', 'w').write('\n'.join(lines) + '\n')
    json.dump(res, open('step1_factor.json', 'w'))
