"""Step 1b/2: class values of 4850 and its relatives in the three models, their components
alpha (F(2^9)*), omega (mu27), z (mu19), and independent checks.  Writes classvalues.json."""
import json, sys, math
import numpy as np
import ff18 as F
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import census, eigen

RULES = {4850: 4, 482758: 5, 10491524: 6, 8438150: 6, 43250486: 6, 20982139: 6, 178279803: 6}
DOSSIER27 = {4850: [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18], 482758: [0, 0, 9, 9, 18, 9, 0, 0, 9, 0, 18],
             10491524: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9], 8438150: [9, 0, 0, 18, 0, 9, 0, 18, 0, 0, 18],
             43250486: [9, 18, 9, 0, 9, 9, 0, 18, 9, 18, 18], 20982139: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9],
             178279803: [9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9]}
z19 = F.z19pows()
u_basis = {i: z19[i] ^ z19[19 - i] for i in range(1, 10)}  # type II ONB of F(2^9) in the 19-model


def nb_u(a):
    """alpha in F(2^9) as sum of u_i = zeta19^i + zeta19^-i, i in 1..9."""
    S = F.nb19(a)
    A = [i for i in S if i <= 9]
    assert sorted(S) == sorted(A + [19 - i for i in A])
    return A


def theta_basis(a):
    """alpha in F(2^9) in the 37-model Gauss-period basis theta_c = t_c + t_{6c}: support of t-coords."""
    S = F.nb37(a)
    return S


def describe(v):
    a, w, z = F.comps(v)
    return dict(value=v, nb19=F.nb19(v), nb37=F.nb37(v), v27=F.v27(v), s19=z19.index(z),
                alpha_u=nb_u(a), alpha_t=F.nb37(a))


out = {}
for n, r in RULES.items():
    vals = [F.rule_value(n, r, j, k) for j, k in F.CLASSES]
    assert all(vals), n
    v27 = [F.v27(v) for v in vals]
    ninth = all(x % 9 == 0 for x in v27)
    # independent check 1: census (its own F(2^36), its own generator) logs mod 27
    zeta = [census.power(2, e) for e in range(37)]
    L = []
    for j, k in census.characters():
        v = 0
        for p, q in census.rule(n, r):
            v ^= zeta[(p * j + q * k) % 37]
        L.append(int(census.log_table()[census.coord(v)]))
    assert [tuple(c) for c in census.characters()] == F.CLASSES
    units = [u for u in range(1, 27) if math.gcd(u, 3) == 1 and all((u * l - x) % 27 == 0 for l, x in zip(L, v27))]
    # independent check 2: the eigen.odd_part period must divide 29127
    per = eigen.odd_part(census.rule(n, r), 37)
    out[n] = dict(radius=r, census_logs27=[int(x) for x in L], dossier_logs27=DOSSIER27[n], my_v27=v27,
                  unit_matching_census=units, ninth=ninth, odd_part=per, odd_part_divides_29127=29127 % per == 0,
                  classes={str(c): describe(v) for c, v in zip(F.CLASSES, vals)})
    print(n, 'v27', v27, 'census', [int(x) for x in L], 'unit', units, 'odd_part', per, 29127 % per == 0)
json.dump(out, open('classvalues.json', 'w'), indent=1)
# print the 4850 table
print('\n4850 class values: support in zeta19 basis | t basis | v27 | s19 | alpha in u-basis')
for c, d in out[4850]['classes'].items():
    print(c, d['nb19'], '|', d['nb37'], '|', d['v27'], '|', d['s19'], '|', d['alpha_u'])
