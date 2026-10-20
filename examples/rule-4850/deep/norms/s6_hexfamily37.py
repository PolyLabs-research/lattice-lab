"""Step 6 (norms): the norm mechanism tested on the hexagon family at m = 37.

f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T) / s,  s = x + 1/x + y + 1/y  (4850 = f_{2,5}).  For q = +-16 p (mod 37) the
12-point set G_{p,q} is r * G_{2,5} mod 37 with r = p/2, and in the 45-degree coordinates
al = (j+k)/2, be = (j-k)/2 the eigenvalue of G_{2,5} is W(al, be)^4 (h^4 identity) and s(c) = t_al t_be.  So off the
diagonals j = +-k the mechanism PREDICTS, from Gauss periods alone,
   N(lambda_f(c)) = N(W(r al, r be))^4 / (eta(al)^2 eta(be)^2) = (eta(r al) eta(r be))^(4 n(d)) (eta(al) eta(be))^-2,
which lies in F8 (ninth power) iff ... and in mu21 (cube) always.  We compare with N of the directly computed
eigenvalue at every off-diagonal character, and report the diagonal characters (j = +-k) directly.
Members: all (p, q) with p, q <= 12 and q = +-16 p mod 37 (9 of them), plus all other (p, q) <= 12 as a check
that the mechanism makes no claim there (the 12-point set is not a dilate of G_{2,5})."""
import sys, json
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/model19')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import numpy as np
from hexfamily import f_pq, hex_pts   # sympy exact division; checked below in the group ring
import census
import nlib

p37 = 37
S = nlib.Setting(p37)
F = S.F
m_ = F.mul
lg = S.two
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
eta = lambda x: S.eta(x % p37)
inF8 = lambda z: F.frob(z, 3) == z
inmu21 = lambda z: F.pow(z, 21) == 1
h = pow(2, -1, p37)
assert f_pq(2, 5) == census.rule(4850, 4)


def G_set(p, q):
    H = hex_pts(p, q)
    return H ^ {(b, a) for a, b in H}


def check_division(p, q, f):
    """s * f == G exactly in F2[Z^2] (Laurent)."""
    from collections import Counter
    c = Counter()
    for a, b in f:
        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c[(a + da, b + db)] += 1
    prod = {k for k, v in c.items() if v % 2}
    return prod == G_set(p, q)


def eig(fset, j, k):
    v = 0
    for a, b in fset:
        v ^= S.zp[(a * j + b * k) % p37]
    return v


rows = []
for P in range(1, 13):
    for Q in range(1, 13):
        typ = (Q - 16 * P) % p37 == 0 or (Q + 16 * P) % p37 == 0
        if not typ:
            continue
        f = f_pq(P, Q)
        assert check_division(P, Q, f)
        r = P * h % p37
        # is G_{P,Q} = r * G_{2,5} mod 37 ?
        Gmod = {(a % p37, b % p37) for a, b in G_set(P, Q)}
        Gdil = {(r * a % p37, r * b % p37) for a, b in G_set(2, 5)}
        assert Gmod == Gdil
        mism = 0; off = 0
        pred_ninth = pred_cube = True
        act_ninth = act_cube = True
        diag_levels = set()
        zeros = 0
        for j in range(p37):
            for k in range(p37):
                if (j, k) == (0, 0):
                    continue
                lam = eig(f, j, k)
                if lam == 0:
                    zeros += 1
                    continue
                Nd = S.norm_Kk(lam)
                act_ninth &= inF8(Nd)
                act_cube &= inmu21(Nd)
                al, be = (j + k) * h % p37, (j - k) * h % p37
                if al == 0 or be == 0:
                    diag_levels.add('ninth' if inF8(Nd) else ('cube' if inmu21(Nd) else 'none'))
                    continue
                off += 1
                d = (lg[be] - lg[al]) % 6
                XY = m_(eta(al), eta(be))
                XYr = m_(eta(r * al), eta(r * be))
                Np = m_(F.pow(XYr, (4 * n[d]) % F.order), F.inv(m_(XY, XY)))
                if Np != Nd:
                    mism += 1
                pred_ninth &= inF8(Np)
                pred_cube &= inmu21(Np)
        rec = dict(p=P, q=Q, r=r, r_QR=nlib.legendre(r, p37) == 1, p_QR=nlib.legendre(P, p37) == 1,
                   off_diag_chars=off, predicted_norm_mismatches=mism,
                   predicted_offdiag=('ninth' if pred_ninth else ('cube' if pred_cube else 'none')),
                   actual_all=('ninth' if act_ninth else ('cube' if act_cube else 'none')),
                   diagonal_levels=sorted(diag_levels), zero_eigenvalues=zeros)
        rows.append(rec)
        print(rec, flush=True)
print('all predictions of N(lambda) exact off the diagonals:', all(r['predicted_norm_mismatches'] == 0 for r in rows))
print('ninth-confined members:', [(r['p'], r['q']) for r in rows if r['actual_all'] == 'ninth'],
      ' = members with p a non-residue:', [(r['p'], r['q']) for r in rows if not r['p_QR']])
json.dump(rows, open('s6_hexfamily37.json', 'w'), indent=1)
