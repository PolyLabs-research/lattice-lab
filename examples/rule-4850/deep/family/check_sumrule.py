import famlib as L
from step11_orbitrules import orbit_numerator, rule_from, eig_coords_to_e
from sizes_engine import Size
from step4_lambda import W_values
m, r = 37, 16
S = Size(m); F = S.F
Wv, u = W_values(S, r)
h = pow(2, -1, m)
for A, A2 in ((1, 7), (5, 35)):
    Nh = orbit_numerator(eig_coords_to_e(A, A, m), m, r)
    N3 = orbit_numerator(eig_coords_to_e(A2, 3 * A2, m), m, r)
    f, st = rule_from([Nh, N3], m)
    worst_off = 0; worst_diag = 0; mism = 0
    for j in range(m):
        for k in range(m):
            if (j, k) == (0, 0): continue
            v = 0
            for a, b in f:
                v ^= F.zp[(a * j + b * k) % m]
            al, be = (j + k) * h % m, (j - k) * h % m
            if al and be:
                X = Wv[A * al % m, A * be % m] ^ Wv[A2 * al % m, 3 * A2 * be % m] ^ Wv[3 * A2 * al % m, A2 * be % m]
                pred = F.mul(X, F.inv(F.mul(F.t[al], F.t[be])))
                mism += pred != v
            if v == 0: continue
            lv = F.log3(v)
            ex = 3 - L.v3(lv, 3)
            if al and be: worst_off = max(worst_off, ex)
            else: worst_diag = max(worst_diag, ex)
    print('A=%d A2=%d: formula mismatches %d; 3-exponent off-diagonal %d (level %d), diagonal %d (level %d)' % (
        A, A2, mism, worst_off, 3 - worst_off, worst_diag, 3 - worst_diag))
