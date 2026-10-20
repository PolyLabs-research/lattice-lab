"""t0: self-test of slib against the dossier's known facts (and census.rule only to confirm numbering)."""
import sys, time, json
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
t0 = time.time()
out = {}
E = S.Eig(37)
F = E.F
out['modulus_36'] = bin(F.mod)
out['zeta'] = E.zeta
# modulus is not Phi_37 (all-ones)
out['modulus_is_not_Phi37'] = F.mod != (1 << 37) - 1
GR = S.GroupRing(37)
L = S.Logs37()
# rule numbering vs census.rule (only to make sure we talk about the same rules)
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census
ok = all(S.rule(n, r) == frozenset(census.rule(n, r)) for n, r in [(4850, 4), (482758, 5), (10491524, 6), (20982139, 6), (178279803, 6), (21563, 4), (105299, 5), (132097, 5), (1084246, 5)])
out['rule_numbering_matches_census'] = ok
out['4850_orbits'] = [o for i, o in enumerate(S.orbits(4)) if 4850 >> i & 1]
# group ring vs eigenvalues for several rules: eigenvalues of a*b equal products
f = S.rule(4850, 4); g = S.rule(10491524, 6)
A, B = GR.elem(f), GR.elem(g)
AB = GR.mul(A, B)
pts_AB = {(i, j) for i in range(37) for j in range(37) if AB[i, j]}
vA, vB, vAB = E.values(f), E.values(g), E.values(pts_AB)
out['eig_homomorphism'] = bool(np.array_equal(F.vmul(vA, vB), vAB))
# status of the seven
status = {}
for n, r in [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)]:
    pts = S.rule(n, r)
    a = GR.elem(pts); v = E.values(pts)
    status[n] = dict(gr_cube=GR.confined(a, 3), gr_ninth=GR.confined(a, 9), gr_27=GR.confined(a, 27),
                     eig_ninth=E.confined(v, 9), eig_27=E.confined(v, 27), zeros=int((v == 0).sum()) - (1 if v[0, 0] == 0 else 0))
out['status'] = status
# R(4850)^29127 = 1 + J Jy ? (dossier) -- the idempotent check
a = GR.elem(f)
P = GR.power(a, 29127)
J = np.ones((37, 37), dtype=np.uint8)
out['R4850^29127 == 1 + J'] = bool(np.array_equal(P, GR.ONE ^ J))
# class logs mod 27 in census order (generator-dependent up to a unit; compare ninth pattern only)
reps = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
v = E.values(f)
l27 = L.log(np.array([v[j, k] for j, k in reps], dtype=np.uint64), 27)
out['4850_logs27_own_generator'] = l27.tolist()
dossier = [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18]
# same up to a unit u mod 27?
units = [u for u in range(27) if u % 3]
out['4850_logs27_equal_dossier_up_to_unit'] = [u for u in units if all((u * x) % 27 == y for x, y in zip(l27, dossier))]
# eigen.odd_part cross-check (the independent period checker)
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen
out['odd_part_4850'] = eigen.odd_part(f, 37)
out['time'] = round(time.time() - t0, 1)
for k, val in out.items():
    print(k, ':', val)
json.dump(out, open('t0_selftest.json', 'w'), indent=1, default=str)
