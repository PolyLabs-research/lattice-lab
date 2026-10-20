"""Step 5. The cube-level analogue at m = 13 (r = 6, u = 10 = 2^10, 2 primitive, symmetric values in F(2^6), 63 = 9*7).
Prediction from step 3 + the reduction formula: f_{p,q} (q = +-6p mod 13) is cube-confined (odd part | 21) iff
p is a non-residue mod 13 and p = q mod 2 (diagonal class zero); every other member has odd part 63.
Checked here with eigen.odd_part on the polynomials, all p, q <= 20.  Also every other (p, q) <= 20 for comparison."""
import json
from collections import Counter
import famlib as L

M = 13
out = []
for p in range(1, 21):
    for q in range(1, 21):
        if p % M == 0 or q % M == 0:
            continue
        f = L.hex_rule(p, q)
        op = L.odd_part(f, M)
        m3 = (q * q + 3 * p * p) % M == 0
        rn = L.rule_number(f)
        pred = None
        if m3:
            pred = 21 if (L.legendre(p, M) == -1 and (p - q) % 2 == 0) else 63
        out.append(dict(p=p, q=q, minus3=m3, chi_p=L.legendre(p, M), same_parity=(p - q) % 2 == 0, terms=len(f),
                        radius=max(max(abs(a), abs(b)) for a, b in f), rule=rn[0] if rn else None,
                        odd_part=op, predicted=pred))
json.dump(out, open('step5_map13.json', 'w'), indent=1)
fam = [r for r in out if r['minus3']]
print('-3 type members p,q <= 20 at 13:', len(fam), '; prediction agrees:', sum(r['odd_part'] == r['predicted'] for r in fam))
for r in fam:
    print('  (%2d,%2d) chi_p=%+d same_parity=%d radius=%2d terms=%4d odd_part=%3d predicted=%3d %s' % (
        r['p'], r['q'], r['chi_p'], r['same_parity'], r['radius'], r['terms'], r['odd_part'], r['predicted'],
        ('rule %d' % r['rule']) if r['rule'] is not None and r['radius'] <= 8 else ''))
print('other pairs: odd parts', Counter(r['odd_part'] for r in out if not r['minus3']).most_common())
print('other pairs with odd part | 21:', [(r['p'], r['q'], r['odd_part']) for r in out if not r['minus3'] and 21 % r['odd_part'] == 0])
