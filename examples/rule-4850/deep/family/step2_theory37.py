"""Step 2. The reduction theorem for the hexagon family at m = 37, checked at every character.

Claim (a), proved in the report, checked here: for q = +-r p mod 37 (r = 16, r^2 = -3), with
c = (j, k), alpha = (j+k)/2, beta = (j-k)/2, u = (1+r)/2 = 27 = 2^6 (order 6),
   W(alpha, beta) = sum_{v in mu3} t_{v alpha} t_{beta/v},   t_n = zeta^n + zeta^-n,
the eigenvalue of f_{p,q} is
   W(2p alpha, 2p beta) / (t_alpha t_beta)             if alpha beta != 0,
   t_{pj} t_{qj} / t_j  (j = alpha or beta)            if alpha beta = 0, p != q mod 2,
   0                                                   if alpha beta = 0, p = q mod 2.
Checked against the polynomial f_{p,q} itself at all 1368 nonzero characters, for every -3-type pair
with p, q <= 20.  Then the 3-adic inputs:
   (T)  t_j^(N/9) = rho^chi(j)            (Fable's identity: t is a cube, its ninth-power class is Legendre)
   (C)  W / (t_alpha t_beta) is a ninth power at every character with alpha beta != 0, W != 0
and the consequences: log3 of every member at every class, compared with the formula
   L = 2^(k+1) v(W) - v(t_alpha) - v(t_beta)   (off-diagonal),   v(t_pj) + v(t_qj) - v(t_j)  (diagonal)."""
import json
import famlib as L

M = 37
F = L.GF(M)
N = 2 ** 18 - 1               # symmetric values lie in F(2^18); work with exponents of F(2^36) = F.N
Q = F.Q                       # 27 (A = 3 for 2^36 - 1)
assert F.A == 3
t = F.t
h = pow(2, -1, M)
r = 16
u = (1 + r) * h % M
assert pow(u, 6, M) == 1 and pow(u, 3, M) == M - 1 and u == 27 == pow(2, 6, M)
mu3 = [1, u * u % M, pow(u, 4, M)]


def W(al, be):
    v = 0
    for x in mu3:
        v ^= F.mul(t[x * al % M], t[be * pow(x, -1, M) % M])
    return v


def eig(f, j, k):
    v = 0
    for a, b in f:
        v ^= F.zp[(a * j + b * k) % M]
    return v


pairs = [(p, q) for p in range(1, 21) for q in range(1, 21) if (q * q + 3 * p * p) % M == 0]
bad = 0
checked = 0
for p, q in pairs:
    f = L.hex_rule(p, q)
    for j in range(M):
        for k in range(M):
            if (j, k) == (0, 0):
                continue
            al, be = (j + k) * h % M, (j - k) * h % M
            lam = eig(f, j, k)
            if al and be:
                pred = F.mul(W(2 * p * al % M, 2 * p * be % M), F.inv(F.mul(t[al], t[be])))
            else:
                jj = al or be
                pred = 0 if (p - q) % 2 == 0 else F.mul(F.mul(t[p * jj % M], t[q * jj % M]), F.inv(t[jj]))
            checked += 1
            if lam != pred:
                bad += 1
print('(a) reduction formula: %d -3-type pairs, %d characters checked, %d mismatches' % (len(pairs), checked, bad))

# (T) Legendre class of t, mod 9 (and its mod-27 digit for the record)
vt = {j: F.log3(t[j]) for j in range(1, M)}
T_ok = all(vt[j] % 3 == 0 for j in vt)
eps = (vt[1] // 3) % 3                       # rho^chi(j) normalisation: v(t_j) = 3 eps chi(j) mod 9
T9 = all((vt[j] - 3 * eps * L.legendre(j, M)) % 9 == 0 for j in vt)
print('(T) t_j cubes:', T_ok, '; v(t_j) = 3*eps*chi(j) mod 9 with eps = %d:' % eps, T9)
print('    v(t_1) mod 27 =', vt[1], '; v(t_j) = 2^ind(j) v(t_1) mod 27:',
      all(vt[pow(2, i, M)] == pow(2, i, 27) * vt[1] % 27 for i in range(36)))
# (C)
vW = {}
for al in range(1, M):
    for be in range(1, M):
        w = W(al, be)
        vW[(al, be)] = F.log3(w)
zeroW = sum(1 for v in vW.values() if v is None)
C9 = all(v is None or (v - vt[al] - vt[be]) % 9 == 0 for (al, be), v in vW.items())
Wcube = all(v is None or v % 3 == 0 for v in vW.values())
# 27-adic digit of W / pi
digit = {}
for (al, be), v in vW.items():
    if v is not None:
        digit[(al, be)] = ((v - vt[al] - vt[be]) % 27) // 9
print('(C) W zero at %d characters; W cube everywhere: %s; W = t_al t_be mod ninth powers everywhere: %s' % (zeroW, Wcube, C9))
from collections import Counter
print('    27-adic digit of W/(t_al t_be): distribution', Counter(digit.values()))
# is the third digit of W/pi a function of (chi(al), chi(be))?
by = {}
for (al, be), dg in digit.items():
    by.setdefault((L.legendre(al, M), L.legendre(be, M)), Counter())[dg] += 1
print('    digit by (chi(al), chi(be)):', {k: dict(v) for k, v in by.items()})
json.dump(dict(pairs=pairs, mismatches=bad, characters=checked, T_cube=T_ok, T_legendre_mod9=T9, eps=eps,
               vt1_mod27=vt[1], W_zero=zeroW, W_cube=Wcube, C_mod9=C9,
               digit27_counts=dict(Counter(digit.values()))), open('step2_theory37.json', 'w'), indent=1)
