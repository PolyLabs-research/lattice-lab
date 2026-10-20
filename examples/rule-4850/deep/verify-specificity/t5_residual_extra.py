"""t5: (a) across-size empirical null for W_m, with the forcing filter used in t3 (a Frobenius stabiliser counts
only if 9 | (2^d-1)/(2^gcd(k,d)-1); the trivial k = d/2 from -1 in <2> does not force anything);
(b) a quick independent check, in own F(2^36), of the closed form claimed by the concurrent norms/ analysis
(not one of the seven investigators): N_{K/F64}(W(al,be)) = (eta(al) eta(be))^n(d), d = ind2(be/al) mod 6,
n = {0:2, 1:-1, 2:-4, 3:2, 4:-4, 5:-1}, eta(x) = sum_{u in mu6} zeta^(u x), at every character with al*be != 0;
and the residual consequence: at d = 1 the norm (eta eta)^-1 lies in F8 (so W(1,2) is a ninth power)."""
import sys, json, math, time
import numpy as np
import sympy
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
from t3_soundness_lib import Size, t_sum_indices, factor_W, frob_stabiliser
T0 = time.time()
OUT = {}
cross = {}
for m in (13, 61, 97, 109, 241):
    Z = Size(m)
    F, t, d = Z.F, Z.t, Z.d
    w = Z.omega[0]
    Tm = [(1, 1), (w, pow(w, -1, m)), (w * w % m, pow(w * w, -1, m))]
    seen = set(); tot = nin = 0; cats = {}
    for al in range(1, m):
        for be in range(1, m):
            if (al, be) in seen:
                continue
            c = (al, be)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            v = 0
            for u in Z.mu3:
                v ^= F.mul(int(t[u * al % m]), int(t[be * pow(u, -1, m) % m]))
            if v == 0:
                continue
            ninth = F.pow(v, Z.N // 9) == 1
            fac = factor_W(t_sum_indices(al, be, m, Z.mu3), m)
            ks = [k for k in frob_stabiliser((al, be), m, d, Tm) if k % d]
            forced = [k for k in ks if (Z.N // (2 ** math.gcd(k, d) - 1)) % 9 == 0]
            cat = 'factorised' if fac else ('frobenius-forced' if forced else 'unforced')
            a = cats.setdefault(cat, [0, 0]); a[0] += 1; a[1] += ninth
            tot += 1; nin += ninth
    cross[m] = dict(d=d, W_orbits=tot, W_ninth=nin, by_category={k: dict(n=v[0], ninth=v[1], rate=v[1] / v[0]) for k, v in cats.items()})
    print('m=%d' % m, cross[m], flush=True)
OUT['cross_size_W'] = cross
un = [c['by_category'].get('unforced') for c in cross.values() if c['by_category'].get('unforced')]
OUT['pooled_unforced_ninth_rate'] = sum(u['ninth'] for u in un) / sum(u['n'] for u in un) if un else None
print('pooled ninth rate of unforced W classes at 13, 61, 97, 109, 241:', OUT['pooled_unforced_ninth_rate'], flush=True)
# (b) the norms closed form at 37
Z = Size(37); F = Z.F; t = Z.t; m = 37
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
zp = Z.E.zp
eta = [0] * m
for x in range(m):
    v = 0
    for u in mu6:
        v ^= int(zp[u * x % m])
    eta[x] = v
ind2 = {pow(2, i, m): i for i in range(36)}
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
NK = 2 ** 18 - 1
ok = 0; tot = 0; res_F8 = True
for al in range(1, m):
    for be in range(1, m):
        Wv = 0
        for u in Z.mu3:
            Wv ^= F.mul(int(t[u * al % m]), int(t[be * pow(u, -1, m) % m]))
        N = F.mul(F.mul(Wv, F.pow(Wv, 64)), F.pow(Wv, 4096))
        dd = (ind2[be] - ind2[al]) % 6
        base = F.mul(eta[al], eta[be])
        e = n[dd] % 63
        rhs = F.pow(base, e)
        tot += 1; ok += (N == rhs)
        if dd in (1, 5):
            res_F8 &= F.pow(N, 7) == 1
OUT['norms_closed_form'] = dict(checked=tot, holds=ok, residual_norm_in_F8=res_F8)
print('norms closed form N(W) = (eta eta)^n(d):', OUT['norms_closed_form'], flush=True)
OUT['time'] = round(time.time() - T0, 1)
json.dump(OUT, open('t5_residual_extra.json', 'w'), indent=1, default=str)
print('time', OUT['time'])
