"""The residual: with W = a0 b0 + a1 b1 + a2 b2 (a_k = R_k(t_alpha), b_k = R_k(t_beta), resolvents of
F(2^18)/F64, all roots of unity of order | 189 or in mu21), write W = a0 b0 (1 + X + Y), X = a1b1/(a0b0),
Y = a2b2/(a0b0).  Tabulate (mu27 exponent, mu7 exponent) of X, Y over all classes and the 3-parts that
decide '4850 is ninth-confined' (W (t_alpha t_beta)^2 a ninth power).  The two free classes are
(alpha, beta) = (1, 2) and (1, 4) (4850 classes (1,3) and (1,8))."""
import json
import ff18 as F
from resolvents import R, tab

T = F.tvec()
rows = []
for al, be in [(1, b) for b in range(1, 19)]:
    A, B = T[al], T[be]
    a = [R(k, A) for k in range(3)]; b = [R(k, B) for k in range(3)]
    c = [F.mul(a[k], b[k]) for k in range(3)]
    Wv = c[0] ^ c[1] ^ c[2]
    X = F.mul(c[1], F.inv(c[0])); Y = F.mul(c[2], F.inv(c[0]))
    th = F.mul(Wv, F.pw(F.mul(A, B), 2))
    rows.append(dict(alpha=al, beta=be, ind_beta=F.ind37(be), d=F.ind37(be) % 6, X=tab[X], Y=tab[Y],
                     a0b0=tab[c[0]], vW=F.v27(Wv), v_theta=F.v27(th), one_plus_X_plus_Y_v27=F.v27(1 ^ X ^ Y)))
for r in rows:
    print(r)
json.dump(rows, open('residual.json', 'w'), indent=1)
