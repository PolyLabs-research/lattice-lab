"""v4 (claim 3): class bookkeeping for 4850 with the hidden symmetry.
Frames: 4850 at (j,k); T frame (10491524) at (a,b) = ((j+k)/2, (j-k)/2).  Off the T-axes (j = +-k in 4850's frame)
lambda'(a,b) = W(a,b)^4 / (t_a t_b) (v1).  Proven T-invariance of R' (mu27) off the T-axes needs only W(Tc) = W(c) and
t cube: R(t_{10a}) = 2^24 R(t_a) = 10 R(t_a) = R(t_a) (R(t) = 0 mod 3).
(1) merge the 11 census classes under <D4, 2I, M0> acting off the diagonals (M0 = Rot^-1 T Rot);
(2) the exact group-ring Legendre law t(x)^29127 = sum_{u nonres} x^u in F2[Z/37] (and rho = that at zeta is a cube root of 1);
(3) per class: T-frame type d, and the explanation:
    axis (0,1): F(0,t) = t^3;  diagonal (1,1): F(t,t) = t^2 (1+t+t^2)^2 with cyclotomic exponents in F(2^36);
    d = 0: W = t_x^2 exactly in F2[Z/37];  d = +-2: W = t_x t_y t_z exactly (two of six terms cancel);
    d = 3: an explicit element of <D4, 2I, T> fixing the character with Frobenius multiplier 2^k, gcd(2^k - 1, 27) = 1;
    d = +-1: none of these shapes;  then the Legendre bookkeeping and a direct field check."""
import json, itertools, time
import numpy as np
import vlib as V
M = V.M
t0 = time.time()
chi = V.legendre
REPS = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
D4M = [((1, 0), (0, 1)), ((M - 1, 0), (0, 1)), ((1, 0), (0, M - 1)), ((M - 1, 0), (0, M - 1)),
       ((0, 1), (1, 0)), ((0, M - 1), (1, 0)), ((0, 1), (M - 1, 0)), ((0, M - 1), (M - 1, 0))]
def mm(A, B):
    return tuple(tuple(sum(A[i][s] * B[s][j] for s in range(2)) % M for j in range(2)) for i in range(2))
def act(A, c):
    return ((A[0][0] * c[0] + A[0][1] * c[1]) % M, (A[1][0] * c[0] + A[1][1] * c[1]) % M)
i2 = pow(2, -1, M)
ROT = ((1, 1), (1, M - 1)); ROTI = ((i2, i2), (i2, M - i2))
T = ((10, 0), (0, 26)); M0 = mm(ROTI, mm(T, ROT))
cls_of = {}
for ci, (a, b) in enumerate(REPS):
    for g in D4M:
        x, y = act(g, (a, b))
        for i in range(36):
            u = pow(2, i, M)
            cls_of.setdefault((u * x % M, u * y % M), ci)
# (1) merging by M0 (only off 4850's diagonals, where the identity is informative)
parent = list(range(11))
def find(x):
    while parent[x] != x:
        x = parent[x]
    return x
for c, ci in cls_of.items():
    j, k = c
    if (j + k) % M == 0 or (j - k) % M == 0:
        continue
    cj = cls_of[act(M0, c)]
    a, b = find(ci), find(cj)
    if a != b: parent[a] = b
groups = {}
for ci in range(11):
    groups.setdefault(find(ci), []).append(REPS[ci])
print('(1) census classes merged by M0 (4850 frame):', sorted(groups.values()))
# (2) Legendre law, exact in F2[Z/37]
tx = V.g1([1, -1])
lhs = V.g1pow(tx, 29127)
nonres = [u for u in range(1, M) if chi(u) == -1]
print('(2) t(x)^29127 == sum_{u nonres} x^u in F2[Z/37]:', np.array_equal(lhs, V.g1(nonres)))
rho = V.g1eval(V.g1(nonres))
print('    rho = sum_{nonres} zeta^u: rho^2 + rho + 1 = 0:', V.mul(rho, rho) ^ rho ^ 1 == 0,
      '; t_j^29127 = rho^chi(j) for all j != 0:', all(V.power(V.t(j), 29127) == V.power(rho, chi(j) % 3) for j in range(1, M)))
print('    (1 + t(x))^29127 == 1:', np.array_equal(V.g1pow(V.g1([0, 1, -1]), 29127), V.g1([0])))
# helpers
def Wx(a, b):
    """W(a, b) as an element of F2[Z/37] (variable x = zeta): sum_{u in mu6, e} x^(u a + e b / u)."""
    return V.g1([u * a + e * b * pow(u, -1, M) for u in V.MU6 for e in (1, -1)])
def tprod(idx):
    v = V.g1([0])
    for j in idx:
        v = V.g1mul(v, V.g1([j, -j]))
    return v
def find_tproduct(w, rmax=3):
    for r in range(1, rmax + 1):
        for combo in itertools.combinations_with_replacement(range(1, 19), r):
            if np.array_equal(tprod(combo), w):
                return combo
    return None
lam4850 = V.eig_all(V.rule(4850, 4))
lam1 = V.eig_all(V.rule(10491524, 6))
res_all = {c: V.res(v) for c, v in lam4850.items() if c != (0, 0)}
def dtype(a, b):
    if a % M == 0 or b % M == 0:
        return 'axis'
    d = (V.IND[b % M] - V.IND[a % M]) % 6
    return {0: 'd=0', 3: 'd=3', 1: 'd=+-1', 5: 'd=+-1', 2: 'd=+-2', 4: 'd=+-2'}[d]
# group <D4, 2I (mult 2), T (mult 1)> in the T frame, with Frobenius exponent k mod 18
def closure():
    I = ((1, 0), (0, 1))
    gens = [(g, 0) for g in D4M] + [(((2, 0), (0, 2)), 1), (T, 0)]
    seen = {(I, 0)}; fr = [(I, 0)]
    while fr:
        nx = []
        for g, k in fr:
            for h, kh in gens:
                e = (mm(h, g), (k + kh) % 18)
                if e not in seen:
                    seen.add(e); nx.append(e)
        fr = nx
    return seen
GT = closure()
print('    |<D4, 2I, T>| with multipliers =', len(GT))
rows = []
for (j, k) in REPS:
    a, b = (j + k) * i2 % M, (j - k) * i2 % M
    typ = dtype(a, b)
    R = res_all[(j, k)]
    row = dict(cls=(j, k), T_frame=(a, b), type=typ, R=R, ninth=R % 9 == 0)
    assert lam4850[(j, k)] == lam1[(a, b)]
    if typ != 'axis':
        w = Wx(a, b)
        nterms = int(w.sum())
        row['W_terms'] = nterms
        prod = find_tproduct(w, 3)
        row['W_as_t_product'] = prod
        if prod is not None:
            s = sum(chi(x) for x in prod) * (2 if len(prod) == 1 and False else 1)
        # explanations
        if typ == 'd=0':
            sq = next((x for x in range(1, 19) if np.array_equal(w, V.g1dil(V.g1([x, -x]), 2))), None)
            row['W_eq_t_sq'] = sq
            # lambda' = t_x^8 / (t_a t_b): ninth iff 8 chi(x) - chi(a) - chi(b) = 0 mod 3
            row['legendre_exponent_mod3'] = (8 * chi(sq) - chi(a) - chi(b)) % 3
        if typ == 'd=+-2':
            row['legendre_exponent_mod3'] = (4 * sum(chi(x) for x in prod) - chi(a) - chi(b)) % 3
            row['two_of_six_cancel'] = nterms == 8   # six t-terms = 12 monomials; two cancelled t-terms leave 8 monomials
        if typ == 'd=3':
            st = [(g, kk) for g, kk in GT if act(g, (a, b)) == (a, b) and kk % 2 == 1]
            row['fixing_elements_with_odd_k'] = len(st)
            g, kk = st[0]
            row['example_fixer'] = (g, kk, 'forces (2^%d - 1) R = 0 mod 27, gcd = %d' % (kk, np.gcd(2 ** kk - 1, 27)))
        if typ == 'd=+-1':
            fixers = [(g, kk) for g, kk in GT if act(g, (a, b)) == (a, b) and kk != 0]
            row['nontrivial_fixers'] = len(fixers)
    rows.append(row)
for r in rows:
    print('   ', r)
# (3) the axis and the diagonal
t1 = V.t(1)
print('(3) axis (0,1): lambda = t_1^3:', lam4850[(0, 1)] == V.power(t1, 3), '; t_1 cube, not ninth:', V.res(t1) % 3 == 0, V.res(t1) % 9 != 0)
diag = V.mul(V.power(t1, 2), V.power(1 ^ t1 ^ V.mul(t1, t1), 2))
z1 = 1 ^ V.ZETA[1]
z5 = 1 ^ V.ZETA[5]
cube_z1 = V.power(z1, V.NE // 3) == 1; ninth_z1 = V.power(z1, V.NE // 9) == 1
print('    diagonal (1,1): lambda = t^2 (1+t+t^2)^2 at t = t_1:', lam4850[(1, 1)] == diag)
print('    t_1 = zeta^-1 (1+zeta)^2:', t1 == V.mul(V.inv(V.ZETA[1]), V.mul(z1, z1)),
      '; 1+t+t^2 = zeta^-2 (1+zeta^5)/(1+zeta):', (1 ^ t1 ^ V.mul(t1, t1)) == V.mul(V.inv(V.ZETA[2]), V.mul(z5, V.inv(z1))),
      '; 1+zeta^5 = (1+zeta)^(2^23):', z5 == V.frob(z1, 23), '(5 = 2^23 mod 37:', pow(2, 23, M) == 5, ')')
print('    1+zeta in F(2^36)*: cube', cube_z1, ', ninth', ninth_z1, '; lambda(1,1) = zeta^-6 (1+zeta)^(2^24 + 2), (2^24+2) mod 3 =', (2 ** 24 + 2) % 3,
      '-> ninth power; check:', lam4850[(1, 1)] == V.mul(V.inv(V.ZETA[6]), V.power(z1, 2 ** 24 + 2)), ' R =', res_all[(1, 1)])
# (4) (1,6): lies in F(2^9)
print('(4) (1,6): lambda^(2^9) == lambda:', V.frob(lam4850[(1, 6)], 9) == lam4850[(1, 6)], '; 2^9 (1,6) =', ((2 ** 9) % M, (2 ** 9 * 6) % M))
# (5) the residual: summary
expl = {'axis': 'F(0,t)=t^3', 'd=0': 'W=t^2', 'd=+-2': 'W=t t t + Legendre', 'd=3': 'forced by T-symmetry'}
print('(5) per 4850 class (type in T frame / ninth / explanation):')
for r in rows:
    e = 'diagonal: cyclotomic exponents' if r['cls'] == (1, 1) else ('Gamma0: F(2^9)-valued' if r['cls'] == (1, 6) else expl.get(r['type'], 'NONE'))
    print('     ', r['cls'], r['type'], r['ninth'], e)
json.dump(dict(groups=sorted(groups.values()), rows=rows), open('v4_claim3.json', 'w'), indent=1, default=str)
print('time', round(time.time() - t0, 1))
