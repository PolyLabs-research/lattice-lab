"""Step 3: each class condition as residue symbols at small-degree factors over F_64.

For a rule and a class (1, k), with G_k(T) = F(T, D_k(T)) (k the census representative):
  (G_k / pi_0)_9 = (pi_0 / G_k)_9 = prod_R (pi_0 / R)_9^{e_R}     (reciprocity; all monic)
over the monic irreducible factors R of G_k over F_64.  Symbols are written as the exponent
j in Z/9 with symbol = w^(7j) (w the generator of F_64).  The class is a ninth power iff the sum is 0.
Also printed: the reduced form r = G_k mod pi_0 over F_64 (degree <= 2), whose roots lie in
F_64 or F_4096, and its own reciprocity evaluation:
  (r/pi_0)_9 = lc(r)^(7*3) * prod_{roots c} pi_0(c)^((64^deg(c) - 1)/9).
Output: step3_symbols.txt, step3_symbols.json."""
import json, math, sys
from rlib import *

KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
P0 = pis()[0]

def fac_symbols(Q):
    """list of dicts per GF(2)-irreducible factor P^e: its F_64-factors' degrees and symbols"""
    out = []
    total = 1
    for p, e in factor2(Q):
        parts = []
        for R in split_over_64(p):
            s = symbol9(P0, R)
            parts.append((q_deg(R), mu9_index(s)))
            total = m64(total, pow64(s, e))
        out.append({'deg': deg(p), 'mult': e, 'parts': parts,
                    'sym': sum(j for _, j in parts) % 9})
    return out, mu9_index(total)

def reduced_form(Q):
    r = q_mod(q_from2(Q), P0)
    lc, facs = factor64(r) if q_deg(r) > 0 else (r[0], [])
    s = pow64(lc, 21)
    roots = []
    for R, e in facs:
        R = list(R)
        sR = symbol9(P0, R)   # = (pi_0 / R)_9 = pi_0(c)^7 for linear R
        s = m64(s, pow64(sR, e))
        roots.append({'deg': q_deg(R), 'R': R, 'mult': e, 'sym': mu9_index(sR)})
    return {'r': r, 'lc_sym': mu9_index(pow64(lc, 21)), 'roots': roots, 'total': mu9_index(s)}

def analyse(n, r, verbose=True):
    F = rule_F(n, r)
    res = {}
    lines = [f'=== rule {n} (radius {r})']
    for k in KS:
        G = Q_dickson(F, k)
        facs, tot = fac_symbols(G)
        direct = to64_from18(f18_pow(val_t1(G), NINTH)) if val_t1(G) else 0
        assert direct == 0 or mu9_index(direct) == tot
        red = reduced_form(G)
        assert red['total'] == tot
        res[k] = {'factors': facs, 'total': tot, 'reduced': red}
        fs = ' '.join(f"{f['deg']}{'^%d' % f['mult'] if f['mult'] > 1 else ''}<" +
                      ','.join(f'{d}:{j}' for d, j in f['parts']) + '>' for f in facs)
        rs = f"lc:{red['lc_sym']} " + ' '.join(f"root(deg{x['deg']}{'^%d' % x['mult'] if x['mult'] > 1 else ''}):{x['sym']}" for x in red['roots'])
        lines.append(f'  k={k:2d} total {tot} | factors over F_64 (deg:symbol): {fs}')
        lines.append(f'         reduced mod pi_0: r = {red["r"]} -> {rs}')
    if verbose:
        print('\n'.join(lines), flush=True)
    return res, lines

if __name__ == '__main__':
    RULES = [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)]
    allres, alllines = {}, []
    for n, r in RULES:
        res, lines = analyse(n, r)
        allres[n] = res
        alllines += lines
    open('step3_symbols.txt', 'w').write('\n'.join(alllines) + '\n')
    json.dump(allres, open('step3_symbols.json', 'w'))
