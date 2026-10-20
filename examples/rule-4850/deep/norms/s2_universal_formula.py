"""Step 2 (norms): the universal norm formula, checked at every character for every prime of the family.

Setting: p prime, ord_p(2) = 2e with 3 | e (then 2^(e/3) = -w for a primitive cube root of 1, w in F_p);
K = F(2^e) contains t_j and W;  k = F(2^(e/3));  sigma = Frob^(e/3) generates Gal(K/k) and acts on indices
as multiplication by w (t is even).  eta(x) = sum_{u in mu6} zeta^(x u) lies in k.

PROVED (algebra, see report):  with A = t_al, sigma A = t_{w al}, sigma^2 A = t_{w^2 al} and the Lagrange resolvents
R_k(A) = A + w_F^k sigma(A) + w_F^2k sigma^2(A) of K/k:
   W(al, be) = sum_k R_k(t_al) R_k(t_be),   N_{K/k} W = x0^3 + x1^3 + x2^3 + x0 x1 x2,  x_k = R_k(t_al) R_k(t_be),
and the elementary symmetric functions of t_al over k are  e1 = eta(al),  e2 = eta(al) + eta((1-w) al),
e3 = eta(2 al) = eta(al)^2 (char 2), the cyclic sums S1 = eta((2+w)al) + eta((2-w)al),
S2 = eta((2+w^2)al) + eta((2-w^2)al),  and eta((2+w)x) = eta((2+w^2)x).  Eliminating:

  N(al, be) = X^2 Y^2 (1 + X + Y) + X Y (X Ya + Xa Y) + X Y Xa Ya + Xa Ya (X + Y) + Xb Yb + Xb' Yb'      (*)

with X = eta(al), Y = eta(be), Xa = eta((1-w) al), Xb = eta((2-w) al), Xb' = eta((2-w^2) al), same for Y.
Also checked: the auxiliary identity  X Xa = Xb + Xb'  (mod 2 product formula for periods).
Both sigma generators (w and w^2) are tried: (*) must hold for the w that sigma actually acts by."""
import json
import nlib

out = {}
for p in (13, 37, 61, 97, 109, 181, 193, 229, 277, 313, 349, 373, 397, 409, 421, 433):
    d = nlib.ordmod(2, p)
    if d % 2 or (d // 2) % 3:
        out[p] = dict(ord=d, skipped='need ord = 2e with 3 | e')
        print(p, out[p])
        continue
    if d > 64:
        out[p] = dict(ord=d, skipped='field too large for this script')
        print(p, out[p])
        continue
    S = nlib.Setting(p)
    e = d // 2
    w = (-pow(2, e // 3, p)) % p
    assert pow(w, 3, p) == 1 and w != 1
    F = S.F
    sq = lambda z: F.mul(z, z)
    m = F.mul
    eta = S.eta
    bad = 0; bad_aux = 0; total = 0
    for al in range(1, p):
        X = eta(al)
        Xa = eta((1 - w) * al % p)
        Xb = eta((2 - w) * al % p)
        Xb2 = eta((2 - w * w) * al % p)
        if m(X, Xa) != Xb ^ Xb2:
            bad_aux += 1
    for al in range(1, p):
        for be in range(1, p):
            X, Y = eta(al), eta(be)
            Xa, Ya = eta((1 - w) * al % p), eta((1 - w) * be % p)
            Xb, Yb = eta((2 - w) * al % p), eta((2 - w) * be % p)
            Xc, Yc = eta((2 - w * w) * al % p), eta((2 - w * w) * be % p)
            XY = m(X, Y)
            val = m(sq(XY), 1 ^ X ^ Y)
            val ^= m(XY, m(X, Ya) ^ m(Xa, Y))
            val ^= m(XY, m(Xa, Ya))
            val ^= m(m(Xa, Ya), X ^ Y)
            val ^= m(Xb, Yb) ^ m(Xc, Yc)
            N = S.norm_Kk(S.W(al, be))
            total += 1
            if N != val:
                bad += 1
    out[p] = dict(ord=d, e=e, k_degree=e // 3, w=w, formula_fail=bad, of=total, aux_identity_fail=bad_aux)
    print(p, out[p], flush=True)
json.dump(out, open('s2_universal_formula.json', 'w'), indent=1)
