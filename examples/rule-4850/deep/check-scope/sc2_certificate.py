"""sc2 (check-scope): the F2[x] certificate (sympy over GF(2)) and the 'forcing' structure of the coset data,
in our own F64 = F2[y]/(y^6 + y + 1) (no 37 field at all).

(A) gcd(x^24 + x^9 + 1, x^63 + 1), its factorisation, sextic | x^21 + 1, and (*)_d = (x x^(2^d))^n(d) mod sextic.
(B) For every hypothetical coset triple (A, B, B') in (Z/6)^3 and every d, with Phi_d(X) := (*) evaluated at
    X, Y = X^(2^d), Xa = X^(2^A), Xb = X^(2^B), Xb' = X^(2^B') (and the same shifts for Y):
      cube-forced(d, e):  Phi_d(X)^e / (X Y)^2 in F8 for every X in mu21      (e = 1: core f0, e = 4: 4850)
      aux-forced(d, e):   same for every X of degree 6 with X X^(2^A) = X^(2^B) + X^(2^B')  (no cube hypothesis)
    and which X the aux relation admits (are they all cubes?).
(C) The claim 'the d = +-1 residual lands in F8 iff 2^6 = 3^3 (mod 37)': we isolate which coordinates of the
    coset triple the residual depends on, with and without the cube hypothesis."""
import itertools
import json
import sympy
from sympy import Poly, symbols, GF

x = symbols('x')
out = {}
P = lambda e: Poly(e, x, modulus=2)
aux = P(x**24 + x**9 + 1)
g = aux.gcd(P(x**63 + 1))
facs = [str(fa.as_expr()) for fa, _ in g.factor_list()[1]]
sext = [fa for fa, _ in g.factor_list()[1] if fa.degree() == 6]
out['gcd'] = str(g.as_expr())
out['factors'] = facs
assert len(sext) == 1
sx = sext[0]
out['sextic'] = str(sx.as_expr())
out['sextic | x^21+1'] = P(x**21 + 1).rem(sx).is_zero
out['sextic irreducible'] = sx.is_irreducible
print('(A) gcd =', out['gcd'], ' factors', facs, ' sextic | x^21+1:', out['sextic | x^21+1'],
      ' irreducible:', out['sextic irreducible'])

n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}


def star_exps(d, A, B, B2):
    """exponents (mod 63) of the ten monomials of (*) at X = x, Y = x^(2^d), etc. (X^(2^c) := x^(2^c))."""
    D = pow(2, d, 63)
    a, b, b2 = pow(2, A, 63), pow(2, B, 63), pow(2, B2, 63)
    X, Y, Xa, Ya, Xb, Yb, Xc, Yc = 1, D, a, a * D, b, b * D, b2, b2 * D
    E = [2 * X + 2 * Y, 3 * X + 2 * Y, 2 * X + 3 * Y,       # X^2Y^2(1 + X + Y)
         X + Y + X + Ya, X + Y + Xa + Y,                    # XY(X Ya + Xa Y)
         X + Y + Xa + Ya,                                   # XY Xa Ya
         Xa + Ya + X, Xa + Ya + Y,                          # Xa Ya (X + Y)
         Xb + Yb, Xc + Yc]                                  # Xb Yb + Xb' Yb'
    return [e % 63 for e in E]


cert = {}
for d in range(6):
    poly = P(0)
    for e in star_exps(d, 4, 3, 5):
        poly = poly + P(x**e)
    target = P(x**(((1 + pow(2, d, 63)) * n[d]) % 63))
    cert[d] = (poly - target).rem(sx).is_zero
out['(*)_d == (x x^(2^d))^n(d) mod sextic'] = cert
print('    reductions mod sextic:', cert)

# ------------------------------------------------------------------ (B) our own F64
MOD = 0b1000011   # y^6 + y + 1


def m64(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & 64:
            a ^= MOD
    return r


def p64(a, e):
    e %= 63
    r = 1
    while e:
        if e & 1:
            r = m64(r, a)
        a = m64(a, a)
        e >>= 1
    return r if a or True else 0


def fr(a, k):
    for _ in range(k % 6):
        a = m64(a, a)
    return a


def inv64(a):
    return p64(a, 62)


inF8 = lambda z: fr(z, 3) == z
els = list(range(1, 64))
mu21 = [z for z in els if p64(z, 21) == 1]
deg6 = [z for z in els if fr(z, 2) != z and fr(z, 3) != z]
assert len(mu21) == 21 and len(deg6) == 54


def Phi(X, d, A, B, B2):
    v = 0
    for e in star_exps(d, A, B, B2):
        v ^= p64(X, e)
    return v


def lands(X, d, cosd, e):
    Y = fr(X, d)
    XY = m64(X, Y)
    val = m64(p64(Phi(X, d, *cosd), e), inv64(m64(XY, XY)))
    return inF8(val)


table = {}
for cosd in itertools.product(range(6), repeat=3):
    A, B, B2 = cosd
    sols = [X for X in deg6 if m64(X, fr(X, A)) == fr(X, B) ^ fr(X, B2)]
    rec = {'n_aux_solutions_deg6': len(sols), 'aux_solutions_all_cubes': all(p64(X, 21) == 1 for X in sols)}
    for e in (1, 4):
        rec['cube_forced_e%d' % e] = [all(lands(X, d, cosd, e) for X in mu21) for d in range(6)]
        rec['aux_forced_e%d' % e] = [bool(sols) and all(lands(X, d, cosd, e) for X in sols) for d in range(6)]
    table[cosd] = rec

act = table[(4, 3, 5)]
print('(B) actual (4,3,5):', act)
res = lambda r, key: r[key][1] and r[key][5]
cube_res = sorted(c for c, r in table.items() if res(r, 'cube_forced_e4'))
cube_res1 = sorted(c for c, r in table.items() if res(r, 'cube_forced_e1'))
cube_all = sorted(c for c, r in table.items() if all(r['cube_forced_e4']))
aux_res = sorted(c for c, r in table.items() if res(r, 'aux_forced_e4'))
aux_all = sorted(c for c, r in table.items() if all(r['aux_forced_e4']))
aux_cubes = sorted(c for c, r in table.items() if r['n_aux_solutions_deg6'] and r['aux_solutions_all_cubes'])
print('    cube hypothesis, d = +-1 forced (4850, e=4): A values', sorted({c[0] for c in cube_res}),
      ' #triples', len(cube_res), '; (core, e=1): A values', sorted({c[0] for c in cube_res1}), '#', len(cube_res1))
print('    cube hypothesis, all six d forced (4850):', cube_all)
print('    aux relation only, d = +-1 forced (4850):', aux_res)
print('    aux relation only, all six forced (4850):', aux_all)
print('    triples whose aux relation admits only cubes (deg-6 solutions):', aux_cubes)
# with A = 4, which (B, B') make eta a cube via the aux relation, and do they all force the residual?
A4 = {c: (table[c]['n_aux_solutions_deg6'], table[c]['aux_solutions_all_cubes'], res(table[c], 'aux_forced_e4'))
      for c in table if c[0] == 4 and table[c]['n_aux_solutions_deg6']}
print('    A = 4 triples with degree-6 aux solutions: (n_sol, all cubes, residual forced):', A4)
out['actual'] = act
out['cube_hyp_residual_forced_triples'] = cube_res
out['cube_hyp_all_forced_triples'] = cube_all
out['aux_only_residual_forced'] = aux_res
out['aux_only_all_forced'] = aux_all
out['aux_admits_only_cubes'] = aux_cubes
out['A4_triples'] = {str(k): v for k, v in A4.items()}
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc2_certificate.json', 'w'),
          indent=1, default=str)
