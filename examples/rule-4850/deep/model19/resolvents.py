"""Lagrange resolvents of K = F(2^18) over k = F64 (sigma = Frob^6, omega in F4):
   R_k(A) = A + w^k s(A) + w^2k s^2(A).   Claims (checked here):
   * R_k(A)^63 = w^-k, so R_1, R_2 lie in mu189 = mu27 x mu7; R_0 = Tr_{K/k} lies in F64;
   * A = R_0 + R_1 + R_2;  and for 10491524:  W(A, B) = sum_k R_k(A) R_k(B),  lambda' t_a t_b = W^4.
So every eigenvalue of 10491524 (= 4850 in the diagonal frame) is built from roots of unity of order | 189.
Prints the exponents of R_k(t_alpha) as zeta27^e * zeta7^f (zeta27 = x in ff18, zeta7 := g^(N/7))."""
import json
import ff18 as F

T = F.tvec()
sig = lambda x: F.pw(x, 64)
w = F.pw(F.zeta27(), 9)            # a primitive cube root of 1 (= eta37 by isomorphism.json)
assert F.mul(w, w) ^ w ^ 1 == 0
z7 = F.exp(F.N // 7).item()
z27 = F.zeta27()
tab = {}
for e in range(27):
    for f in range(7):
        tab[F.mul(F.pw(z27, e), F.pw(z7, f))] = (e, f)


def R(k, A):
    return A ^ F.mul(F.pw(w, k), sig(A)) ^ F.mul(F.pw(w, 2 * k), sig(sig(A)))


out = {}
for al in range(1, 19):
    A = T[al]
    r0, r1, r2 = R(0, A), R(1, A), R(2, A)
    assert r0 ^ r1 ^ r2 == A
    assert F.pw(r0, 64) == r0
    for k, r in ((1, r1), (2, r2)):
        assert r != 0 and F.pw(r, 63) == F.pw(w, (-k) % 3)
    out[al] = dict(R0_in_mu63=tab.get(r0), R1=tab[r1], R2=tab[r2])
# check the W formula for 10491524 on all (alpha, beta)
for al in range(1, 19):
    for be in range(1, 19):
        A, B = T[al], T[be]
        Wv = 0
        for k in range(3):
            Wv ^= F.mul(R(k, A), R(k, B))
        assert F.pw(Wv, 4) == F.mul(F.rule_value(10491524, 6, al, be), F.mul(A, B))
print('R_k^63 = w^-k, A = R0+R1+R2, W = sum R_k(A)R_k(B), lambda\'*AB = W^4: all verified')
for al in range(1, 7):
    print('alpha=%2d' % al, out[al])
json.dump(out, open('resolvents.json', 'w'), indent=1)
