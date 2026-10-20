"""Step 7. The closest analogues of 37 beyond step 3's range: primes m = 13 mod 24 with 2 a primitive root (so u, -1 in
<2>, symmetric values in F(2^((m-1)/2)), 9 | 2^((m-1)/2) - 1, and the twist classes are the Legendre classes).
Full family computation (all p) at the sizes given on the command line; levels as in step 3."""
import json, sys, time
from sizes_engine import Size
import famlib as L

out = []
for m in [int(x) for x in sys.argv[1:]]:
    t0 = time.time()
    S = Size(m)
    for r in S.roots:
        res = S.family(r)
        fam = res.pop('family')
        rec = dict(m=m, d=S.d, A=S.A, agen=S.agen, r=r, u=res['u'],
                   t_level=S.agen - res['t_exp'], pi_level=S.agen - res['pi_exp'],
                   W_level=None if res['W_exp'] is None else S.agen - res['W_exp'],
                   W_equals_pi_n=res['W_equals_pi^n_mod_3^i'],
                   best_member_level_off=max(S.agen - f['E_off'] for f in fam),
                   confined=[(f['p'], f['q'], S.agen - f['E_off']) for f in fam if S.agen - f['E_off'] >= 1],
                   members=len(fam), secs=round(time.time() - t0, 1))
        out.append(rec)
        print(rec, flush=True)
json.dump(out, open('step7_bigprimes_%s.json' % '_'.join(sys.argv[1:]), 'w'), indent=1)
