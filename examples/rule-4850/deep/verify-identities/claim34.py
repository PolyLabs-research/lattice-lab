"""Claims 3 and 4, checked from scratch with vlib (own F(2^36), trinomial modulus; own Laurent and
group-ring arithmetic). eigen.odd_part (Phi_37 model of F(2^36)) is used as the independent
period checker.

Claim 3: lambda_4850(j,k) = W^4 / (t_al t_be),  al = (j+k)/2, be = (j-k)/2,
         W = sum_{u in {1, 27, 26}} t_{u al} t_{be/u}.
Claim 4: 10491524*ab = Sh(7,3)+Sh(4,4), 20982139*ab = Sh(7,4)+Sh(3,3), 178279803*ab = Sh(4,3)+Sh(7,7)
         (Laurent); dilations by 10, 26 mod 37 carry the first onto the second / third;
         lambda_g1 = lambda_f0^64 (t_j t_k)^63 and lambda_g2 = lambda_f0^4096 (t_j t_k)^4095 off the axes;
         axis restrictions Psi7 and Psi3*Psi11, ninth powers at 37; the 'iff' conclusion.
"""
import json
import sys
from math import lcm

import sympy as sp

sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-identities')
import vlib as V  # noqa: E402

sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen  # noqa: E402

M = 37
out = {}
f4850 = V.rule(4850, 4)
f0, g1, g2 = V.rule(10491524, 6), V.rule(20982139, 6), V.rule(178279803, 6)
ab = V.lp([(1, 1), (1, -1), (-1, 1), (-1, -1)])
half = pow(2, -1, M)

# ---------------------------------------------------------------- claim 3


def W(al, be, U):
    v = 0
    for u in U:
        v ^= V.fmul(V.t(u * al), V.t(be * pow(u, -1, M)))
    return v


mult_fail = quot_fail = undefined = undefined_lambda_nonzero = 0
same_W_mu3 = 0
for j in range(M):
    for k in range(M):
        al, be = (j + k) * half % M, (j - k) * half % M
        lam = V.value(f4850, j, k)
        w = W(al, be, (1, 27, 26))
        same_W_mu3 += w == W(al, be, (1, 10, 26))
        w4 = V.fpow(w, 4)
        tt = V.fmul(V.t(al), V.t(be))
        mult_fail += V.fmul(lam, tt) != w4
        if tt == 0:
            undefined += 1
            undefined_lambda_nonzero += lam != 0
        else:
            quot_fail += lam != V.fmul(w4, V.finv(tt))
out['claim3_mult_form_lambda_tt_eq_W4_failures_of_1369'] = mult_fail
out['claim3_quotient_form_failures'] = quot_fail
out['claim3_characters_with_t_al_t_be_zero'] = undefined
out['claim3_of_which_lambda_nonzero'] = undefined_lambda_nonzero
out['claim3_W_same_with_mu3_1_10_26'] = same_W_mu3

# ---------------------------------------------------------------- claim 4: Laurent identities
h0, h1, h2 = V.lmul(f0, ab), V.lmul(g1, ab), V.lmul(g2, ab)
out['claim4_h0_eq_Sh73_Sh44'] = h0 == V.ladd(V.shell(7, 3), V.shell(4, 4))
out['claim4_h1_eq_Sh74_Sh33'] = h1 == V.ladd(V.shell(7, 4), V.shell(3, 3))
out['claim4_h2_eq_Sh43_Sh77'] = h2 == V.ladd(V.shell(4, 3), V.shell(7, 7))
out['claim4_terms'] = (len(h0), len(h1), len(h2))
for d in (10, 26, 27, 11):
    out[f'claim4_dil{d}_h0_mod37'] = ('h1' if V.gdil(V.red(h0), ((d, 0), (0, d))) == V.red(h1) else
                                      'h2' if V.gdil(V.red(h0), ((d, 0), (0, d))) == V.red(h2) else 'neither')
out['claim4_10_is_minus_2^6'] = (10 + pow(2, 6, M)) % M == 0
out['claim4_26_is_2^12'] = pow(2, 12, M) == 26

# eigenvalue identities, all characters with j k != 0
fail1 = fail2 = 0
for j in range(1, M):
    for k in range(1, M):
        tt = V.fmul(V.t(j), V.t(k))
        l0 = V.value(f0, j, k)
        fail1 += V.value(g1, j, k) != V.fmul(V.fpow(l0, 64), V.fpow(tt, 63))
        fail2 += V.value(g2, j, k) != V.fmul(V.fpow(l0, 4096), V.fpow(tt, 4095))
out['claim4_g1_identity_failures_of_1296'] = fail1
out['claim4_g2_identity_failures_of_1296'] = fail2
# does the identity also hold on the axes (it need not)?
ax1 = sum(V.value(g1, 0, k) != V.fmul(V.fpow(V.value(f0, 0, k), 64), V.fpow(V.fmul(V.t(0), V.t(k)), 63))
          for k in range(1, M))
out['claim4_g1_identity_on_axis_failures_of_36'] = ax1

# axis restrictions as polynomials in t = y + 1/y
tt_ = sp.Symbol('t')


def axis_poly(S):
    """F(0, t): sum of y^b over (a, b) in S (x = 1), symmetric Laurent in y -> polynomial in t."""
    c = {}
    for _, b_ in S:
        c[b_] = c.get(b_, 0) ^ 1
    lau = {e for e, v in c.items() if v}
    assert all(-e in lau for e in lau)
    poly = sp.Integer(0)
    lau = set(lau)
    while lau:
        n = max(lau)
        if n == 0:
            poly += 1
            lau.discard(0)
            break
        # D_n(t) = y^n + y^-n + lower terms; subtract its Laurent expansion
        poly += tt_**n
        # expand t^n as Laurent in y mod 2
        ex = {0: 1}
        for _ in range(n):
            new = {}
            for e, v in ex.items():
                new[e + 1] = new.get(e + 1, 0) ^ v
                new[e - 1] = new.get(e - 1, 0) ^ v
            ex = {e: v for e, v in new.items() if v}
        lau ^= set(ex)
    return sp.Poly(poly, tt_, modulus=2)


def psi(n):
    """Psi_n(t) with Psi_n(y + 1/y) = y^(-phi(n)/2) Phi_n(y), n odd > 1, via the same expansion."""
    ph = sp.Poly(sp.cyclotomic_poly(n, tt_), tt_, modulus=2)
    h = ph.degree() // 2
    S = {(0, e - h) for (e,), cf in ph.terms() if int(cf) % 2}
    return axis_poly(S)


Psi = {n: psi(n) for n in (3, 5, 7, 11)}
out['claim4_Psi'] = {n: str(p.as_expr()) for n, p in Psi.items()}
ax = {n: axis_poly(S) for n, S in (('f0', f0), ('g1', g1), ('g2', g2), ('4850', f4850))}
out['claim4_axis_polys'] = {n: str(p.as_expr()) for n, p in ax.items()}
out['claim4_axis_g1_eq_Psi7'] = (ax['g1'] - Psi[7]).is_zero
out['claim4_axis_g2_eq_Psi3Psi11'] = (ax['g2'] - Psi[3] * Psi[11]).is_zero
out['claim4_axis_f0_eq_t2Psi5sq'] = (ax['f0'] - sp.Poly(tt_**2, tt_, modulus=2) * Psi[5] ** 2).is_zero
# ninth-powers on the axis, direct, all 36 nonzero axis characters (both axes)
for n, S in (('f0', f0), ('g1', g1), ('g2', g2), ('4850', f4850)):
    vals = [V.value(S, 0, k) for k in range(1, M)] + [V.value(S, k, 0) for k in range(1, M)]
    out[f'claim4_axis_{n}_ninth_all'] = all(v and V.is_power(v, 9, '18') for v in vals)
    out[f'claim4_axis_{n}_cube_all'] = all(v and V.is_power(v, 3, '18') for v in vals)
# 1 + zeta: cube but not ninth (used in the hand argument)
oz = 1 ^ V.ZETA
out['one_plus_zeta_cube'] = V.is_power(oz, 3)
out['one_plus_zeta_ninth'] = V.is_power(oz, 9)
dlog2 = {pow(2, e, M): e for e in range(36)}
out['dlog2_mod37_of_3_5_7_11'] = {n: dlog2[n] for n in (3, 5, 7, 11)}

# per-class ninth-power status and periods: own field and eigen.odd_part
reps = V.classes()


def status(S):
    nz = [V.value(S, j, k) for j, k in reps]
    nz = [v for v in nz if v]
    return dict(ninth=all(V.is_power(v, 9, '18') for v in nz), cube=all(V.is_power(v, 3, '18') for v in nz),
                q27=all(V.is_power(v, 27, '18') for v in nz), zeros=sum(1 for j, k in reps if V.value(S, j, k) == 0))


for n, S in (('4850', f4850), ('10491524', f0), ('20982139', g1), ('178279803', g2)):
    per, z = V.period(S)
    out[f'status_{n}'] = dict(**status(S), period_own=per, period_odd_part=eigen.odd_part(S, M))
# off-axis-only status (to make the 'iff' explicit)
for n, S in (('10491524', f0), ('20982139', g1), ('178279803', g2)):
    vals = [V.value(S, j, k) for j in range(1, M) for k in range(1, M)]
    out[f'offaxis_ninth_{n}'] = all(v == 0 or V.is_power(v, 9, '18') for v in vals)

for k_, v_ in out.items():
    print(k_, ':', v_)
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/verify-identities/claim34.json', 'w'),
          indent=1, default=str)
