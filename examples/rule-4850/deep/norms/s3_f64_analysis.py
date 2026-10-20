"""Step 3 (norms): at m = 37, reduce the residual to F64 and ask which facts about eta_0 force it.

At 37: w = 10, and the cosets (log2 mod 6) of 1 - w, 2 - w, 2 - w^2 are a = 4, b = 3, b' = 5.  So with
X = eta(al) = eta_0^(2^i), Y = eta(be) = eta_0^(2^j):  Xa = X^16, Xb = X^8, Xb' = X^32, and (*) of step 2 is a
polynomial Phi_{i,j}(eta_0).  We compute:
 (1) the minimal polynomial of eta_0 over F2 (from our GF(2^36) model) and the order of eta_0;
 (2) N(i, j) from (*) and from the field norm;
 (3) the solution set in F64 of the auxiliary relation  X^17 = X^8 + X^32  (forced by (a, b, b') = (4, 3, 5)),
     and for each solution whether Phi_{0,1}(X) (the residual class d = 1) lies in F8 -- i.e. whether the relation
     alone forces the residual, or whether more of the arithmetic of eta_0 is needed;
 (4) all 'coset data' (a, b, b') in (Z/6)^3: for every X in F64 of degree 6 satisfying X Xa = Xb + Xb' (with the
     corresponding exponents), is Phi_{0,1}(X) in F8 (d = 1) -- the 'forcing table'."""
import json
import itertools
import nlib

p = 37
S = nlib.Setting(p)
F = S.F
m = F.mul
lg = S.two
eta0 = S.eta(1)
w = 10
coset = lambda x: lg[x % p] % 6
a, b, b2 = coset(1 - w), coset(2 - w), coset(2 - w * w)
print('cosets of 1-w, 2-w, 2-w^2:', a, b, b2, '  coset of 3:', coset(3), ' of 7:', coset(7))
# F64 inside GF(2^36): elements z with z^64 = z
def frob(z, k):
    return F.frob(z, k % 6) if F.pow(z, 64) == z else None
def sub_elements():
    # F64* = <g^((2^36-1)/63)>
    g = F.element_of_order(63)
    els = [0]
    z = 1
    for _ in range(63):
        els.append(z)
        z = m(z, g)
    return els, g
F64, g63 = sub_elements()
assert F.pow(eta0, 64) == eta0
order = next(n for n in range(1, 64) if 63 % n == 0 and F.pow(eta0, n) == 1)
deg = next(k for k in (1, 2, 3, 6) if F.frob(eta0, k) == eta0)
print('eta_0: order', order, ' degree over F2', deg)
# minimal polynomial: prod (x - eta0^(2^k)) computed with coefficients in GF(2^36) (should be in F2)
coeffs = [1]
for k in range(6):
    r = F.frob(eta0, k)
    new = [0] * (len(coeffs) + 1)
    for i, c in enumerate(coeffs):
        new[i + 1] ^= c          # x * c x^i
        new[i] ^= m(c, r)        # r * c x^i
    coeffs = new
assert all(c in (0, 1) for c in coeffs)
minpoly = ''.join(str(c) for c in coeffs[::-1])
print('minimal polynomial of eta_0 (coefficients x^6..x^0):', minpoly)


def Phi(X, i_shift, j_shift, cos=(a, b, b2)):
    """(*) with Y = X^(2^j_shift)... applied to X^(2^i), using X^(c) = X^(2^c)."""
    A, B, B2 = cos
    fr = lambda z, k: F.frob(z, k % 6)
    Xi = fr(X, i_shift); Yj = fr(X, j_shift)
    Xa, Ya = fr(Xi, A), fr(Yj, A)
    Xb, Yb = fr(Xi, B), fr(Yj, B)
    Xc, Yc = fr(Xi, B2), fr(Yj, B2)
    XY = m(Xi, Yj)
    v = m(m(XY, XY), 1 ^ Xi ^ Yj)
    v ^= m(XY, m(Xi, Ya) ^ m(Xa, Yj))
    v ^= m(XY, m(Xa, Ya))
    v ^= m(m(Xa, Ya), Xi ^ Yj)
    v ^= m(Xb, Yb) ^ m(Xc, Yc)
    return v


ok = True
for i in range(6):
    for j in range(6):
        al, be = pow(2, i, p), pow(2, j, p)
        if Phi(eta0, i, j) != S.norm_Kk(S.W(al, be)):
            ok = False
print('(*) as Phi_{i,j}(eta_0) equals the field norm on (Z/6)^2:', ok)
inF8 = lambda z: F.frob(z, 3) == z
# (3) solutions of X^17 = X^8 + X^32 in F64
sols = [X for X in F64 if m(X, F.frob(X, a)) == F.frob(X, b) ^ F.frob(X, b2)]
print('#X in F64 with X * X^(2^a) = X^(2^b) + X^(2^b\'):', len(sols))
rows = []
for X in sols:
    dg = next(k for k in (1, 2, 3, 6) if F.frob(X, k) == X)
    od = 0 if X == 0 else next(n for n in range(1, 64) if 63 % n == 0 and F.pow(X, n) == 1)
    res = {d: inF8(Phi(X, 0, d)) for d in (1, 3, 5)}
    rows.append(dict(is_eta_conj=any(F.frob(eta0, k) == X for k in range(6)), degree=dg, order=od,
                     trace_F2=sum(1 for k in range(6) if True) and None,
                     Phi01_in_F8=res[1], Phi03_in_F8=res[3], Phi05_in_F8=res[5]))
for r in rows:
    print('   ', r)
# (4) forcing table over all coset data (A, B, B2) in (Z/6)^3, X ranging over the degree-6 elements of F64
deg6 = [X for X in F64 if X and F.frob(X, 2) != X and F.frob(X, 3) != X]
print('#degree-6 elements of F64:', len(deg6))
table = []
for cos in itertools.product(range(6), repeat=3):
    A, B, B2 = cos
    Xs = [X for X in deg6 if m(X, F.frob(X, A)) == F.frob(X, B) ^ F.frob(X, B2)]
    if not Xs:
        continue
    d1 = [inF8(Phi(X, 0, 1, cos)) for X in Xs]
    table.append(dict(cos=cos, n_X=len(Xs), d1_in_F8=sum(d1), all_nqr_in_F8=sum(
        all(inF8(Phi(X, 0, d, cos)) for d in (1, 3, 5)) for X in Xs)))
for t in table:
    print('   coset data', t)
json.dump(dict(cosets=(a, b, b2), eta0_order=order, eta0_degree=deg, minpoly=minpoly, star_ok=ok,
               aux_solutions=rows, forcing_table=table), open('s3_f64_analysis.json', 'w'), indent=1)
