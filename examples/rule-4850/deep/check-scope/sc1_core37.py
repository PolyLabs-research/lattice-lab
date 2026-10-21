"""sc1 (check-scope): the 37 argument recomputed in our own field model.

(a) field / normal-basis facts: zeta^1..zeta^36 independent over F2 => eta_i independent, eta_0 not in F8, != 0
(b) coset data (a, b, b') of 1-w, 2-w, 2-w^2 (log2 mod 6), log2(3), and the chain
      3^3 = 2^6 (mod 37)  <=>  log2 3 = 2 (mod 12)  =>  log2(1-w) = 4 (mod 6)   via (1-w)^2 = -3w
(c) formula (*) at all 1296 (al, be); closed form N(W) = (XY)^n(d), n = (2,-1,-4,2,-4,-1)
(d) 4850 itself: exponent set rebuilt from its D4 orbits (cross-checked with census.rule), eigenvalue at all
    1368 nonzero characters; lambda t_al t_be = W^4 off j = +-k; N(lambda) = (XY)^(4n-2); ninth-power test
    directly (lambda^((2^18-1)/9) = 1); on j = +-k: lambda = t_2j t_5j / t_j and its 3-adic level
(e) t_x: N(t_x) = eta(x)^2, cube; its ninth class tracks the Legendre symbol (derived from eta_0 being a cube)."""
import json
import sys
import cslib

sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census  # only for the rule's exponent set, to cross-check our own construction

m = 37
S = cslib.Setting(m, seed=11)
F = S.F
mul = F.mul
out = {'modulus_P': hex(F.P), 'w': S.w}
print('GF(2^36) modulus (dense random):', hex(F.P), ' weight', bin(F.P).count('1'), ' w =', S.w)

# (a) linear independence of zeta^1..zeta^36 over F2 (rank of 36 x 36 bit matrix)
def rank(vecs):
    rows, r = list(vecs), 0
    basis = {}
    for v in rows:
        while v:
            hb = v.bit_length() - 1
            if hb in basis:
                v ^= basis[hb]
            else:
                basis[hb] = v
                r += 1
                break
    return r
rk = rank(S.zp[1:])
out['rank zeta^1..36'] = rk
lg = {pow(2, k, m): k for k in range(36)}
eta = [S.eta(pow(2, i, m)) for i in range(6)]
eta0 = eta[0]
out['eta0 in F64'] = F.in_sub(eta0, 6)
out['eta0 in F8'] = F.in_sub(eta0, 3)
out['eta0 order'] = F.order(eta0)
print('(a) rank of {zeta^i} =', rk, '; eta0 in F64:', out['eta0 in F64'], ' in F8:', out['eta0 in F8'],
      ' order:', out['eta0 order'])

# (b) coset data and the 3^3 = 2^6 chain
w = S.w
cos = lambda x: lg[x % m] % 6
abb = (cos(1 - w), cos(2 - w), cos(2 - w * w))
out['coset data (a,b,b2)'] = abb
L3 = lg[3]
out['log2 3 mod 36'] = L3
out['3^3 = 2^6 mod 37'] = pow(3, 3, m) == pow(2, 6, m)
out['(1-w)^2 = -3w'] = (1 - w) ** 2 % m == (-3 * w) % m
out['log2(1-w) mod 36'] = lg[(1 - w) % m]
out['A_full = (log3 + 6)/2 mod 18'] = ((L3 + 6) // 2) % 18 if (L3 + 6) % 2 == 0 else None
out['log2 7 mod 6'] = lg[7] % 6
out['(2-w)(2-w^2) = 7'] = (2 - w) * (2 - w * w) % m == 7
print('(b) coset data =', abb, '; log2 3 =', L3, '(mod 12:', L3 % 12, '); 3^3 = 2^6:', out['3^3 = 2^6 mod 37'],
      '; log2(1-w) =', out['log2(1-w) mod 36'], ' = (log3+6)/2 mod 18 ->', out['A_full = (log3 + 6)/2 mod 18'])
print('    2-w =', (2 - w) % m, '= -8?', (2 - w) % m == m - 8, '; 2-w^2 =', (2 - w * w) % m, '= -24?',
      (2 - w * w) % m == m - 24, '; 1-w =', (1 - w) % m, '= -9?', (1 - w) % m == m - 9,
      '; log2 7 mod 6 =', out['log2 7 mod 6'])

# (c) (*) and the closed form
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
bad_star = bad_closed = bad_Wdef = 0
for al in range(1, m):
    for be in range(1, m):
        Wv = S.W(al, be)
        if Wv != S.W_def(al, be):
            bad_Wdef += 1
        N = S.norm(Wv)
        if N != S.star(al, be):
            bad_star += 1
        d = (lg[be] - lg[al]) % 6
        XY = mul(S.eta(al), S.eta(be))
        if N != F.pow(XY, n[d] % F.N):
            bad_closed += 1
out['W(sum mu3 t t) == W(definition) mismatches'] = bad_Wdef
out['(*) mismatches /1296'] = bad_star
out['closed form mismatches /1296'] = bad_closed
print('(c) W forms agree:', bad_Wdef == 0, '; (*) mismatches:', bad_star, '; closed-form mismatches:', bad_closed)

# (d) 4850
orbs = [(1, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 3), (4, 2)]
f = set()
for a, b in orbs:
    for x, y in ((a, b), (b, a)):
        for sx in (1, -1):
            for sy in (1, -1):
                f.add((sx * x, sy * y))
f = frozenset(f)
out['4850 exponent set == census.rule(4850, 4)'] = f == frozenset(map(tuple, census.rule(4850, 4)))
h = pow(2, -1, m)
Q9 = (2 ** 18 - 1) // 9
stats = dict(off=0, diag=0, zero=0, h4_bad=0, normform_bad=0, ninth_direct_fail=0, normF8_vs_direct_disagree=0,
             diag_formula_bad=0, diag_ninth_fail=0, in_F18_fail=0)
for j in range(m):
    for k in range(m):
        if (j, k) == (0, 0):
            continue
        lam = 0
        for x, y in f:
            lam ^= S.zp[(x * j + y * k) % m]
        if lam == 0:
            stats['zero'] += 1
            continue
        if not F.in_sub(lam, 18):
            stats['in_F18_fail'] += 1
        ninth = F.pow(lam, Q9) == 1
        if not ninth:
            stats['ninth_direct_fail'] += 1
        Nl = S.norm(lam)
        if F.in_sub(Nl, 3) != ninth:
            stats['normF8_vs_direct_disagree'] += 1
        al, be = (j + k) * h % m, (j - k) * h % m
        if al and be:
            stats['off'] += 1
            if mul(lam, mul(S.t[al], S.t[be])) != F.pow(S.W(al, be), 4):
                stats['h4_bad'] += 1
            d = (lg[be] - lg[al]) % 6
            XY = mul(S.eta(al), S.eta(be))
            if Nl != F.pow(XY, (4 * n[d] - 2) % F.N):
                stats['normform_bad'] += 1
        else:
            stats['diag'] += 1
            jj = al or be       # on j = +-k the character is (jj, +-jj) up to the 45-degree map
            # j = k  -> be = 0, al = j ; j = -k -> al = 0, be = j
            x = j
            pred = mul(mul(S.t[2 * x % m], S.t[5 * x % m]), F.inv(S.t[x]))
            if pred != lam:
                stats['diag_formula_bad'] += 1
out['4850'] = stats
print('(d) 4850:', stats)

# (e) t_x cube class vs Legendre symbol; N(t_x) = eta(x)^2
okN = all(S.norm(S.t[x]) == F.sq(S.eta(x)) for x in range(1, m))
cls = {}
for x in range(1, m):
    lev = F.level3(S.t[x], 18)
    # second 3-adic digit: t^((2^18-1)/9) in mu3 -> exponent relative to omega0 = t_1^((2^18-1)/9)
    v = F.pow(S.t[x], Q9)
    cls.setdefault(cslib.legendre(x, m), set()).add((lev, v))
out['N(t_x) = eta(x)^2'] = okN
out['t_x levels by Legendre symbol'] = {str(k): sorted({a for a, _ in v}) for k, v in cls.items()}
out['t_x ninth class constant on QR / on NR, and different'] = (
    len({b for _, b in cls[1]}) == 1 and len({b for _, b in cls[-1]}) == 1 and cls[1] != cls[-1])
print('(e) N(t_x) = eta(x)^2:', okN, '; t_x 3-levels by chi:', out['t_x levels by Legendre symbol'],
      '; ninth class depends only on chi(x):', out['t_x ninth class constant on QR / on NR, and different'])
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc1_core37.json', 'w'), indent=1,
          default=str)
