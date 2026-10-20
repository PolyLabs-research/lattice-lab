"""Step 4 (norms): exponent bookkeeping.  At m = 37, with X = eta(al) and Frobenius conjugates
X^(c) := eta(2^c al) = X^(2^c), formula (*) makes N(al, 2^d al) a sum of monomials X^E, E in Z/63.
Ninth-confinement of the core f0 (lambda = W / (t_al t_be)) at the class d is
        N(W) / (X^2 Y^2)  in  F8*  (= the ninth powers of F64*),   Y = X^(2^d),
(4850 = rotation of 10491524 = pi^3 f0^4 off the axes, so the same classes).
If X is a cube (X^21 = 1) write X = c w^s, c = X^15 in mu7 = F8*, w^s = X^7 in mu3; then
sum_E X^E = A0 + A1 w^s + A2 w^2s with A_r = sum_{E = r mod 3} c^(E mod 7), and it lies in F8 iff A1 = A2.
We test, for every d and for the actual coset data (a, b, b') = (4, 3, 5), whether F8-membership is FORMAL in c
(holds for every c in mu7 and both s), i.e. follows from 'eta is a cube' alone; then the same for every
hypothetical coset data (A, B, B') in (Z/6)^3; and without the cube hypothesis (all X of degree 6)."""
import json
import itertools
import collections
import nlib

p = 37
S = nlib.Setting(p)
F = S.F
m = F.mul
eta0 = S.eta(1)
g63 = F.element_of_order(63)
F64 = [F.pow(g63, k) for k in range(63)]
mu21 = [z for z in F64 if F.pow(z, 21) == 1]
ord21 = [z for z in mu21 if F.pow(z, 7) != 1]
mu7 = [z for z in F64 if F.pow(z, 7) == 1]
inF8 = lambda z: F.frob(z, 3) == z


def exponents(d, cos):
    """exponent multiset (mod 63) of N(1, 2^d) as a polynomial in X, formula (*)."""
    A, B, B2 = cos
    D = pow(2, d, 63)
    pa, pb, pb2 = pow(2, A, 63), pow(2, B, 63), pow(2, B2, 63)
    X, Y = 1, D
    Xa, Ya = pa, pa * D
    Xb, Yb = pb, pb * D
    Xc, Yc = pb2, pb2 * D
    E = []
    E += [2 * X + 2 * Y, 3 * X + 2 * Y, 2 * X + 3 * Y]                 # X^2 Y^2 (1 + X + Y)
    E += [X + Y + X + Ya, X + Y + Xa + Y]                            # X Y (X Ya + Xa Y)
    E += [X + Y + Xa + Ya]                                           # X Y Xa Ya
    E += [Xa + Ya + X, Xa + Ya + Y]                                  # Xa Ya (X + Y)
    E += [Xb + Yb, Xc + Yc]                                          # Xb Yb + Xb' Yb'
    return [x % 63 for x in E], (2 * X + 2 * Y) % 63


def reduce2(E, mod):
    c = collections.Counter(x % mod for x in E)
    return sorted(x for x, k in c.items() if k % 2)


def evaluate(E, X):
    v = 0
    for x in E:
        v ^= F.pow(X, x)
    return v


def formal_F8(E, shift):
    """is X^-shift * sum X^E in F8 for EVERY X of order 21 (cube hypothesis), checked formally
    via A1 == A2 as Laurent polynomials in c (exponents mod 7)."""
    R = reduce2([x - shift for x in E], 21)
    A = {r: collections.Counter() for r in range(3)}
    for x in R:
        A[x % 3][x % 7] += 1
    A1 = sorted(k for k, n in A[1].items() if n % 2)
    A2 = sorted(k for k, n in A[2].items() if n % 2)
    return A1 == A2, R


actual = (4, 3, 5)
res = {}
print('actual coset data (a, b, b\') =', actual)
for d in range(6):
    E, sh = exponents(d, actual)
    val = evaluate(E, eta0)
    N = S.norm_Kk(S.W(1, pow(2, d, p)))
    formal, R = formal_F8(E, sh)
    # sanity: brute force over all X of order 21
    brute = all(inF8(m(evaluate(E, X), F.inv(F.pow(X, sh)))) for X in ord21)
    res[d] = dict(formula_matches_field=val == N, exps_mod21_of_N_over_X2Y2=R, formal_F8_under_cube=formal,
                  brute_all_order21=brute, at_eta0=inF8(m(N, F.inv(F.pow(eta0, sh)))))
    print(' d=%d' % d, res[d])
# 4850 itself: N(lambda_4850) = N(W)^4 / (X^2 Y^2): same test with exponents 4E - (2X+2Y)
print('4850 (rotated, 10491524 = W^4/(t t)):')
for d in range(6):
    E, sh = exponents(d, actual)
    E4 = [4 * x for x in E]
    formal, R = formal_F8(E4, sh)
    print(' d=%d formal F8 under cube hypothesis: %s' % (d, formal))
    res[d]['4850_formal'] = formal
# without the cube hypothesis: X ranging over all 54 degree-6 elements of F64
deg6 = [X for X in F64 if F.frob(X, 2) != X and F.frob(X, 3) != X]
nocube = {}
for d in range(6):
    E, sh = exponents(d, actual)
    good = [X for X in deg6 if inF8(m(evaluate(E, X), F.inv(F.pow(X, sh))))]
    nocube[d] = dict(n_good=len(good), of=len(deg6), good_are_order21=all(F.pow(X, 21) == 1 for X in good))
    print(' no cube hypothesis, d=%d:' % d, nocube[d])
# hypothetical coset data: which (A, B, B') make every class formal-F8 under the cube hypothesis?
good_data = []
partial = collections.Counter()
for cos in itertools.product(range(6), repeat=3):
    flags = [formal_F8(*exponents(d, cos))[0] for d in range(6)]
    partial[tuple(flags)] += 1
    if all(flags):
        good_data.append(cos)
print('coset data (A, B, B\') with ALL six d formal-F8 under the cube hypothesis:', good_data)
print('pattern counts (flags for d=0..5):')
for k, v in sorted(partial.items(), key=lambda kv: -kv[1]):
    print('   ', k, v)
# also which data make d=1 alone formal
d1 = [cos for cos in itertools.product(range(6), repeat=3) if formal_F8(*exponents(1, cos))[0]]
print('coset data with d = 1 formal-F8:', d1)
json.dump(dict(actual=actual, per_d=res, no_cube=nocube, good_data=good_data, d1_good=d1,
               patterns={str(k): v for k, v in partial.items()}), open('s4_bookkeeping.json', 'w'), indent=1)
