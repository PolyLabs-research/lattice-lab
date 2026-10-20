"""Step 1: the explicit isomorphism between the 37-model F2(t), t = zeta37 + 1/zeta37, and the
19-model F2(zeta19) (and the 27-model F2(zeta27)) of F(2^18).  Writes isomorphism.json."""
import json
import ff18 as F

out = {}
t1 = F.t1(); T = F.tvec(); z19 = F.zeta19()
leg37 = lambda j: 1 if pow(j, 18, 37) == 1 else -1
leg19 = lambda j: 1 if pow(j, 9, 19) == 1 else -1

# 0. sanity: bar = Frob^9 acts as zeta19 -> zeta19^-1, zeta27 -> zeta27^-1, t1 -> t6
assert F.frob(z19, 9) == F.z19pows()[18]
assert F.frob(F.zeta27(), 9) == F.pw(F.zeta27(), 26)
assert F.frob(t1, 9) == T[6]
out['bar'] = 'x -> x^512 sends zeta19 -> zeta19^-1, zeta27 -> zeta27^-1, t_1 -> t_6 (2^9 = -6 mod 37)'

# 1. t_j in the zeta19 normal basis (canonical zeta19 = mu19-part of t_1)
S1 = F.nb19(t1)
out['t1_in_zeta19_basis'] = S1
rows = {}
for j in range(1, 19):
    S = F.nb19(T[j])
    rows[j] = S
    # Frobenius covariance check: t_{2j} support = 2 * support
    assert sorted(2 * i % 19 for i in S) == F.nb19(T[2 * j % 37])
out['t_j_in_zeta19_basis'] = rows
# the 18 possible identifications: zeta19' = zeta19^u gives support u^-1 * S1
alt = {u: sorted(pow(u, -1, 19) * i % 19 for i in S1) for u in range(1, 19)}
out['t1_support_for_zeta19^u'] = alt
# 2. zeta19 in the t basis; zeta19^i general
out['zeta19_in_t_basis'] = F.nb37(z19)
out['zeta19^i_in_t_basis_sizes'] = {i: len(F.nb37(F.z19pows()[i])) for i in range(1, 19)}
# 3. zeta27 in both bases, and mu9, mu3
z27 = F.zeta27()
out['zeta27_in_zeta19_basis'] = {i: F.nb19(F.pw(z27, i)) for i in (1, 2, 3, 9)}
out['zeta27_in_t_basis'] = {i: F.nb37(F.pw(z27, i)) for i in (1, 2, 3, 9)}
# 4. Gauss periods: eta19 = sum_{QR19} zeta19^a and eta37 = sum_{QR37} zeta37^a are cube roots of 1
e19, e37 = F.eta19(), F.eta37()
assert F.mul(e19, e19) ^ e19 ^ 1 == 0 and F.mul(e37, e37) ^ e37 ^ 1 == 0
rho = F.pw(z27, 9)
out['eta19 == zeta27^9'] = e19 == rho
out['eta37 == zeta27^9'] = e37 == rho
out['eta19 == eta37'] = e19 == e37
# 5. the Legendre-symbol law for rule 90 in this model
law = {}
for j in range(1, 37):
    tj = T[j]
    p = F.pw(tj, 29127)
    nonres_period = e37 ^ 1  # sum over non-residues
    law[j] = dict(leg=leg37(j), v27=F.v27(tj), t29127_is_eta_QR=p == e37, t29127_is_eta_NR=p == nonres_period)
    assert (p == nonres_period) if leg37(j) == 1 else (p == e37)
out['rule90_law'] = 't_j^29127 = sum_{u nonresidue} zeta37^u if (j/37)=1 else sum_{u residue}: verified j=1..36'
out['v27_t_j'] = {j: law[j]['v27'] for j in range(1, 19)}
# v27(t_j) = 2^ind(j) * v27(t_1) mod 27
for j in range(1, 37):
    assert law[j]['v27'] == pow(2, F.ind37(j), 27) * law[1]['v27'] % 27
# 6. components of rule-90 / rule-150 values
comp = {}
for j in (1,):
    a, w, z = F.comps(T[j])
    comp['t1'] = dict(alpha_in_t_basis=F.nb37(a), alpha_in_F512=F.in_F512(a), v27=F.v27(T[j]), z_is_zeta19=z == z19)
    a, w, z = F.comps(T[j] ^ 1)
    comp['1+t1'] = dict(v27=F.v27(T[j] ^ 1), mu19_exp=F.z19pows().index(z))
out['components'] = comp
# 7. 19-cyclotomic units: 1 + zeta19^i
cu = {}
for i in (1,):
    u = 1 ^ z19
    cu['1+zeta19'] = dict(v27=F.v27(u), mu19_exp=F.z19pows().index(F.pw(u, F.E19)), log=int(F.log(u)), order_index=int(__import__('math').gcd(int(F.log(u)), F.N)))
out['cyclotomic19'] = cu
# weights of all nonzero elements in the zeta19 basis vs t basis (distribution baseline)
json.dump(out, open('isomorphism.json', 'w'), indent=1, default=str)
for k, v in out.items():
    print(k, ':', v if not isinstance(v, dict) or len(str(v)) < 400 else str(v)[:400] + '...')
