"""Step 24: the one remaining condition (class C, line k = 3) in cyclotomic terms.
G_3 of 4850 is T^2 * P5 * P7 with P5 | Psi_31 and P7 | Psi_127 (partial cyclotomic factors).
For e = 31, 127 (Mersenne: omega of order e generates F_{2^r}*), the factors of Psi_e are
P_u = prod_j (T + c_u^(2^j)), c_u = omega^u + omega^-u, one per coset u of <+-2> in (Z/e)*.
We list every factor's class (log9 at t_1), mark the ones dividing G_3, and compare the sum over
all factors with the cyclotomic-exponent value of the full Psi_e."""
from rlib import *

def field(r, poly):
    """GF(2^r) via poly (int); returns mul, pow"""
    def mul(a, b):
        res = 0
        while b:
            if b & 1:
                res ^= a
            b >>= 1
            a <<= 1
            if a >> r & 1:
                a ^= poly
        return res
    def pw(a, e):
        r_ = 1
        while e:
            if e & 1:
                r_ = mul(r_, a)
            a = mul(a, a)
            e >>= 1
        return r_
    return mul, pw

F = rule_F(4850, 4)
G3 = Q_dickson(F, 3)
g3f = dict(factor2(G3))
for e, r, poly in [(31, 5, 0b100101), (127, 7, 0b10000011)]:
    mul, pw = field(r, poly)
    w = 0b10
    assert pw(w, e) == 1 and all(pw(w, e // p) != 1 for p in [e])
    seen, rows = set(), []
    for u in range(1, e):
        if u in seen:
            continue
        coset = set()
        for j in range(r):
            coset |= {(u * pow(2, j, e)) % e, (-u * pow(2, j, e)) % e}
        seen |= coset
        cu = pw(w, u) ^ pw(w, e - u)
        # minimal polynomial over GF(2) of c_u: prod_j (T + c_u^(2^j)), coefficients in GF(2)
        poly_coeffs = [1]
        x = cu
        for j in range(r):
            new = [0] * (len(poly_coeffs) + 1)
            for i, c in enumerate(poly_coeffs):
                new[i + 1] ^= c
                new[i] ^= mul(c, x)
            poly_coeffs = new
            x = mul(x, x)
        assert all(c in (0, 1) for c in poly_coeffs)
        P = sum(c << i for i, c in enumerate(poly_coeffs))
        cls = log9(val_t1(P))
        rows.append((min(coset), cls, P in g3f))
    tot = sum(c for _, c, _ in rows) % 9
    full = log9(val_t1(psi(e)))
    print(f'Psi_{e}: {len(rows)} factors of degree {r}; (coset rep, class mod 9, divides G_3):', rows)
    print(f'   sum of classes {tot}, class of Psi_{e}(t_1) itself {full}')
print('class of T at t_1:', log9(val_t1(2)), '; G_3 =', [(deg(p), m) for p, m in factor2(G3)], '; class of G_3:', log9(val_t1(G3)))
