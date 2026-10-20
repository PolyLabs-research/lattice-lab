"""Step 3. Other sizes: every odd m <= MMAX with r^2 = -3 (mod m) solvable (prime factors = 1 mod 3, at most one 3),
v3(2^d - 1) >= 1.  For each square root r (up to sign) and each p, the hexagon-family member's 3-adic confinement
level (sizes_engine.Size.family).  Output step3_sizes.json; the log lists every (m, r) with any member confined
beyond the generic 3-exponent (level >= 1) off the diagonal."""
import json, sys, time, math
import sympy
from sizes_engine import Size

MMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PRIME_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 400
ms = []
for m in range(7, max(MMAX, PRIME_MAX) + 1, 2):
    fac = sympy.factorint(m)
    if any(p % 3 != 1 and p != 3 for p in fac) or fac.get(3, 0) > 1:
        continue
    if m == 3:
        continue
    if not sympy.isprime(m) and m > MMAX:
        continue
    ms.append(m)
out = []
for m in ms:
    t0 = time.time()
    S = Size(m)
    rec = dict(m=m, factors={int(k): int(v) for k, v in sympy.factorint(m).items()}, d=S.d, A=S.A,
               minus1_in_2=S.minus1_in_2, index_of_2=S.index2, roots=S.roots)
    if not S.A:
        rec['note'] = 'no 3-torsion in F(2^d)*: nothing to confine'
        out.append(rec); print(rec, flush=True); continue
    rec['agen'] = S.agen
    if S.agen == 0:
        rec['note'] = 'symmetric values in fields with no 3-torsion: trivially confined'
        out.append(rec); print(rec, flush=True); continue
    rec['per_root'] = []
    for r in S.roots:
        res = S.family(r)
        fam = res.pop('family')
        lev_off = [S.agen - f['E_off'] for f in fam]
        lev_both = [S.agen - max(f['E_off'], f['E_diag_opp']) for f in fam]
        res.update(r=r, members=len(fam), best_level_off=max(lev_off), best_level_with_diag=max(lev_both),
                   confined_off=[(f['p'], f['q'], S.agen - f['E_off']) for f in fam if S.agen - f['E_off'] >= 1],
                   t_level=S.agen - res['t_exp'], pi_level=S.agen - res['pi_exp'],
                   W_level=None if res['W_exp'] is None else S.agen - res['W_exp'])
        rec['per_root'].append(res)
    rec['secs'] = round(time.time() - t0, 1)
    out.append(rec)
    short = {k: v for k, v in rec.items() if k != 'per_root'}
    print(short, flush=True)
    for res in rec['per_root']:
        print('    r=%d u=%d  levels: t %d, pi %d, W %s, W=pi^n mod 3^i: %s;  best member level off-diag %d (with diag %d); confined members (p,q,level): %s' % (
            res['r'], res['u'], res['t_level'], res['pi_level'], res['W_level'], res['W_equals_pi^n_mod_3^i'],
            res['best_level_off'], res['best_level_with_diag'], res['confined_off'][:12]), flush=True)
json.dump(out, open('step3_sizes.json', 'w'), indent=1)
