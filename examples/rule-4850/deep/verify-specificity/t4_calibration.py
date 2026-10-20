"""t4 (claim 3): the honest p-value for '4850's residual class condition is chance', from scratch.

1. Residual identification at 37 (own bookkeeping): T-frame type of each of 4850's 11 classes (al = (j+k)/2,
   be = (j-k)/2, d = ind2(be/al) mod 6 folded by d ~ -d); which classes have an exact t-factorisation of W or a
   Frobenius stabiliser; whether the residual classes form ONE <D4, T, 2I>-orbit of W-arguments.
2. Is cube-ness of W at the residual class forced?  (i) Frobenius stabilisers of the residual argument;
   (ii) for 10491524: R(Pc) = 19 R(c) (mod 27) at every character, P = diag(1, 27) -- so P-invariance of the
   residue (threeadic's hypothesis) is equivalent to cube-confinement and cannot be used to derive it;
   (iii) the T-invariant family f_O = W_O^4/pi: cube-confinement rate (from t3).  -> the residual is 1 or 2 trits.
3. normform's null recomputed: the identity W(al, 2^d al)/(t_al t_{2^d al}) = 1 + a b^65 + a^65 b, a = t_al^63,
   b = a^(2^d), checked in own field; the rate of ninth powers over all a of order 1387 (Frobenius orbits).
4. An across-size empirical null: at primes m = 1 mod 3 with 9 | 2^d - 1 and the class values in a field with a
   nontrivial 3-part, the fraction of W_m class values (al*be != 0) that are ninth powers, overall and among the
   classes with no exact t-factorisation and no Frobenius stabiliser.  m = 19 flagged: vacuous (F(2^9)* has no
   3-part), checked on random symmetric rules.
5. Dependence of the relatives: exact Laurent identities 482758 = 4850 (1+a)(1+b), 8438150 = 4850 Phi3(xy)Phi3(x/y)
   (as symmetric units), 43250486 = 4850 (1+a)^2(1+b)^2; R2 pi = dil_10(R1 pi), R3 pi = dil_26(R1 pi) mod 37 and
   the eigenvalue relations lambda_R2 = lambda_R1^64 pi^63, lambda_R3 = lambda_R1^4096 pi^4095 off the axes.
6. The p-values."""
import sys, json, time, math, itertools
import numpy as np
import sympy
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
import c37
from t3_soundness_lib import Size, t_sum_indices, factor_W, frob_stabiliser

T0 = time.time()
OUT = {}
m = 37
Z = Size(37)
F, E = Z.F, Z.E
L = S.Logs37()
t = Z.t
ind2 = {pow(2, i, m): i for i in range(36)}
h = pow(2, -1, m)
mu3 = Z.mu3
Tm = [(1, 1), (10, 26), (26, 10)]


def W(al, be):
    v = 0
    for u in mu3:
        v ^= F.mul(int(t[u * al % m]), int(t[be * pow(u, -1, m) % m]))
    return v


# ---------------------------------------------------------------- 1. residual identification
f4850 = S.rule(4850, 4)
lam = E.values(f4850)
rows = []
for (j, k) in c37.REPS:
    al, be = (j + k) * h % m, (j - k) * h % m
    if al == 0 or be == 0:
        rows.append(dict(cls=(j, k), T_frame=(al, be), type='T-axis (4850 diagonal)'))
        continue
    dd = (ind2[be] - ind2[al]) % 6
    dd = min(dd, 6 - dd)
    cp = (4 * al % m, 4 * be % m)   # lambda_4850 = W(4 al, 4 be)/pi = W(al,be)^4/pi
    Sidx = t_sum_indices(cp[0], cp[1], m, mu3)
    fac = factor_W(Sidx, m)
    ks = [k_ for k_ in frob_stabiliser(cp, m, 36, Tm) if k_ % 36]
    v27 = int(L.log(np.array([lam[j, k]], dtype=np.uint64), 27)[0])
    vW = int(L.log(np.array([W(al, be)], dtype=np.uint64), 27)[0])
    vpi = int(L.log(np.array([F.mul(int(t[al]), int(t[be]))], dtype=np.uint64), 27)[0])
    rows.append(dict(cls=(j, k), T_frame=(al, be), d=dd, W_terms=len(Sidx), W_t_factorisation=fac,
                     frobenius_stabiliser_exponents=ks, v27_lambda=v27, v27_W=vW, v27_pi=vpi))
OUT['classes'] = rows
for r in rows:
    print(r, flush=True)
res = [r for r in rows if r.get('d') == 1]
OUT['residual_classes'] = [r['cls'] for r in res]
# one orbit?  the W-arguments (al, be) of the residual classes under <D4, T, 2I>
D4 = c37.D4
def orbit_DT2(c):
    O = set()
    for g in D4:
        for a_, b_ in Tm:
            x = (a_ * c[0] % m, b_ * c[1] % m)
            y = c37.act(g, x)
            for i in range(36):
                u = pow(2, i, m)
                O.add((u * y[0] % m, u * y[1] % m))
    return O
O1 = orbit_DT2(res[0]['T_frame'])
OUT['residual_one_orbit'] = all(r['T_frame'] in O1 for r in res)
print('residual classes', OUT['residual_classes'], 'are one <D4,T,2I>-orbit of W-arguments:', OUT['residual_one_orbit'], flush=True)

# ---------------------------------------------------------------- 2. is cube-ness forced at the residual?
OUT['residual_frobenius_stabilisers'] = [r['frobenius_stabiliser_exponents'] for r in res]
OUT['residual_W_factorisations'] = [r['W_t_factorisation'] for r in res]
R1 = S.rule(10491524, 6)
lam1 = E.values(R1)
vals = np.array([lam1[c] for c in c37.NZ], dtype=np.uint64)
R = L.log(vals, 27)
P = ((1, 0), (0, 27)); Tg = ((10, 0), (0, 26))
pP, pT = c37.perm(P), c37.perm(Tg)
offax = np.array([c[0] != 0 and c[1] != 0 for c in c37.NZ])
OUT['R1_T_invariant_mu27_offaxis'] = bool(np.all(R[pT][offax] == R[offax]))
OUT['R1_P_acts_as_19_offaxis'] = bool(np.all(R[pP][offax] == (19 * R[offax]) % 27))
# the algebra: P = Sy * 26 * T and 2^12 = 19 mod 27
P2 = c37.mm(((1, 0), (0, 36)), c37.mm(((26, 0), (0, 26)), Tg))
OUT['P_equals_Sy_26_T'] = P2 == P
OUT['2^12_mod_27'] = pow(2, 12, 27)
print('R1: T-invariant (mu27, off axes):', OUT['R1_T_invariant_mu27_offaxis'], '; R(Pc) = 19 R(c):', OUT['R1_P_acts_as_19_offaxis'],
      '; P = Sy 26 T:', OUT['P_equals_Sy_26_T'], ' => P-invariance <=> 18 R = 0 mod 27 <=> cube', flush=True)
# a T-invariant residue that is NOT a cube: from f_O = G_O^4/pi with O = <D4,T>-orbit of (1,2) (24 points)
O = set()
for g in D4:
    for a_, b_ in Tm:
        O.add(c37.act(g, (a_ * 1 % m, b_ * 2 % m)))
cen = lambda a: (a % m) - m if (a % m) > 18 else (a % m)
G4 = frozenset((4 * cen(a), 4 * cen(b)) for a, b in O)
fO, rem = S.ldiv(G4, S.PI_POLY); assert not rem
lamO = E.values(fO)
vO = np.array([lamO[c] for c in c37.NZ], dtype=np.uint64)
RO = L.log(vO, 27)
nz = (RO >= 0) & (RO[pT] >= 0) & offax
OUT['example_T_invariant_not_cube'] = dict(orbit_rep=(1, 2), orbit_size=len(O),
                                           T_invariant=bool(np.all(RO[pT][nz] == RO[nz])),
                                           cube_off_axis=bool(np.all(RO[offax & (RO >= 0)] % 3 == 0)),
                                           P_invariant=bool(np.all(RO[pP][nz] == RO[nz])))
print('T-invariant but not cube example (G_O^4/pi, O = orbit of (1,2)):', OUT['example_T_invariant_not_cube'], flush=True)

# ---------------------------------------------------------------- 3. normform's trinomial null
A = int(t[1])
a0 = F.pow(A, 63)
assert F.pow(a0, 1387) == 1 and F.pow(a0, 73) != 1 and F.pow(a0, 19) != 1
ident = []
for d in range(6):
    be = pow(2, d, m)
    b0 = F.pow(a0, 2 ** d)
    X = F.mul(a0, F.pow(b0, 65)); Y = F.mul(F.pow(a0, 65), b0)
    lhs = F.mul(W(1, be), F.pow(F.mul(A, int(t[be])), Z.N - 1))
    ident.append(lhs == (1 ^ X ^ Y))
OUT['trinomial_identity_d0..5'] = ident
gen = L.g
g1387 = F.pow(gen, Z.N // 1387)
rates = {}
for d in range(6):
    seen = set(); tot = ninth = cube = 0
    for kk in range(1, 1387):
        if kk % 19 == 0 or kk % 73 == 0:
            continue
        rep = min(kk * pow(2, i, 1387) % 1387 for i in range(36))
        if rep in seen:
            continue
        seen.add(rep)
        a = F.pow(g1387, rep)
        b = F.pow(a, 2 ** d)
        v = 1 ^ F.mul(a, F.pow(b, 65)) ^ F.mul(F.pow(a, 65), b)
        tot += 1
        if v:
            ninth += F.pow(v, L.N18 // 9) == 1
            cube += F.pow(v, L.N18 // 3) == 1
    rates[d] = dict(orbits=tot, ninth=ninth, cube=cube, rate_ninth=ninth / tot, rate_cube=cube / tot)
OUT['trinomial_null'] = rates
print('trinomial identity d=0..5:', ident, '\ntrinomial null (over a of order 1387):', rates, flush=True)

# ---------------------------------------------------------------- 4. across-size empirical null for W_m
cross = {}
for mm_ in (13, 19, 61, 97, 109, 157, 181, 193, 229, 241):
    if mm_ % 3 != 1:
        continue
    dd = sympy.n_order(2, mm_)
    if dd > 60 or (2 ** dd - 1) % 9:
        continue
    Zm = Size(mm_)
    Fm = Zm.F
    tm = Zm.t
    w = Zm.omega[0]
    Tmm = [(1, 1), (w, pow(w, -1, mm_)), (w * w % mm_, pow(w * w, -1, mm_))]
    # does the field of symmetric values have a 3-part?  values lie in F(2^(d/2)) if -1 in <2>
    half = dd // 2 if pow(2, dd // 2, mm_) == mm_ - 1 else dd
    seen = set(); tot = ninth = unforced = unforced_ninth = 0
    for al in range(1, mm_):
        for be in range(1, mm_):
            if (al, be) in seen:
                continue
            c = (al, be)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % mm_, 2 * c[1] % mm_)
            v = 0
            for u in Zm.mu3:
                v ^= Fm.mul(int(tm[u * al % mm_]), int(tm[be * pow(u, -1, mm_) % mm_]))
            if v == 0:
                continue
            nin = Fm.pow(v, Zm.N // 9) == 1
            tot += 1; ninth += nin
            Sidx = t_sum_indices(al, be, mm_, Zm.mu3)
            ks_ = [k_ for k_ in frob_stabiliser((al, be), mm_, dd, Tmm) if k_ % dd]
            forcing_ = [k_ for k_ in ks_ if (Zm.N // (2 ** math.gcd(k_, dd) - 1)) % 9 == 0]  # trivial k = d/2 does not force
            if factor_W(Sidx, mm_) is None and not forcing_:
                unforced += 1; unforced_ninth += nin
    cross[mm_] = dict(d=dd, symmetric_value_field_degree=half, three_part_of_value_field=sympy.multiplicity(3, 2 ** half - 1),
                      W_orbits=tot, W_ninth=ninth, rate=ninth / tot if tot else None,
                      unforced=unforced, unforced_ninth=unforced_ninth, unforced_rate=unforced_ninth / unforced if unforced else None)
    print('W null at m=%d:' % mm_, cross[mm_], flush=True)
OUT['cross_size_W_null'] = cross
# m = 19 vacuity: random symmetric rules
Z19 = Size(19)
rng = np.random.default_rng(7)
vac = 0; nr = 0
for _ in range(40):
    n = int(rng.integers(1, 1 << 15))
    v = Z19.E.values(S.rule(n, 4))
    nr += 1; vac += Z19.E.confined(v, 9)
OUT['m19_random_symmetric_rules_ninth_confined'] = [vac, nr]
print('m = 19: random radius-4 symmetric rules ninth-confined:', vac, 'of', nr, flush=True)

# ---------------------------------------------------------------- 5. dependence of the relatives
u_a = frozenset({(0, 0), (1, 0), (-1, 0)})       # 1 + a
u_b = frozenset({(0, 0), (0, 1), (0, -1)})       # 1 + b
dep = {}
dep['482758 = 4850 (1+a)(1+b)'] = S.lmul(S.lmul(f4850, u_a), u_b) == S.rule(482758, 5)
dep['43250486 = 4850 (1+a)^2(1+b)^2'] = S.lmul(S.lmul(f4850, S.lmul(u_a, u_a)), S.lmul(u_b, u_b)) == S.rule(43250486, 6)
u_xy = frozenset({(0, 0), (1, 1), (-1, -1)}); u_xmy = frozenset({(0, 0), (1, -1), (-1, 1)})  # 1 + t(xy), 1 + t(x/y)
dep['8438150 = 4850 (1+t(xy))(1+t(x/y))'] = S.lmul(S.lmul(f4850, u_xy), u_xmy) == S.rule(8438150, 6)
GR = Z.GR
def gr_pts(a):
    return {(i, j) for i in range(m) for j in range(m) if a[i, j]}
R1pi = GR.elem(S.lmul(R1, S.PI_POLY))
R2pi = GR.elem(S.lmul(S.rule(20982139, 6), S.PI_POLY))
R3pi = GR.elem(S.lmul(S.rule(178279803, 6), S.PI_POLY))
dep['R2 pi = dil_10(R1 pi) mod 37'] = bool(np.array_equal(GR.dil(R1pi, 10), R2pi))
dep['R3 pi = dil_26(R1 pi) mod 37'] = bool(np.array_equal(GR.dil(R1pi, 26), R3pi))
pi_v = E.values(S.PI_POLY)
l2 = E.values(S.rule(20982139, 6)); l3 = E.values(S.rule(178279803, 6))
offm = (E.J != 0) & (E.K != 0)
dep['lambda_R2 = lambda_R1^64 pi^63 off axes'] = bool(np.array_equal(l2[offm], F.vmul(F.vpow(lam1, 64), F.vpow(pi_v, 63))[offm]))
dep['lambda_R3 = lambda_R1^4096 pi^4095 off axes'] = bool(np.array_equal(l3[offm], F.vmul(F.vpow(lam1, 4096), F.vpow(pi_v, 4095))[offm]))
dep['10 = -2^6, 26 = 2^12 mod 37'] = (10 == (-pow(2, 6, m)) % m, 26 == pow(2, 12, m))
# units are ninth powers (so the multiples are confined iff 4850 is)
for name, U in (('(1+a)(1+b)', S.lmul(u_a, u_b)), ('(1+t(xy))(1+t(x/y))', S.lmul(u_xy, u_xmy)), ('pi^63 (off axes)', None)):
    if U is None:
        vv = F.vpow(pi_v, 63)[offm]
        dep['unit ' + name + ' ninth'] = bool(np.all(Z.E.qth_power_mask(vv, 9)))
    else:
        vv = E.values(U)
        dep['unit ' + name + ' ninth'] = bool(np.all(Z.E.qth_power_mask(vv, 9)[vv != 0]))
OUT['relatives_dependence'] = dep
for k_, v_ in dep.items():
    print('  ', k_, ':', v_, flush=True)

# ---------------------------------------------------------------- 6. p-values
pv = {}
pv['residual_two_trits_uniform'] = 1 / 9
pv['residual_one_trit_if_cube_granted'] = 1 / 3
pv['normform_trinomial_null_d1'] = rates[1]['rate_ninth']
pv['normform_trinomial_null_cube_d1'] = rates[1]['rate_cube']
pv['cross_size_unforced_W_ninth_rate'] = (sum(c['unforced_ninth'] for k_, c in cross.items() if k_ != 19) /
                                          max(1, sum(c['unforced'] for k_, c in cross.items() if k_ != 19)))
OUT['p_values'] = pv
print('p-values:', pv, flush=True)
OUT['time'] = round(time.time() - T0, 1)
print('time', OUT['time'])
json.dump(OUT, open('t4_calibration.json', 'w'), indent=1, default=str)
