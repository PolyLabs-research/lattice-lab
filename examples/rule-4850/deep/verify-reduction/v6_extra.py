"""v6: (a) claim-1 step (ii): t_{c a}/t_a is a 27th power for c in mu3, all a != 0 (and why: (2^24 - 1) R(t) = 9 * 3w = 0 mod 27);
(b) Frob^6 on the residue: R(27c) = 64 R(c) = 10 R(c) mod 27, checked on a counterexample rule;
(c) independent period check (eigen.odd_part) of one counterexample f_O = G_O^4/pi: T-invariant residue yet not cube-confined;
(d) smaller counterexamples: rules f = G_O / pi (pi f = G_O, G_O T-invariant), radius <= 17: T-invariance vs P-invariance vs cube."""
import sys, json, time
import numpy as np
import vlib as V
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen
from v2_claim1 import divide_pi, Torbit, cen, analyse, act, T, P, orbs, PI
M = V.M
t0 = time.time()
ok = all(V.res(V.mul(V.t(c * a), V.inv(V.t(a)))) == 0 for a in range(1, M) for c in V.MU3)
print('(a) t_{ca}/t_a is a 27th power for all c in mu3, a != 0:', ok, '; 2^24 mod 27 =', pow(2, 24, 27), '; (2^24 - 1) mod 27 =', (2 ** 24 - 1) % 27)
O = next(o for o in orbs if min(o) == (1, 2))
G = frozenset((cen(p), cen(q)) for p, q in O)
f = divide_pi(frozenset((4 * p, 4 * q) for p, q in G))
L = V.eig_all(f)
R = {c: V.res(L[c]) for c in L if c != (0, 0)}
OFF = [(a, b) for a in range(1, M) for b in range(1, M)]
okF = all(R[(27 * a % M, 27 * b % M)] == 10 * R[(a, b)] % 27 for (a, b) in OFF if R[(a, b)] >= 0)
diff = sum(1 for c in OFF if R[c] >= 0 and R[(27 * c[0] % M, 27 * c[1] % M)] != R[c])
print('(b) counterexample O=(1,2)-orbit, |f| =', len(f), ': R(27c) == 10 R(c) at all off-axis c:', okF, '; characters with R(27c) != R(c):', diff)
op = eigen.odd_part(f, 37)
print('(c) eigen.odd_part(f_O, 37) =', op, '; divides 87381 (all eigenvalues cubes):', 87381 % op == 0, '; 3-adic part of the period:', op // (op // 27 if op % 27 == 0 else op // 9 if op % 9 == 0 else op // 3 if op % 3 == 0 else op))
rows = []
for O in orbs:
    G = frozenset((cen(p), cen(q)) for p, q in O)
    f = divide_pi(G)
    assert f is not None and V.lmul(PI, f) == G
    a = analyse(V.eig_all(f))
    a.update(rep=min(O), size=len(O), radius=max(max(abs(p), abs(q)) for p, q in f))
    rows.append(a)
keys = ['T_inv_mu27', 'P_inv_mu27', 'P_inv_mod9', 'P_acts_as_19', 'cube_off_axis', 'ninth_off_axis']
print('(d) f = G_O/pi over', len(rows), 'orbits:', {k: sum(r[k] for r in rows) for k in keys},
      '; P_inv_mu27 == cube for all:', all(r['P_inv_mu27'] == r['cube_off_axis'] for r in rows))
bad = sorted([r for r in rows if r['T_inv_mu27'] and not r['P_inv_mu27']], key=lambda r: r['radius'])
print('    T-invariant, not mu27 P-invariant:', len(bad), '; smallest radius examples:', [(r['rep'], r['size'], int(r['radius'])) for r in bad[:4]])
if bad:
    O = next(o for o in orbs if min(o) == bad[0]['rep'])
    f = divide_pi(frozenset((cen(p), cen(q)) for p, q in O))
    op = eigen.odd_part(f, 37)
    print('    eigen.odd_part of the smallest one (radius %d, %d terms): %d; divides 87381: %s' % (bad[0]['radius'], len(f), op, 87381 % op == 0))
print('time', round(time.time() - t0, 1))
