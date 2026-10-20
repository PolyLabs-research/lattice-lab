"""Step 16: the one remaining class (d = +-1: census classes (1,2), (1,5), (1,13) in the T frame).
(a) multiplicative search: log W(1,2) = sum n_j log t_j + sum m_i log(1 + t_i), small exponents, few factors
(meet in the middle over F(2^18)* logs);  (b) line polynomials: W on the line (x, x^k) is
sum_{u in mu6, e} x^(u + e k / u) with exponents lifted in [-18, 18]; factor over GF(2) and test whether all
factors are cyclotomic (then pilot 7's exponent bookkeeping would explain the class)."""
import itertools, json, collections
import numpy as np
import sympy as sp
import nf

m = 37
T = nf.tvec()
EXP, LOG = nf.tables()
NK = nf.NK
mu3 = [1, 10, 26]; mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
    return v
gens = {}
for j in range(1, 19):
    gens['t%d' % j] = int(LOG[T[j]])
    gens['(1+t%d)' % j] = int(LOG[1 ^ T[j]])
names = list(gens)
logs = np.array([gens[n] for n in names], dtype=np.int64)
target = int(LOG[W(1, 2)])
# half words: up to 2 factors with exponents in {-2,-1,1,2}
half = {}
exps = (-2, -1, 1, 2)
for r in (0, 1, 2):
    for combo in itertools.combinations(range(len(names)), r):
        for es in itertools.product(exps, repeat=r):
            s = sum(e * int(logs[i]) for i, e in zip(combo, es)) % NK
            half.setdefault(s, (combo, es))
hits = []
for s, (c1, e1) in list(half.items()):
    need = (target - s) % NK
    if need in half:
        c2, e2 = half[need]
        word = collections.Counter()
        for i, e in list(zip(c1, e1)) + list(zip(c2, e2)):
            word[names[i]] += e
        word = {k: v for k, v in word.items() if v}
        hits.append(word)
hits = sorted({tuple(sorted(h.items())) for h in hits}, key=len)
print('(a) W(1,2) as a word of <= 4 factors t_j^n, (1+t_i)^n, |n| <= 2:', hits[:5] if hits else 'none')
# control: same search for W(1,4) (should find t11 t14 t17) and for a random element
for lab, tgt in (('W(1,4)', int(LOG[W(1, 4)])), ('random', 123457)):
    ok = any(((tgt - s) % NK) in half for s in half)
    print('    control', lab, 'found:', ok)
# (b) line polynomials
x = sp.Symbol('x')
def cen(p):
    p %= m
    return p - m if p > m // 2 else p
cyclo = {}
for e in range(1, 400):
    if e % 37:
        cyclo[sp.Poly(sp.cyclotomic_poly(e, x), x, modulus=2).factor_list()[1][0][0].as_expr()] = e
def is_cyclotomic_factor(f):
    # an irreducible f over GF(2) divides Phi_e for e = order of its roots
    p = sp.Poly(f, x, modulus=2)
    d = p.degree()
    if d == 0:
        return True
    if p == sp.Poly(x, x, modulus=2):
        return True
    for e in range(1, 2 ** min(d, 20)):
        if (2 ** d - 1) % e:
            continue
        if sp.rem(sp.Poly(x ** e - 1, x, modulus=2), p).is_zero:
            return e
    return False
out = {}
for k in (2, 5, 13, 4):
    exps_ = [cen(u + e * k * pow(u, -1, m)) for u in mu6 for e in (1, -1)]
    cnt = collections.Counter(exps_)
    terms = [n for n, c in cnt.items() if c % 2]
    sh = -min(terms)
    poly = sp.Poly(sum(x ** (n + sh) for n in terms), x, modulus=2)
    fl = poly.factor_list()[1]
    info = []
    for f, mult in fl:
        e = is_cyclotomic_factor(f.as_expr())
        info.append((f.degree(), mult, e))
    print('(b) line (1,%d): W(x, x^%d) terms %s; factors (degree, mult, order of roots or False):' % (k, k, sorted(terms)), info)
    out[k] = info
json.dump({'word_hits_W12': [list(h) for h in hits[:20]], 'line_factors': {str(k): v for k, v in out.items()}}, open('step16_d1search.json', 'w'), indent=1, default=str)
