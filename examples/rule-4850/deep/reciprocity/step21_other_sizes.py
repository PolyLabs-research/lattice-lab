"""Step 21: is the hidden symmetry of N = e(4,0)+e(5,2) = 4850*(a+b) special to m = 37?
For odd m in 5..301 (m prime to the support's needs), the stabiliser of supp(N) mod m in GL2(Z/m)
(column action), found by mapping two independent support points to support points.  At 37 it has
order 24 (D4 extended by R3 = [[18,-8],[-8,18]], eigenvalues 10, 26 = the cube roots of 1).
The dossier: 4850 is not ninth-power confined at 101, 109, 185, 197."""
import math
import numpy as np
from rlib import points

def stab(S, m):
    S = sorted({(p % m, q % m) for p, q in S})
    Sarr = np.array(S, dtype=np.int64)
    codes = np.sort(Sarr[:, 0] * m + Sarr[:, 1])
    p1 = S[0]
    p2 = next((s for s in S[1:] if math.gcd((p1[0] * s[1] - p1[1] * s[0]) % m, m) == 1), None)
    if p2 is None:
        return None
    det = (p1[0] * p2[1] - p1[1] * p2[0]) % m
    di = pow(det, -1, m)
    Pinv = ((p2[1] * di) % m, (-p2[0] * di) % m, (-p1[1] * di) % m, (p1[0] * di) % m)
    out = []
    for q1 in S:
        for q2 in S:
            a = (q1[0] * Pinv[0] + q2[0] * Pinv[2]) % m
            b = (q1[0] * Pinv[1] + q2[0] * Pinv[3]) % m
            c = (q1[1] * Pinv[0] + q2[1] * Pinv[2]) % m
            d = (q1[1] * Pinv[1] + q2[1] * Pinv[3]) % m
            if math.gcd((a * d - b * c) % m, m) != 1:
                continue
            img = np.sort(((a * Sarr[:, 0] + b * Sarr[:, 1]) % m) * m + (c * Sarr[:, 0] + d * Sarr[:, 1]) % m)
            if np.array_equal(img, codes):
                out.append((a, b, c, d))
    return out

if __name__ == '__main__':
  S = points((4, 0)) | points((5, 2))
  special = []
  for m in range(5, 302, 2):
    st = stab(S, m)
    if st is None:
        continue
    if len(st) > 8:
        special.append((m, len(st)))
        extra = [M for M in st if not (M[1] % m == 0 and M[2] % m == 0 or M[0] % m == 0 and M[3] % m == 0)]
        print(f'm = {m}: |Stab| = {len(st)}; non-signed-permutation elements e.g. {extra[:4]}')
  print('sizes with a stabiliser larger than D4:', special)
