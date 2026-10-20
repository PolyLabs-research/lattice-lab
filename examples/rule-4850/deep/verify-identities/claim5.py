"""Claim 5: the hexagon family f_{p,q} = (Hex_{p,q}(x,y) + Hex_{p,q}(y,x)) / s,
Hex_{p,q} = {+-(2p,0), +-(p,q), +-(p,-q)}, s = x + 1/x + y + 1/y.
Built here by own exact Laurent division (vlib.ldiv), eigenvalues in vlib's F(2^36) (trinomial
modulus) and periods also by examples/linear-atlas-3/eigen.py odd_part (Phi_37 model).

Checks: f_{2,5} = 4850; f_{5,6} radius 9, ninth-confined at 37 with period 29127; twins (3,11),
(4,10) cube- but not ninth-confined with period 87381; and a hand explanation via
f_{p,q} * s = dil_l(4850 * s) mod 37 when (p, +-q) = l (2, 5) mod 37, l = +-2^e, so that off the
diagonals lambda_{p,q} = lambda_4850^(2^e) s^(2^e - 1): ninth iff e even (l a square mod 37).
"""
import json
import sys

sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-identities')
import vlib as V  # noqa: E402

sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen  # noqa: E402

M = 37
s = V.lp([(1, 0), (-1, 0), (0, 1), (0, -1)])
reps = V.classes()


def hexagon(p, q):
    return V.lp([(2 * p, 0), (-2 * p, 0), (p, q), (-p, -q), (p, -q), (-p, q)])


def f_pq(p, q):
    H = hexagon(p, q)
    HT = V.lp((b, a) for a, b in H)
    num = V.ladd(H, HT)
    quo, rem = V.ldiv(num, s)
    assert not rem, (p, q)
    assert V.lmul(quo, s) == num
    return quo


def status(S):
    vals = [V.value(S, j, k) for j, k in reps]
    nz = [v for v in vals if v]
    return dict(zeros=len(vals) - len(nz),
                cube=all(V.is_power(v, 3, '18') for v in nz),
                ninth=all(V.is_power(v, 9, '18') for v in nz),
                q27=all(V.is_power(v, 27, '18') for v in nz))


out = {}
f25 = f_pq(2, 5)
out['f25_is_4850'] = f25 == V.rule(4850, 4)
dlog2 = {pow(2, e, M): e for e in range(36)}
recs = []
for p, q in [(2, 5), (5, 6), (3, 11), (4, 10)] + [(p, q) for p in range(1, 13) for q in range(1, 13)
                                                  if (q * q + 3 * p * p) % M == 0 and (p, q) not in
                                                  [(2, 5), (5, 6), (3, 11), (4, 10)]]:
    f = f_pq(p, q)
    per, z = V.period(f)
    st = status(f)
    # l with (p, q) = l (2, 5) or (p, -q) = l (2, 5) mod 37
    ls = [l_ for l_ in range(1, M) if (2 * l_ - p) % M == 0 and ((5 * l_ - q) % M == 0 or (5 * l_ + q) % M == 0)]
    lam = ls[0] if ls else None
    e = dlog2[lam] if lam else None
    qr = (pow(lam, 18, M) == 1) if lam else None
    rec = dict(p=p, q=q, terms=len(f), radius=max(max(abs(a), abs(b)) for a, b in f), d4=V.is_d4(f),
               q2_plus_3p2=q * q + 3 * p * p, l=lam, dlog2_l=e, l_is_QR=qr, **st, period_own=per,
               period_odd_part=eigen.odd_part(f, M))
    # check f*s == dil_l(4850*s) mod 37, and the off-diagonal eigenvalue formula
    if lam:
        G25 = V.red(V.lmul(f25, s))
        rec['fs_eq_dil_l_4850s_mod37'] = V.red(V.lmul(f, s)) == V.gdil(G25, ((lam, 0), (0, lam)))
        bad = n_off = 0
        diag_ninth = []
        for j in range(M):
            for k in range(M):
                sv = V.t(j) ^ V.t(k)
                lv = V.value(f, j, k)
                if sv == 0:
                    if (j, k) != (0, 0):
                        diag_ninth.append(lv != 0 and V.is_power(lv, 9, '18'))
                    continue
                n_off += 1
                pred = V.fmul(V.fpow(V.value(f25, j, k), 2**e), V.fpow(sv, 2**e - 1))
                bad += pred != lv
        rec['offdiag_formula_failures'] = bad
        rec['offdiag_checked'] = n_off
        rec['diag_all_ninth'] = all(diag_ninth)
    recs.append(rec)
    print(rec, flush=True)
out['records'] = recs
# s itself at 37: cube? ninth?  (s = t_al t_be in the diagonal frame)
sv = [V.t(j) ^ V.t(k) for j, k in reps]
out['s_nonzero_all_cubes'] = all(V.is_power(v, 3, '18') for v in sv if v)
out['s_nonzero_all_ninth'] = all(V.is_power(v, 9, '18') for v in sv if v)
out['N18_over_9'] = (2**18 - 1) // 9
out['N18_over_3'] = (2**18 - 1) // 3
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/verify-identities/claim5.json', 'w'), indent=1)
print({k: v for k, v in out.items() if k != 'records'})
