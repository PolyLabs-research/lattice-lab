"""check-algebra a3: step (2) at m = 37, from scratch.

 (a) w = 10 = -2^6 (sigma = Frob^6 acts on t-indices by w); own log2 table mod 37; cosets (log2 mod 6) of
     1-w, 2-w, 2-w^2 (and of 1-w^2, 2-w^2, 2-w for the other generator).
 (b) the product rule applied to eta(x) eta((1-w)x): list the six arguments x(1 + (1-w)v), v in mu6, their
     cosets, and whether eta(0) enters.  => X^17 = X^8 + X^32, X = eta(2^i).
 (c) X^17 + X^8 + X^32 = X^8 (X^24 + X^9 + 1) as polynomials; gcd(x^24+x^9+1, x^63+1) over F2 (own Euclid, and
     sympy); factorisation x^9+x^3+1 = (x^3+x^2+1)(x^6+x^5+x^4+x^2+1) (product check); irreducibility of both
     factors (Rabin, and gcd with x^4+x, x^8+x); sextic | x^21+1.
 (d) eta_0 in the verifier's field (F2[x]/Phi_37, zeta = x): eta_0 in F64, not in F8, not in F4, nonzero,
     root of the sextic not the cubic, order 21; satisfies x^24 + x^9 + 1.
     Own argument for eta_0 not in F8: zeta^1..zeta^36 are F2-independent (rank 36 computed), the six periods
     are sums over disjoint index sets, so eta_0 != eta(8) = Frob^3(eta_0) and eta_0 != eta(4) = Frob^2(eta_0).
 (e) F64 = F2[eta_0] enumerated (64 elements as F2-combinations of 1..eta_0^5): solutions of X^17 = X^8 + X^32.
 (f) (outside lens, quick) (*) reduced mod the sextic equals (XY)^n(d), n = (2,-1,-4,2,-4,-1), and the field
     norm equals (eta(al) eta(be))^n(d) at all 1296 characters.
"""
import json
import sympy as sp
from flib import Field, pmod, pgcd, clmul, rabin_irreducible

p = 37
out = {}
F = Field(p)
assert F.d == 36 and F.nfactors == 1
m = F.mul
lg, x = {}, 1
for k in range(36):
    lg[x] = k
    x = 2 * x % p
assert len(lg) == 36
w = (-pow(2, 6, p)) % p
out['w'] = w
assert w == 10 and pow(w, 3, p) == 1
w2 = w * w % p
cos = lambda z: lg[z % p] % 6
mults = {'1-w': (1 - w) % p, '2-w': (2 - w) % p, '2-w^2': (2 - w2) % p,
         '1-w^2': (1 - w2) % p, '2-(w^2)': (2 - w2) % p, '2-(w^2)^2=2-w': (2 - w) % p}
out['multipliers_mod_37'] = mults
out['cosets_(1-w,2-w,2-w^2)'] = (cos(1 - w), cos(2 - w), cos(2 - w2))
out['cosets_other_generator_(1-w^2,2-w^2,2-w)'] = (cos(1 - w2), cos(2 - w2), cos(2 - w))
print('w =', w, ' 1-w, 2-w, 2-w^2 =', (1 - w) % p, (2 - w) % p, (2 - w2) % p, '= -9, -8, -24:',
      ((1 - w) % p, (2 - w) % p, (2 - w2) % p) == ((-9) % p, (-8) % p, (-24) % p))
print('cosets (log2 mod 6):', out['cosets_(1-w,2-w,2-w^2)'], '  with w^2 as generator:',
      out['cosets_other_generator_(1-w^2,2-w^2,2-w)'])
# (b)
mu6 = F.mu(6)
args = []
for v in mu6:
    z = (1 + (1 - w) * v) % p
    args.append(dict(v=v, arg=z, coset=None if z == 0 else cos(z)))
out['product_rule_args_eta(x)eta((1-w)x)'] = args
print('eta(x) eta((1-w)x) = sum_v eta(x(1+(1-w)v)); arguments and cosets:', [(a['arg'], a['coset']) for a in args])
print('   eta(0) edge case enters the aux identity:', any(a['arg'] == 0 for a in args))
# cosets 0,0 cancel (eta(x) twice), 1,1 cancel (eta(2x) twice), leaving cosets 3 and 5
from collections import Counter
cnt = Counter(a['coset'] for a in args)
left = sorted(c for c, n in cnt.items() if n % 2)
print('   surviving cosets mod 2:', left, ' => X * X^16 = X^(2^3) + X^(2^5) = X^8 + X^32')
out['aux_surviving_cosets'] = left
# (c)
X = sp.symbols('x')
lhs = sp.Poly(X ** 17 + X ** 8 + X ** 32, X, modulus=2)
fac = sp.Poly(X ** 8 * (X ** 24 + X ** 9 + 1), X, modulus=2)
print('X^17 + X^8 + X^32 == X^8 (X^24 + X^9 + 1):', lhs == fac)
mono = lambda e: 1 << e
f24 = mono(24) ^ mono(9) ^ 1
g_own = pgcd(mono(63) ^ 1, f24)
g_sp = sp.gcd(sp.Poly(X ** 24 + X ** 9 + 1, X, modulus=2), sp.Poly(X ** 63 + 1, X, modulus=2))
cubic, sext = 0b1101, 0b1110101
print('gcd(x^24+x^9+1, x^63+1): own =', bin(g_own), ' sympy =', g_sp.as_expr(), ' == x^9+x^3+1:',
      g_own == (mono(9) ^ mono(3) ^ 1))
prod = clmul(cubic, sext)
print('(x^3+x^2+1)(x^6+x^5+x^4+x^2+1) == x^9+x^3+1:', prod == (mono(9) ^ mono(3) ^ 1))
print('sympy factor_list(x^9+x^3+1):', sp.Poly(X ** 9 + X ** 3 + 1, X, modulus=2).factor_list())
irr = dict(cubic_rabin=rabin_irreducible(cubic), sextic_rabin=rabin_irreducible(sext),
           sextic_gcd_x4_x=pgcd(mono(4) ^ 2, sext), sextic_gcd_x8_x=pgcd(mono(8) ^ 2, sext))
print('irreducibility:', irr)
div21 = pmod(mono(21) ^ 1, sext) == 0
div7 = pmod(mono(7) ^ 1, sext) == 0
print('sextic | x^21 + 1:', div21, '  sextic | x^7 + 1:', div7, ' (roots of order exactly 21 if not | x^7+1, x^3+1)')
print('squarefree x^24+x^9+1 (gcd with derivative x^8):', pgcd(f24, mono(8)) == 1)
out.update(gcd=bin(g_own), gcd_is_x9_x3_1=g_own == (mono(9) ^ mono(3) ^ 1),
           factorisation_ok=prod == (mono(9) ^ mono(3) ^ 1), irreducible=dict((k, int(v) if not isinstance(v, bool) else v) for k, v in irr.items()),
           sextic_divides_x21_1=div21, sextic_divides_x7_1=div7)
# (d)
eta = [F.eta(j, mu6) for j in range(p)]
e0 = eta[1]
rank = 0
basis = {}
for j in range(1, 37):
    v = F.z(j)
    while v:
        hb = v.bit_length() - 1
        if hb in basis:
            v ^= basis[hb]
        else:
            basis[hb] = v
            rank += 1
            break
periods = [eta[pow(2, i, p)] for i in range(6)]
supports = [sorted(u * pow(2, i, p) % p for u in mu6) for i in range(6)]
disjoint = len(set(sum(supports, []))) == 36


def sum_poly(poly, z):
    acc, zp = 0, 1
    for i in range(poly.bit_length()):
        if poly >> i & 1:
            acc ^= zp
        zp = m(zp, z)
    return acc


order = next(n for n in range(1, 64) if F.pow(e0, n) == 1) if F.pow(e0, 63) == 1 else None
dd = dict(rank_zeta1_to_zeta36=rank, period_supports_disjoint_cover=disjoint,
          periods_distinct_nonzero=len(set(periods)) == 6 and 0 not in periods,
          eta0_nonzero=e0 != 0, eta0_in_F64=F.frob(e0, 6) == e0, eta0_in_F8=F.frob(e0, 3) == e0,
          eta0_in_F4=F.frob(e0, 2) == e0, Frob3_eta0_is_eta8=F.frob(e0, 3) == eta[8],
          sextic_at_eta0=sum_poly(sext, e0), cubic_at_eta0_nonzero=sum_poly(cubic, e0) != 0,
          eta0_x24_x9_1=sum_poly(f24, e0), eta0_order=order, eta0_is_cube_in_F64=F.pow(e0, 21) == 1)
print('eta_0 facts:', dd)
out['eta0'] = dd
# (e) F64 = F2[eta_0]
pw = [1]
for _ in range(5):
    pw.append(m(pw[-1], e0))
F64 = []
for mask in range(64):
    z = 0
    for i in range(6):
        if mask >> i & 1:
            z ^= pw[i]
    F64.append(z)
assert len(set(F64)) == 64 and all(F.frob(z, 6) == z for z in F64)
sols = [z for z in F64 if m(z, F.frob(z, 4)) == F.frob(z, 3) ^ F.frob(z, 5)]
deg = lambda z: next(k for k in (1, 2, 3, 6) if F.frob(z, k) == z)
print('solutions in F64 of X^17 = X^8 + X^32:', len(sols), ' by degree:', Counter(deg(z) for z in sols),
      ' conjugates of eta_0 among them:', sum(any(F.frob(e0, k) == z for k in range(6)) for z in sols))
out['F64_solutions'] = dict(n=len(sols), by_degree=dict(Counter(deg(z) for z in sols)))
# (f) quick downstream check
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
okf = True
for al in range(1, p):
    for be in range(1, p):
        Wv = 0
        for u in F.mu(3):
            Wv ^= m(F.t(u * al), F.t(be * pow(u, -1, p)))
        N = F.pow(Wv, 1 + 64 + 64 * 64)
        dlt = (lg[be] - lg[al]) % 6
        okf &= N == F.pow(m(eta[al], eta[be]), n[dlt] % F.order)
# formal: (*) with X = x, Xa = x^16, Xb = x^8, Xb' = x^32, Y = x^(2^d) ... reduced mod sextic, exponents mod 63
formal = {}
for dlt in range(6):
    D = pow(2, dlt, 63)
    Ex = [2 + 2 * D, 3 + 2 * D, 2 + 3 * D, 2 + D + 16 * D, 1 + 16 + 2 * D, 1 + D + 16 + 16 * D,
          16 + 16 * D + 1, 16 + 16 * D + D, 8 + 8 * D, 32 + 32 * D]
    poly = 0
    for ex in Ex:
        poly ^= mono(ex % 63)
    formal[dlt] = pmod(poly ^ mono(((1 + D) * n[dlt]) % 63), sext) == 0
print('(f) field norm == (eta(al)eta(be))^n(d) at all 1296 characters:', okf, '  formal mod sextic:', formal)
out['f_norm_closed_form_all_chars'] = okf
out['f_formal_mod_sextic'] = formal
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-algebra/a3_step2_37.json', 'w'), indent=1,
          default=str)
