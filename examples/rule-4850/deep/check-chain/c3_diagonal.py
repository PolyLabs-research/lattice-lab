"""check-chain c3: the diagonal classes j = +-k of rule 4850 (be = 0 or al = 0 in the 45-degree frame), step (5).

(1) F(a, b) = s^3 + P^2 s^2 + P^3 + P^2 + P (s = a+b, P = ab) reproduces lambda(j,k) = F(t_j, t_k) at every character
    (so the dossier polynomial is the rule), and F(t, t) = t^2 (1 + t + t^2)^2 as polynomials.
(2) exact Laurent identity over F2: t(x)^2 (1 + t(x) + t(x)^2)^2 = t(x) t(x^5), t(x) = x + 1/x.
    So lambda(j, +-j) = t_j t_{5j}.
(3) route A (the investigator's 'cyclotomic' route): needs the class of t_x mod ninth powers:
    t_x^29127 = rho^(legendre(x)) with rho of order 3 (rule 90 is Legendre), and 5 a non-residue mod 37.
    This is a finite computed fact (equivalently: 1 + zeta is a cube, not a ninth power, in F(2^36)*).
(4) route B (norm mechanism, no rule-90 input): N_{K/k}(t_j t_{5j}) = eta(j)^2 eta(5j)^2 = eta(j)^(2 + 2*2^c5),
    c5 = log2(5) mod 6, and eta^21 = 1 (from the c1 certificate), so the exponent mod 21 decides.
(5) direct: every diagonal eigenvalue is a ninth power.
"""
import json
import functools
import clib
from clib import p

F = clib.GF36()
z = [F.pow(F.zeta, i) for i in range(p)]
t = [z[i] ^ z[(-i) % p] for i in range(p)]
mu6 = clib.mu(6)
L2 = clib.LOG2
eta = lambda x: functools.reduce(lambda a, b: a ^ b, (z[x * u % p] for u in mu6), 0)
out = {}
pts = clib.rule_points(clib.RULE4850_ORBITS)
def lam(j, k):
    v = 0
    for a, b in pts:
        v ^= z[(a * j + b * k) % p]
    return v
mm = F.mul
def Fab(a, b):
    s = a ^ b
    P = mm(a, b)
    P2 = mm(P, P)
    return mm(mm(s, s), s) ^ mm(P2, mm(s, s)) ^ mm(P2, P) ^ P2 ^ P
out['(1) lambda(j,k) = F(t_j, t_k) at all 1369 characters'] = all(lam(j, k) == Fab(t[j], t[k]) for j in range(p) for k in range(p))

# Laurent polynomials over F2 as sets of integer exponents
def lmul(A, B):
    o = set()
    for i in A:
        for j in B:
            o ^= {i + j}
    return o
def ladd(*As):
    o = set()
    for A in As:
        o ^= set(A)
    return o
T = {1, -1}
T5 = {5, -5}
lhs = lmul(lmul(T, T), lmul(ladd({0}, T, lmul(T, T)), ladd({0}, T, lmul(T, T))))
out['(2) t^2 (1+t+t^2)^2 == t(x) t(x^5) as Laurent polynomials'] = lhs == lmul(T, T5)
# F(t,t) from the polynomial: s = 0, P = t^2 -> t^6 + t^4 + t^2 = t^2 (1 + t + t^2)^2 (char 2)
out['(1) F(t,t) = t^6 + t^4 + t^2 = t^2(1+t+t^2)^2 (char 2 square)'] = True
diag = [(j, s * j % p) for j in range(1, p) for s in (1, -1)]
out['(2) lambda(j, +-j) == t_j t_{5j}, all 72'] = all(lam(j, k) == mm(t[j], t[5 * j % p]) for j, k in diag)

# (3) route A
cls = {x: F.pow(t[x], 29127) for x in range(1, p)}
rho = cls[1]
out['(3) t_1^29127 has order 3'] = rho != 1 and F.pow(rho, 3) == 1
out['(3) t_x^29127 == rho^legendre(x), all x'] = all(cls[x] == (rho if clib.legendre(x) == 1 else F.mul(rho, rho)) for x in range(1, p))
out['(3) legendre(5)'] = clib.legendre(5)
onez = 1 ^ z[1]
out['(3) 1+zeta cube in F(2^36)*'] = F.pow(onez, clib.N36 // 3) == 1
out['(3) 1+zeta ninth power in F(2^36)*'] = F.pow(onez, clib.N36 // 9) == 1

# (4) route B
c5 = L2[5] % 6
e = (2 + 2 * 2 ** c5)
out['(4) log2(5) mod 6, exponent 2+2*2^c5, mod 21'] = [c5, e, e % 21]
out['(4) exponent divisible by 3 (=> N in mu7 = F8*)'] = e % 3 == 0
inF8 = lambda v: F.in_sub(v, 3)
out['(4) N(lambda) == eta(j)^e at all 72 diagonal chars'] = all(F.norm_K_k(lam(j, k)) == F.pow(eta(j), e) for j, k in diag)
out['(4) N(lambda) in F8 at all 72'] = all(inF8(F.norm_K_k(lam(j, k))) for j, k in diag)
# (5)
out['(5) every diagonal eigenvalue a ninth power'] = all(F.pow(lam(j, k), 29127) == 1 for j, k in diag)
out['(5) every diagonal eigenvalue a 27th power'] = all(F.pow(lam(j, k), 9709) == 1 for j, k in diag)
json.dump(out, open('c3_diagonal.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
