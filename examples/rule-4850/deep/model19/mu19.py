"""Step 2: components of the eigenvalues on the 19-torus.  For each rule: the mu19 exponent s(a, b),
its F19-Fourier support, the 3-part v27, and the 19-torus polynomials of the value and its parts.
Baselines: random radius-4 rules.  Writes mu19.json."""
import json, random, sys
import numpy as np
import ff18 as F
import torus19 as T19

REL = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6}
rho = F.pw(F.zeta27(), 9)


def analyse(valfun, full=True):
    h = T19.torus_values(valfun)
    if not all(h.values()):
        return None
    sb = T19.s_function(h)
    sab = T19.s_full(sb)
    C = T19.fourier19(sab)
    v = {b: F.v27(h[b]) for b in h}
    res = dict(s_1b=sb, v27_1b=v, fourier_support=len(C),
               fourier=sorted([[i, l, c] for (i, l), c in C.items()]) if len(C) < 12 else None,
               linear_fit=[c for c in range(19) if all(sab[(a, b)] == c * (a + b) % 19 for (a, b) in sab)])
    if full:
        alpha = {b: F.pw(h[b], F.E511) for b in h}
        root = {b: F.mul(F.pw(h[b], F.E19), F.pw(h[b], F.E27)) for b in h}
        res['weight_value_poly'] = len(T19.poly_of(h))
        res['weight_alpha_poly'] = len(T19.poly_of(alpha))
        res['weight_rootpart_poly'] = len(T19.poly_of(root))
    return res


out = {'S_t1': F.nb19(F.t1())}
# check the transport: t_j = T(zeta19^phi(j))
Tm = F.nb19(F.t1())
for j in range(1, 37):
    zj = F.z19pows()[T19.phi(j)]
    val = 0
    for i in Tm:
        val ^= F.pw(zj, i)
    assert val == F.tvec()[j]
out['transport_check'] = 't_j = T(zeta19^phi(j)) for all j: ok'
for n, r in REL.items():
    out[n] = analyse(lambda j, k: F.rule_value(n, r, j, k))
    o = out[n]
    print(n, 'fourier support of s:', o['fourier_support'], 'linear fit', o['linear_fit'],
          'weights value/alpha/root:', o['weight_value_poly'], o['weight_alpha_poly'], o['weight_rootpart_poly'])
# ratios of the two unexplained rules to 10491524
for n in (20982139, 178279803):
    def ratio(j, k, n=n):
        return F.mul(F.rule_value(n, 6, j, k), F.inv(F.rule_value(10491524, 6, j, k)))
    o = analyse(ratio)
    out['ratio_%d' % n] = o
    print('ratio', n, '/10491524: v27', sorted(set(o['v27_1b'].values())), 'fourier support', o['fourier_support'],
          'linear', o['linear_fit'], 'weights', o['weight_value_poly'], o['weight_alpha_poly'], o['weight_rootpart_poly'])
    print('   s(1,b):', [o['s_1b'][b] for b in range(1, 19)])
# baseline
random.seed(1)
base = []
for trial in range(150):
    n = random.randrange(1, 1 << 15)
    o = analyse(lambda j, k: F.rule_value(n, 4, j, k))
    if o:
        base.append((n, o['fourier_support'], o['weight_value_poly'], o['weight_alpha_poly'], o['weight_rootpart_poly'], len(o['linear_fit'])))
B = np.array([b[1:] for b in base])
out['baseline'] = dict(n=len(base), fourier_support=np.bincount(B[:, 0]).tolist(),
                       weight_value_mean_sd=[float(B[:, 1].mean()), float(B[:, 1].std())], weight_value_min=int(B[:, 1].min()),
                       weight_alpha_mean_sd=[float(B[:, 2].mean()), float(B[:, 2].std())], weight_alpha_min=int(B[:, 2].min()),
                       weight_root_mean_sd=[float(B[:, 3].mean()), float(B[:, 3].std())], weight_root_min=int(B[:, 3].min()),
                       linear_fits=int(B[:, 4].sum()))
print('baseline', out['baseline'])
print('4850 s(1,b):', [out[4850]['s_1b'][b] for b in range(1, 19)])
print('4850 v27(1,b):', [out[4850]['v27_1b'][b] for b in range(1, 19)])
json.dump(out, open('mu19.json', 'w'), indent=1, default=str)
