"""sc6 (check-scope): no false positives?  Sizes 61, 97, 109 (and the 13 table, for the derivation of the 13 rule).

For each size: which hypotheses of the 37 argument hold (f = 6, single orbit, coset triple, eta cube), then
  * -3-type hexagon members and rule 4850 itself: odd part (eigen.odd_part) and 3-adic confinement level;
  * the norm criterion: off-diagonal level of each member predicted from (*) (exact where decidable:
    cube level needs 3 | 2^f - 1, ninth needs 9 | 2^f - 1) vs the direct level at the same characters.
At 13 also print the 2 x 2 table of N(W) by mu6-coset pair, from which the 13 rule follows by hand."""
import json
import sys
import cslib

sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import eigen  # noqa: E402
import census  # noqa: E402


def v3(n):
    k = 0
    while n and n % 3 == 0:
        n //= 3
        k += 1
    return k


out = {}
# ---- the 13 table
S = cslib.Setting(13, seed=9)
F = S.F
lg = {pow(2, i, 13): i for i in range(12)}
eta0, eta1 = S.eta(1), S.eta(2)
omega_ok = F.in_sub(eta0, 2) and not F.in_sub(eta0, 1) and eta0 ^ eta1 == 1
tab = {}
for ca in (0, 1):
    for cb in (0, 1):
        vals = {S.norm(S.W(al, be)) for al in range(1, 13) for be in range(1, 13)
                if lg[al] % 2 == ca and lg[be] % 2 == cb}
        assert len(vals) == 1
        v = vals.pop()
        tab['%d%d' % (ca, cb)] = {eta0: 'eta0', eta1: 'eta1', 1: '1', 0: '0'}.get(v, hex(v))
cos13 = tuple(lg[x % 13] % 2 for x in (1 - S.w, 2 - S.w, 2 - S.w * S.w))
out['13'] = dict(eta0_primitive_cube_root_in_F4=omega_ok, coset_triple_mod2=cos13, NW_by_coset_pair=tab)
print('13: eta0 is a primitive cube root in F4 (eta0 + eta1 = 1):', omega_ok, '; coset triple (mod 2):', cos13,
      '; N(W) by (coset al, coset be):', tab)

# ---- negative sizes
members = {61: [(2, 7), (1, 27), (5, 13), (3, 20)], 97: [(4, 7), (7, 12), (1, 26)], 109: [(6, 1), (1, 18), (7, 17)]}
f4850 = frozenset(map(tuple, census.rule(4850, 4)))
for m, mems in members.items():
    S = cslib.Setting(m, seed=9)
    F = S.F
    mul = F.mul
    Ne = (1 << S.e) - 1
    Nk = (1 << S.f) - 1
    A = v3(Ne)
    h = pow(2, -1, m)
    idx = (m - 1) // S.d
    reps = []
    seen = set()
    for x in range(1, m):
        if x in seen:
            continue
        reps.append(x)
        seen |= {x * u % m for u in S.mu6}
    # Frobenius orbits of mu6-cosets
    cosets = {x: next(r for r in reps if any(x * u % m == r for u in S.mu6)) for x in range(1, m)}
    orbit_of = {}
    for r in reps:
        if r in orbit_of:
            continue
        y = r
        for _ in range(S.f):
            orbit_of[cosets[y]] = r
            y = 2 * y % m
    single = len(set(orbit_of.values())) == 1
    etas_cubes = all(F.pow(S.eta(r), Nk // 3) == 1 for r in reps) if Nk % 3 == 0 else None
    rec = dict(f=S.f, ninth_decidable_by_N=Nk % 9 == 0, cube_decidable_by_N=Nk % 3 == 0, index_of_2=idx,
               single_orbit=single, eta_all_cubes_in_k=etas_cubes, K_3adic=A)
    rows = []
    for (p, q) in mems:
        assert (q * q + 3 * p * p) % m == 0
        f = cslib.divide_by_s(cslib.hex_G(p, q))
        op = eigen.odd_part(f, m)
        lev = v3(Ne // op)
        # off-diagonal: predicted level from (*) vs direct, over coset-pair representatives
        pred_lev = direct_lev = A
        mism = 0
        for al in reps:
            for be in range(1, m):
                Nst = S.star(2 * p * al % m, 2 * p * be % m)
                XY = mul(S.eta(al), S.eta(be))
                Nl = mul(Nst, F.inv(mul(XY, XY)))
                lam = mul(S.W(2 * p * al % m, 2 * p * be % m), F.inv(mul(S.t[al], S.t[be])))
                if lam == 0:
                    continue
                if S.norm(lam) != Nl:
                    mism += 1
                l = 0
                while l < A and Nk % 3 ** (l + 1) == 0 and F.pow(Nl, Nk // 3 ** (l + 1)) == 1:
                    l += 1
                pred_lev = min(pred_lev, l)
                l = 0
                while l < A and F.pow(lam, Ne // 3 ** (l + 1)) == 1:
                    l += 1
                direct_lev = min(direct_lev, l)
        cap = v3(Nk)
        rows.append(dict(p=p, q=q, terms=len(f), odd_part=op, level_all_chars=lev,
                         offdiag_level_direct=direct_lev, offdiag_level_from_star=pred_lev,
                         star_decides_up_to_level=cap, star_vs_field_norm_mismatch=mism,
                         agree=(min(direct_lev, cap) == pred_lev)))
        print(m, rows[-1], flush=True)
    op4850 = eigen.odd_part(f4850, m)
    rec['members'] = rows
    rec['4850_odd_part'] = op4850
    rec['4850_level'] = v3(Ne // op4850)
    print(m, {k: v for k, v in rec.items() if k != 'members'}, flush=True)
    out[str(m)] = rec
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc6_negatives.json', 'w'), indent=1,
          default=str)
