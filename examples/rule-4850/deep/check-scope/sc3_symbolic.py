"""sc3 (check-scope): is formula (*) a theorem (for every size in the setting) rather than a numerical fit?

Generic model: A_i = t_{w^i al}, B_i = t_{w^i be} (i = 0, 1, 2) are indeterminates; sigma: A_i -> A_{i+1}.
  W = A0 B0 + A1 B2 + A2 B1     (= sum_{u in mu3} t_{u al} t_{be/u})
  N = W sigma(W) sigma^2(W).
Dictionary (each entry is an elementary t-product computation valid whenever w is a primitive cube root mod m):
  X  = e1(A)                         [t_al + t_{w al} + t_{w^2 al} = eta(al)]
  Xa = e1(A) + e2(A)                 [e2 = eta(al) + eta((1-w) al)]
  Xb = S1(A) + Xa,  S1 = sum A_i^2 A_{i+1}     [S1 = eta((2+w)al) + eta((2-w)al), eta((2+w)x) = eta((1-w)x)]
  Xb'= S2(A) + Xa,  S2 = sum A_i A_{i+1}^2     [S2 = eta((2+w^2)al) + eta((2-w^2)al)]
  e3(A) = e1(A)^2                    [e3 = eta(2 al) = eta(al)^2]   <- the only relation imposed
Check: N - (*)(dictionary) lies in the ideal (e3(A) + e1(A)^2, e3(B) + e1(B)^2) of F2[A0..2, B0..2]
(Groebner basis over GF(2)).  Each dictionary entry is also checked numerically at several sizes."""
import json
import sympy as sp
import cslib

A0, A1, A2, B0, B1, B2 = sp.symbols('A0 A1 A2 B0 B1 B2')
A, B = [A0, A1, A2], [B0, B1, B2]
gens = A + B


def sig(expr, k=1):
    sub = {A[i]: A[(i + k) % 3] for i in range(3)}
    sub.update({B[i]: B[(i + k) % 3] for i in range(3)})
    return expr.xreplace(sub)


Wg = A0 * B0 + A1 * B2 + A2 * B1
N = sp.expand(Wg * sig(Wg) * sig(Wg, 2))
e1 = lambda V: V[0] + V[1] + V[2]
e2 = lambda V: V[0] * V[1] + V[0] * V[2] + V[1] * V[2]
e3 = lambda V: V[0] * V[1] * V[2]
S1 = lambda V: V[0] ** 2 * V[1] + V[1] ** 2 * V[2] + V[2] ** 2 * V[0]
S2 = lambda V: V[0] * V[1] ** 2 + V[1] * V[2] ** 2 + V[2] * V[0] ** 2
X, Y = e1(A), e1(B)
Xa, Ya = e1(A) + e2(A), e1(B) + e2(B)
Xb, Yb = S1(A) + Xa, S1(B) + Ya
Xc, Yc = S2(A) + Xa, S2(B) + Ya
star = (X**2 * Y**2 * (1 + X + Y) + X * Y * (X * Ya + Xa * Y) + X * Y * Xa * Ya + Xa * Ya * (X + Y)
        + Xb * Yb + Xc * Yc)
diff = sp.Poly(sp.expand(N - star), *gens, modulus=2)
G = sp.groebner([e3(A) + e1(A) ** 2, e3(B) + e1(B) ** 2], *gens, modulus=2, order='grevlex')
_, rem = G.reduce(diff.as_expr())
rem = sp.Poly(rem, *gens, modulus=2)
out = {'N - (*) reduces to 0 modulo (e3 = e1^2) for A and B': rem.is_zero,
       'N - (*) is zero without the relation': diff.is_zero}
print('symbolic: N - (*) == 0 in F2[A,B]/(e3 - e1^2):', rem.is_zero, '; identically zero without it:', diff.is_zero)
# is the relation e3 = e1^2 really needed? (sanity) and is the dictionary consistent with S1 + S2 = X Xa?
aux = sp.Poly(sp.expand(S1(A) + S2(A) - (e1(A) * e2(A) + e3(A))), *A, modulus=2)
out['S1 + S2 = e1 e2 + e3 (identity)'] = aux.is_zero
print('S1 + S2 = e1 e2 + e3 identically:', aux.is_zero, ' (with e3 = e1^2 this is the aux relation X Xa = Xb + Xb\')')

# numerical check of every dictionary entry at several sizes (own field model)
num = {}
for m in (13, 19, 37, 61, 109, 157 if False else 181):
    try:
        S = cslib.Setting(m, seed=3)
    except AssertionError as ex:
        num[m] = 'setting fails: %s' % ex
        continue
    F, w = S.F, S.w
    mul = F.mul
    bad = 0
    for al in range(1, m):
        a = [S.t[al], S.t[w * al % m], S.t[w * w * al % m]]
        E1 = a[0] ^ a[1] ^ a[2]
        E2 = mul(a[0], a[1]) ^ mul(a[0], a[2]) ^ mul(a[1], a[2])
        E3 = mul(mul(a[0], a[1]), a[2])
        s1 = mul(mul(a[0], a[0]), a[1]) ^ mul(mul(a[1], a[1]), a[2]) ^ mul(mul(a[2], a[2]), a[0])
        s2 = mul(a[0], mul(a[1], a[1])) ^ mul(a[1], mul(a[2], a[2])) ^ mul(a[2], mul(a[0], a[0]))
        ok = (E1 == S.eta(al) and E2 == S.eta(al) ^ S.eta((1 - w) * al) and E3 == F.sq(S.eta(al))
              and s1 == S.eta((2 - w) * al) ^ S.eta((1 - w) * al)
              and s2 == S.eta((2 - w * w) * al) ^ S.eta((1 - w) * al)
              and F.frob(a[0], S.f) == a[1])                      # sigma = Frob^f acts as w on indices
        bad += not ok
    # (*) at all pairs for the smaller sizes, a sample for 181
    pairs = [(al, be) for al in range(1, m) for be in range(1, m)]
    if m > 120:
        pairs = pairs[:: max(1, len(pairs) // 3000)]
    sb = sum(S.norm(S.W(al, be)) != S.star(al, be) for al, be in pairs)
    num[m] = dict(f=S.f, w=w, dictionary_failures=bad, star_failures=sb, star_pairs=len(pairs))
    print(m, num[m], flush=True)
out['numerical'] = num
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc3_symbolic.json', 'w'), indent=1,
          default=str)
