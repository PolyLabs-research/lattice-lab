"""v5 (claim 4): the residual as a norm condition and the Gauss-period identity.
Definitions (zeta = the class of z in F2[z]/Phi37):  mu6 = {1,10,11,26,27,36}, mu12 = <8> in F37*;
  eta_i   = sum_{u in mu6}  zeta^(2^i u),  i in Z/6   (index-6 Gauss periods, in F64 = F(2^6))
  theta_i = sum_{u in mu12} zeta^(2^i u) = eta_i + eta_{i+3},  i in Z/3   (index-3 Gauss periods, in F8)
  N = N_{K/F64}(z) = z^(1 + 64 + 64^2) = z^4161,  K = F(2^18).
(a) criterion: z in K* is a ninth power <=> N(z) in F8* -- exhaustively over K* = <g> by walking g^L;
(b) the residual: lambda_4850(1,3) = lambda'(1,2) = W(1,2)^4 / (t_1 t_2), t_1 t_2 a ninth power (chi(1)+chi(2) = 0),
    so ninth <=> W(1,2) ninth <=> N(W(1,2)) in F8;  also for the other two members (1,5), (1,13);
(c) N(W(1,2)) == theta_2 = eta_2 + eta_5:  (i) field: W W^64 W^4096;  (ii) exact in F2[Z/37]: prod_{c in mu3} W_x(1, 2c) as a
    1728-term product, compared with eta_2(x) + eta_5(x) (+ J allowed, J = sum of all x^n, which vanishes at zeta)."""
import json, time
import numpy as np
import vlib as V
M = V.M
t0 = time.time()
NK = V.NK
# a generator of K*
def kelem(c):
    return V.power(c, (1 << 18) + 1)
g = next(kelem(c) for c in range(2, 10000) if kelem(c) and all(V.power(kelem(c), NK // p) != 1 for p in (3, 7, 19, 73)))
Ng = V.power(g, 4161)
print('generator g of K* found; N(g) has order', next(o for o in (63,) if V.power(Ng, o) == 1 and all(V.power(Ng, o // p) != 1 for p in (3, 7))))
# (a) walk z = g^L, N(z) = N(g)^L
ok = True; z = 1; n = 1; cnt = 0
for L in range(NK):
    ninth = (L % 9 == 0)
    inF8 = V.power(n, 7) == 1           # F8* = mu7 inside F64*
    if ninth != inF8:
        ok = False; break
    if L % 9973 == 0:                    # spot-check the walk against direct arithmetic and against res()
        assert V.power(z, 4161) == n and (V.res(z) % 9 == 0) == ninth
        cnt += 1
    z = V.mul(z, g); n = V.mul(n, Ng)
assert z == 1
print('(a) for all 262143 z in K*: ninth power <=> N_{K/F64}(z) in F8*:', ok, '(spot checks vs direct arithmetic:', cnt, ')')
# definitions
def eta(i):
    v = 0
    for u in V.MU6:
        v ^= V.zeta(pow(2, i, M) * u)
    return v
def theta(i):
    v = 0
    for u in V.MU12:
        v ^= V.zeta(pow(2, i, M) * u)
    return v
E = [eta(i) for i in range(6)]; TH = [theta(i) for i in range(3)]
print('    eta_i in F64:', all(V.frob(e, 6) == e for e in E), '; theta_i in F8:', all(V.frob(x, 3) == x for x in TH),
      '; theta_i == eta_i + eta_{i+3}:', all(TH[i] == E[i] ^ E[i + 3] for i in range(3)), '; mu12 == mu6 u 8 mu6:', sorted(V.MU12) == sorted(set(V.MU6) | {8 * u % M for u in V.MU6}))
def W(a, b):
    v = 0
    for u in V.MU3:
        v ^= V.mul(V.t(u * a), V.t(b * pow(u, -1, M)))
    return v
lam4850 = V.eig_all(V.rule(4850, 4)); lam1 = V.eig_all(V.rule(10491524, 6))
# (b)
w12 = W(1, 2)
print('(b) lambda_4850(1,3) == lambda\'(1,2):', lam4850[(1, 3)] == lam1[(1, 2)],
      '; == W(1,2)^4/(t_1 t_2):', lam1[(1, 2)] == V.mul(V.power(w12, 4), V.inv(V.mul(V.t(1), V.t(2)))))
print('    chi(1), chi(2) =', V.legendre(1), V.legendre(2), '; t_1 t_2 ninth power:', V.res(V.mul(V.t(1), V.t(2))) % 9 == 0)
NW = V.power(w12, 4161)
for (j, k) in ((1, 3), (1, 5), (1, 13)):
    a, b = (j + k) * pow(2, -1, M) % M, (j - k) * pow(2, -1, M) % M
    w = W(a, b)
    n = V.power(w, 4161)
    print('    4850 class', (j, k), '-> T frame', (a, b), ': ninth(lambda) =', V.res(lam4850[(j, k)]) % 9 == 0,
          '; t_a t_b ninth:', V.res(V.mul(V.t(a), V.t(b))) % 9 == 0, '; N(W) in F8:', V.frob(n, 3) == n,
          '; equivalence holds:', (V.res(lam4850[(j, k)]) % 9 == 0) == (V.frob(n, 3) == n))
# (c)(i) field
prodc = 1
for c in V.MU3:
    prodc = V.mul(prodc, W(1, 2 * c))
print('(c) N(W(1,2)) = W W^64 W^4096 == prod_{c in mu3} W(1, 2c):', NW == prodc)
print('    N(W(1,2)) == theta_2 = eta_2 + eta_5:', NW == TH[2] == E[2] ^ E[5], '; == theta_0, theta_1:', NW == TH[0], NW == TH[1],
      '; N(W(1,2)) in F8:', V.frob(NW, 3) == NW)
# (c)(ii) exact group ring, 1728 terms
def Wx(a, b):
    return [(u * a + e * b * pow(u, -1, M)) % M for u in V.MU6 for e in (1, -1)]
cnt = np.zeros(M, dtype=np.int64)
L = [Wx(1, 2 * c % M) for c in V.MU3]
for n1 in L[0]:
    for n2 in L[1]:
        for n3 in L[2]:
            cnt[(n1 + n2 + n3) % M] += 1
P = (cnt % 2).astype(np.uint8)
P2 = V.g1mul(V.g1mul(V.g1(L[0]), V.g1(L[1])), V.g1(L[2]))
eta25 = V.g1([pow(2, 2, M) * u for u in V.MU6] + [pow(2, 5, M) * u for u in V.MU6])
J = np.ones(M, dtype=np.uint8)
print('    exact: prod_c W_x(1,2c) (1728 terms, count mod 2) == eta_2(x) + eta_5(x):', np.array_equal(P, eta25),
      '; == eta_2 + eta_5 + J:', np.array_equal(P, eta25 ^ J), '; agrees with g1mul product:', np.array_equal(P, P2), '; total count', int(cnt.sum()))
print('    support of the product:', sorted(int(n) for n in np.nonzero(P)[0]), ' 4 mu12 =', sorted(4 * u % M for u in V.MU12))
# the full norm-table for d = 0..5 (for context)
tab = []
for d in range(6):
    n = V.power(W(1, pow(2, d, M)), 4161)
    which = [nm for nm, v in [('theta%d' % i, TH[i]) for i in range(3)] + [('eta%d' % i, E[i]) for i in range(6)] if v == n]
    tab.append((d, V.frob(n, 3) == n, which))
print('    N(W(1,2^d)) for d = 0..5: (d, in F8, equals):', tab)
json.dump(dict(criterion=ok, NW_eq_theta2=NW == TH[2], exact_groupring=bool(np.array_equal(P, eta25)), table=tab), open('v5_claim4.json', 'w'), indent=1, default=str)
print('time', round(time.time() - t0, 1))
