"""Step 14. The twin-digit identity.  For a QR member p' and an NR member p of the -3 family at 37, with
d_p(c) = (second 3-adic digit of lambda_p(c)) = (v(lambda_p(c)) / 3) mod 3 (all values are cubes):
   d_NR(c) + d_QR(c) = eps (chi(al) + chi(be))  (mod 3)  at every off-diagonal c,
   eps = digit of t_1 (37: eps = 1); diagonal digit = eps chi(j) (2^k + 2^(k + ind r) - 1) mod 3, which at 37 is 0 for NR
   and chi(j) for QR (members with a nonzero diagonal class), and at 13 is -eps chi(j) for every member.
Same identity one level down at 13 (first digit, v mod 3).  Checked from the polynomials' eigenvalues directly."""
import json
from collections import Counter
import famlib as L

out = {}
for m, nr, qr, A in ((37, (2, 5), (1, 16), 3), (37, (5, 6), (12, 7), 3), (13, (2, 1), (1, 6), 2), (13, (5, 4), (3, 8), 2)):
    F = L.GF(m)
    h = pow(2, -1, m)
    fN, fQ = L.hex_rule(*nr), L.hex_rule(*qr)
    lvl = 3 if A == 3 else 1          # digit scale: 37 -> v/3 mod 3 ; 13 -> v mod 3

    def ev(f, j, k):
        v = 0
        for a, b in f:
            v ^= F.zp[(a * j + b * k) % m]
        return v
    ok = 0; bad = 0; pat = Counter()
    vt1 = F.log3(F.t[1])
    eps = ((vt1 // 3) % 3) if A == 3 else vt1 % 3          # the digit of t_1: v(t_j) digit = eps * chi(j)
    ind = {pow(2, i, m): i for i in range(m - 1)}
    r = {37: 16, 13: 6}[m]
    for j in range(m):
        for k in range(m):
            if (j, k) == (0, 0):
                continue
            al, be = (j + k) * h % m, (j - k) * h % m
            vN, vQ = ev(fN, j, k), ev(fQ, j, k)
            if not vN or not vQ:
                continue
            lN, lQ = F.log3(vN), F.log3(vQ)
            if A == 3:
                assert lN % 3 == 0 and lQ % 3 == 0
                dN, dQ = (lN // 3) % 3, (lQ // 3) % 3
            else:
                dN, dQ = lN % 3, lQ % 3
            if al and be:
                s = eps * (L.legendre(al, m) + L.legendre(be, m)) % 3
                good = (dN + dQ - s) % 3 == 0
                pat[('off', L.legendre(al * be, m), dN, dQ)] += 1
            else:
                jj = al or be
                # diagonal value t_pj t_qj / t_j: digit = eps chi(j) (2^k + 2^(k + ind r) - 1) mod 3 (k = ind p)
                def dg(pq):
                    kk = ind[pq[0] % m]
                    return eps * L.legendre(jj, m) * (pow(2, kk, 9) + pow(2, kk + ind[r], 9) - 1) % 3
                good = (dN - dg(nr)) % 3 == 0 and (dQ - dg(qr)) % 3 == 0
                pat[('diag', dN, dQ)] += 1
            ok += good; bad += not good
    key = '%d: NR %s, QR %s' % (m, nr, qr)
    out[key] = dict(eps=eps, holds=ok, fails=bad, patterns={str(k): v for k, v in pat.items()})
    print(key, 'identity holds at', ok, 'characters, fails at', bad)
    print('   (where, chi(al be) or -, d_NR, d_QR) counts:', dict(pat))
json.dump(out, open('step14_twins.json', 'w'), indent=1)
