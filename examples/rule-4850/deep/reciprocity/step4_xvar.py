"""Step 4: the same in the x-variable.  F(2^36) = F_64[x]/(phi_0), phi_0 a sextic factor of Phi_37
over F_64 (x -> zeta).  For the class (1, k): X_k(x) = x^(deg G_k) G_k(x + 1/x) = x^N f(x, x^k);
(X_k/phi_0)_9 = (phi_0/X_k)_9 = prod_R (phi_0/R)_9 over the F_64-irreducible factors R of X_k.
Checks the law against X_k(zeta)^((2^36-1)/9) and prints the symbols, plus the reduced form
X_k mod phi_0 (degree <= 5) with its roots' degrees and symbols.  Output: step4_xvar.txt"""
import sys
from rlib import *

KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
PH = phis()
prod = [1]
for p in PH:
    prod = q_mul(prod, p)
assert prod == q_from2(phi37())
PH0 = PH[0]
print('phi_0 =', PH0, ' phi_0(0) =', PH0[0])

def xpoly(G):
    """x^deg(G) G(x + 1/x) over GF(2), as int"""
    d = deg(G)
    # (x + 1/x)^i x^d = x^(d-i) (x^2+1)^i
    out = 0
    p = 1
    for i in range(d + 1):
        if G >> i & 1:
            out ^= p << (d - i)
        p = clmul(p, 0b101)
    return out

def mu9_of_36(v):
    """the F(2^36) ninth-power symbol v^((2^36-1)/9) as an F_64 element"""
    return f36_to_f64()[f36_pow(v, NINTH36)]

def val_zeta(X):
    return pmod(X, phi37())

lines = []
for n, r in [(4850, 4), (482758, 5), (10491524, 6), (20982139, 6), (178279803, 6)]:
    F = rule_F(n, r)
    lines.append(f'=== rule {n}')
    for k in KS:
        G = Q_dickson(F, k)
        X = xpoly(G)
        # cross-check X(zeta) = zeta^deg G * G(t_1) and X equals x^N f(x, x^k) up to a shift
        g, shift = g_line(rule_points(n, r), k)
        assert X == g << (deg(X) - deg(g)) or X == g, 'x-poly matches f(x,x^k)'
        direct = mu9_of_36(val_zeta(X))
        total = 1
        parts = []
        for p, e in factor2(X):
            for R in split_over_64(p):
                s = symbol9(PH0, R)
                total = m64(total, pow64(s, e))
                parts.append(f'{q_deg(R)}{"^%d" % e if e > 1 else ""}:{mu9_index(s)}')
        assert total == direct, (n, k)
        red = q_mod(q_from2(X), PH0)
        lc, facs = factor64(red)
        rs = ' '.join(f'deg{q_deg(list(R))}{"^%d" % e if e > 1 else ""}:{mu9_index(symbol9(PH0, list(R)))}' for R, e in facs)
        lines.append(f'  k={k:2d} symbol {mu9_index(direct)}  factors(deg:sym) {" ".join(parts)}')
        lines.append(f'        reduced mod phi_0: deg {q_deg(red)}, lc-sym {mu9_index(pow64(lc, 7 * 6))}, roots {rs}')
print('\n'.join(lines))
open('step4_xvar.txt', 'w').write('phi_0 = ' + str(PH0) + '\n' + '\n'.join(lines) + '\n')
