"""Step 13: the norm N_{K/F64}(f0) in terms of Gauss periods.  K = F(2^18), F64 = fixed field of
sigma = Frob^6 (= dilation by 64 = -10 on indices).  eta_i = sum_{u in mu6} zeta^(2^i u) (index-6 periods, F64),
theta_i = eta_i + eta_{i+3} (index-3 periods, F8), rho_i = eta_i + eta_{i+2} + eta_{i+4} (index 2, F4).
N(W)(al, be) = prod_{c in mu3} W(al, c be) is a Galois-invariant sum of zeta powers, hence
c0 + sum_i c_i eta_i with c_i = (number of 1728 exponents in the coset 2^i mu6) mod 2: compute that
expansion exactly by counting, check it against field arithmetic, and tabulate N(f0)(0, d)."""
import json, itertools, collections
import numpy as np
import nf

m = 37
T = nf.tvec()
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
mu3 = [1, 10, 26]
lg2 = {pow(2, k, m): k for k in range(36)}
coset = {n: lg2[n] % 6 for n in range(1, m)}
eta = []
for i in range(6):
    v = 0
    for u in mu6:
        if u <= 18:
            pass
    # eta_i = sum over u in mu6 of zeta^(2^i u) = sum over u in mu3 of t_(2^i u)
    v = 0
    for u in mu3:
        v ^= T[pow(2, i, m) * u % m]
    eta.append(v)
g64 = nf.kpow(nf.gen(), 4161)
l64 = {}
xx = 1
for e in range(63):
    l64[xx] = e; xx = nf.kmul(xx, g64)
L = lambda z: l64.get(z, None) if z else None
theta = [eta[i] ^ eta[i + 3] for i in range(3)]
rho = [eta[0] ^ eta[2] ^ eta[4], eta[1] ^ eta[3] ^ eta[5]]
print('log eta_i:', [L(e) for e in eta], ' log theta_i:', [L(t) for t in theta], ' log rho:', [L(r) for r in rho])
print('theta in F8:', all(nf.kpow(t, 8) == t for t in theta), ' rho in F4:', all(nf.kpow(r, 4) == r for r in rho))
def Wexps(al, be):
    return [(u * al + e * be * pow(u, -1, m)) % m for u in mu6 for e in (1, -1)]
def NW_expansion(al, be):
    cnt = collections.Counter()
    lists = [Wexps(al, c * be % m) for c in mu3]
    for n1 in lists[0]:
        for n2 in lists[1]:
            for n3 in lists[2]:
                cnt[(n1 + n2 + n3) % m] += 1
    c0 = cnt[0] % 2
    ci = [0] * 6
    for n, k in cnt.items():
        if n:
            ci[coset[n]] += k
    # each coset has 6 elements: the counts must be equal within a coset (Galois invariance), check
    per = collections.defaultdict(set)
    for n in range(1, m):
        per[coset[n]].add(cnt[n] % 2)
    assert all(len(s) == 1 for s in per.values())
    ci = [per[i].pop() for i in range(6)]
    return c0, ci
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
    return v
rows = []
for d in range(6):
    al, be = 1, pow(2, d, m)
    c0, ci = NW_expansion(al, be)
    val = c0
    for i in range(6):
        if ci[i]:
            val ^= eta[i]
    nw = 1
    for c in mu3:
        nw = nf.kmul(nw, W(al, c * be % m))
    assert val == nw
    nf0 = nf.kmul(nw, nf.kinv(nf.kmul(nf.kmul(eta[0], eta[0]), nf.kmul(eta[d], eta[d]))))
    rows.append(dict(d=d, NW_expansion=[c0] + ci, logNW=L(nw), logNf0=L(nf0), Nf0_in_F8=nf.kpow(nf0, 8) == nf0))
    print('d=%d: N(W)(1, 2^d) = %d + sum %s . eta_i   log=%s ;  N(f0) log=%s in F8: %s' % (d, c0, ci, L(nw), L(nf0), nf.kpow(nf0, 8) == nf0))
# express N(f0)(0,d) as a word in theta's / eta's? search small monomials
cands = {}
names = ['eta%d' % i for i in range(6)] + ['theta%d' % i for i in range(3)]
elts = eta + theta
for exps in itertools.product(range(-2, 3), repeat=3):
    # monomials in theta only
    v = 1
    for t, e in zip(theta, exps):
        v = nf.kmul(v, nf.kpow(t, e % nf.NK))
    cands.setdefault(L(v), []).append(('theta', exps))
for r in rows:
    print('  d=%d  N(f0) log %s = theta-monomials:' % (r['d'], r['logNf0']), cands.get(r['logNf0'], [])[:4])
json.dump(dict(rows=rows, log_eta=[L(e) for e in eta], log_theta=[L(t) for t in theta]), open('step13_periods.json', 'w'), indent=1)
