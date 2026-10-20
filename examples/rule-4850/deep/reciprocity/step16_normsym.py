"""Step 16: the 'norm-symmetry group' of a rule: all M in GL2(Z/37) with
   N_{F(2^18)/F_64}(lambda(M^T c)) = N_{F(2^18)/F_64}(lambda(c))   for every character c,
(equivalently lambda(M^T c)/lambda(c) is a 63rd power everywhere).  It contains the true
symmetries (D4) and every 'twisted symmetry' f o M = f * (63rd powers), such as R3 for 4850.
Its orbits on the 11 classes show which ninth-power conditions are tied together.
Also: the 27-part version (lambda(M^T c)/lambda(c) a 27th power) and the plain ninth-power version
(vacuous for confined rules; reported for controls)."""
import sys, time
import numpy as np
from rlib import *
from fulllog import log_table

M = 37
LOG = log_table()

def char_values(Fset):
    """lambda at every character (j, k) in (Z/37)^2 (F(2^18) elements); index j*37 + k"""
    lines = {}
    for k in range(M):
        lines[k] = val_t1(Q_dickson(Fset, k)) if k else val_t1(subst_line(Fset, 0))
    axis = val_t1(subst_line(Fset, 0))
    vals = np.zeros(M * M, dtype=np.int64)
    for j in range(M):
        for k in range(M):
            if j == 0 and k == 0:
                v = 0 if len(Fset) % 2 == 0 else 1  # trivial character: parity (unused)
            elif j == 0:
                v = f18_pow(axis, 2 ** (pow(2, -1, M) and [e for e in range(36) if pow(2, e, M) == k][0]))
            else:
                kk = (k * pow(j, -1, M)) % M
                e = [e for e in range(36) if pow(2, e, M) == j][0]
                v = f18_pow(lines[kk], 2 ** e)
            vals[j * M + k] = v
    return vals

def group(Fset, modulus, label):
    vals = char_values(Fset)
    logs = np.where(vals == 0, -1, LOG[vals])
    nu = np.where(logs < 0, -1, logs % modulus)
    nu[0] = -2  # ignore trivial character
    js, ks = np.divmod(np.arange(M * M), M)
    # prefilter on 30 random characters
    rng = np.random.default_rng(1)
    test = rng.choice(np.arange(1, M * M), size=30, replace=False)
    a, b, c, d = [x.ravel() for x in np.meshgrid(*[np.arange(M)] * 4, indexing='ij')]
    det = (a * d - b * c) % M
    keep = det != 0
    a, b, c, d = a[keep], b[keep], c[keep], d[keep]
    ok = np.ones(len(a), dtype=bool)
    for t in test:
        j, k = js[t], ks[t]
        j2, k2 = (a * j + c * k) % M, (b * j + d * k) % M
        ok &= nu[j2 * M + k2] == nu[t]
    cand = np.flatnonzero(ok)
    full = []
    for i in cand:
        j2, k2 = (a[i] * js + c[i] * ks) % M, (b[i] * js + d[i] * ks) % M
        if np.array_equal(nu[1:], nu[(j2 * M + k2)[1:]]):
            full.append((int(a[i]), int(b[i]), int(c[i]), int(d[i])))
    print(f'{label}: |group| = {len(full)}')
    return full, nu

if __name__ == '__main__':
    t0 = time.time()
    for n, r in [(4850, 4), (10491524, 6), (20982139, 6)]:
        F = rule_F(n, r)
        for mod in (63, 27, 7):
            G, nu = group(F, mod, f'rule {n}, logs mod {mod}')
        print('   ', round(time.time() - t0), 's', flush=True)
    # controls: two random radius-4 rules, and two ninth-power-confined explained rules
    import random
    rng = random.Random(11)
    for n in [rng.randrange(1, 1 << 15) for _ in range(2)] + [7, 1057]:
        G, nu = group(rule_F(n, 4), 63, f'control rule {n} (radius 4), mod 63')
