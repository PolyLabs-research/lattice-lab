"""sc5 (check-scope): does the same reasoning give the hexagon family's levels at 37 and the cube-level at 13?

For a -3-type member f_{p,q} (q = +-r p mod m, r^2 = -3), built here by our own exact division G / s, we compute:
  (i)  odd part of the period with linear-atlas-3/eigen.odd_part (independent checker), and its 3-adic level;
  (ii) our own direct 3-adic level from eigenvalues in our own field (all characters);
  (iii) the MECHANISM's prediction, assembled only from derived ingredients:
        off j = +-k:  lambda = W(2p al, 2p be) / (t_al t_be)   [hexagon identity, re-checked here at every char],
                      N(lambda) = N(W(2p al, 2p be)) / (eta(al) eta(be))^2 with N(W) from formula (*)
                      -> level read off from N(lambda) in k (37: ninth iff in F8; 13: cube iff N = 1);
        on  j = +-k:  lambda = 0 if p = q (mod 2), else t_{pj} t_{qj} / t_j  [derivative formula, re-checked],
                      level of t_x from N(t_x) = eta(x)^2 (derived), i.e. the Legendre class.
     The prediction is the minimum of the two parts' levels (zero eigenvalues do not count).
  (iv) the investigators' rules: 37: ninth iff p non-residue (else cube);  13: cube iff p non-residue and
       p = q (mod 2) (else full).
"""
import json
import sys
import time
import cslib

sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/family')
import eigen  # noqa: E402
import famlib  # noqa: E402  (only to cross-check our exact quotient)


def v3(n):
    k = 0
    while n % 3 == 0:
        n //= 3
        k += 1
    return k


def analyse(S, p, q):
    m, F = S.m, S.F
    mul = F.mul
    e = S.e
    Ne = (1 << e) - 1
    A = v3(Ne)
    f = cslib.divide_by_s(cslib.hex_G(p, q))
    same_as_famlib = f == famlib.hex_rule(p, q)
    h = pow(2, -1, m)
    lg = {pow(2, i, m): i for i in range(S.d)}
    kf = S.f
    Nk = (1 << kf) - 1
    lev_direct = A
    lev_off_pred = A
    lev_diag_pred = A
    bad_hex = bad_diag = zeros = 0
    seen = set()
    for j in range(m):
        for k in range(m):
            if (j, k) == (0, 0) or (j, k) in seen:
                continue
            c = (j, k)
            while c not in seen:
                seen.add(c)
                c = (2 * c[0] % m, 2 * c[1] % m)
            lam = 0
            for x, y in f:
                lam ^= S.zp[(x * j + y * k) % m]
            al, be = (j + k) * h % m, (j - k) * h % m
            if al and be:
                Wv = S.W(2 * p * al % m, 2 * p * be % m)
                pred = mul(Wv, F.inv(mul(S.t[al], S.t[be])))
                if pred != lam:
                    bad_hex += 1
                # mechanism: level from N(lambda) = (*)(2p al, 2p be) / (eta(al) eta(be))^2, in k
                Nst = S.star(2 * p * al % m, 2 * p * be % m)
                XY = mul(S.eta(al), S.eta(be))
                Nl = mul(Nst, F.inv(mul(XY, XY)))
                # lambda is a 3^l-th power in K iff (for l <= v3|k*| + ...) -- use: lambda^(Ne/3^l) = Nl^(Nk/3^l)
                l = 0
                while l < A and Nk % 3 ** (l + 1) == 0 and F.pow(Nl, Nk // 3 ** (l + 1)) == 1:
                    l += 1
                lev_off_pred = min(lev_off_pred, l)
            else:
                jj = al or be
                if (p - q) % 2 == 0:
                    pred = 0
                else:
                    pred = mul(mul(S.t[p * jj % m], S.t[q * jj % m]), F.inv(S.t[jj]))
                # on j = k: al = j, be = 0 ; on j = -k: al = 0, be = j ; the formula uses jj = j up to sign
                if pred != lam:
                    bad_diag += 1
                if pred:
                    # level of t_x from N(t_x) = eta(x)^2 (derived), assembled multiplicatively in k
                    Nd = mul(mul(F.sq(S.eta(p * jj)), F.sq(S.eta(q * jj))), F.inv(F.sq(S.eta(jj))))
                    l = 0
                    while l < A and Nk % 3 ** (l + 1) == 0 and F.pow(Nd, Nk // 3 ** (l + 1)) == 1:
                        l += 1
                    lev_diag_pred = min(lev_diag_pred, l)
            if lam == 0:
                zeros += 1
                continue
            l = 0
            while l < A and F.pow(lam, Ne // 3 ** (l + 1)) == 1:
                l += 1
            lev_direct = min(lev_direct, l)
    t0 = time.time()
    op = eigen.odd_part(f, m)
    secs = round(time.time() - t0, 1)
    lev_oddpart = v3(Ne // op) if Ne % op == 0 else None
    return dict(p=p, q=q, chi_p=cslib.legendre(p, m), same_parity=(p - q) % 2 == 0, terms=len(f),
                quotient_matches_famlib=same_as_famlib, hexagon_identity_failures=bad_hex,
                diagonal_formula_failures=bad_diag, zero_orbits=zeros, odd_part=op, level_from_odd_part=lev_oddpart,
                level_direct=lev_direct, mech_level_offdiag=lev_off_pred, mech_level_diag=lev_diag_pred,
                mech_level=min(lev_off_pred, lev_diag_pred), secs_odd_part=secs)


out = {}
# 37: q = +-16 p.  6 non-residue and 6 residue members, both parities
mem37 = [(2, 5), (5, 6), (2, 32), (8, 17), (6, 15), (13, 14), (14, 2),
         (1, 16), (1, 21), (3, 11), (7, 1), (9, 4), (12, 7), (4, 27)]
S37 = cslib.Setting(37, seed=5)
rows = []
for p, q in mem37:
    assert (q - 16 * p) % 37 == 0 or (q + 16 * p) % 37 == 0
    r = analyse(S37, p, q)
    r['investigator_rule_level'] = 2 if r['chi_p'] == -1 else 1
    rows.append(r)
    print(37, r, flush=True)
out['37'] = rows
# 13: q = +-6 p
mem13 = [(5, 9), (7, 3), (11, 1), (2, 12), (6, 10), (2, 1), (5, 4), (7, 10), (1, 6), (1, 7), (3, 5), (3, 8), (4, 2)]
S13 = cslib.Setting(13, seed=5)
rows = []
for p, q in mem13:
    assert (q - 6 * p) % 13 == 0 or (q + 6 * p) % 13 == 0
    r = analyse(S13, p, q)
    r['investigator_rule_level'] = 1 if (r['chi_p'] == -1 and r['same_parity']) else 0
    rows.append(r)
    print(13, r, flush=True)
out['13'] = rows
for m in ('37', '13'):
    ok = all(r['level_from_odd_part'] == r['level_direct'] == r['mech_level'] == r['investigator_rule_level']
             and r['hexagon_identity_failures'] == 0 and r['diagonal_formula_failures'] == 0 for r in out[m])
    print('m = %s: odd_part level == direct level == mechanism level == investigators\' rule for all members: %s'
          % (m, ok))
    out['all_agree_%s' % m] = ok
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc5_family.json', 'w'), indent=1)
