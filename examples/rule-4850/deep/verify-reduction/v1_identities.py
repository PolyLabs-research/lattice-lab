"""v1: exact identities.  (a) 4850's support; the 45-degree rotation f(xy, x/y) is rule 10491524 (exact Laurent);
(b) pi * f' = orbit(4,4) + orbit(7,3) (exact Laurent) and = h^4 in F2[(Z/37)^2]; h = sum_{u in mu6, e=+-1} x^u y^(e/u);
(c) h's support is invariant under T: (p, q) -> (10 p, 26 q);  (d) field side: lambda_4850(j,k) = lambda'((j+k)/2,(j-k)/2),
lambda'(a,b) t_a t_b = W(a,b)^4 with W(a,b) = sum_{u in mu3} t_{ua} t_{b/u}, W(Tc) = W(c) exactly, at all 1369 characters;
(e) independent period check with examples/linear-atlas-3/eigen.py odd_part."""
import sys, time, json
import numpy as np
import vlib as V
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen
M = V.M
t0 = time.time()
f = V.rule(4850, 4)
print('4850 orbits:', [o for i, o in enumerate(V.orbits(4)) if 4850 >> i & 1], ' |f| =', len(f))
fr = frozenset({(p + q, p - q) for p, q in f})            # f(xy, x/y): x^p y^q -> x^(p+q) y^(p-q)
r1 = V.rule(10491524, 6)
print('(a) f(xy, x/y) == rule 10491524 (exact Laurent):', fr == r1)
PI = frozenset({(1, 1), (1, -1), (-1, 1), (-1, -1)})
pif = V.lmul(PI, r1)
print('(b) pi * f\' == orbit(4,4) + orbit(7,3) exactly:', pif == frozenset(V.d4(4, 4) ^ V.d4(7, 3)))
h = {}
for u in V.MU6:
    for e in (1, -1):
        k = (u % M, e * pow(u, -1, M) % M); h[k] = h.get(k, 0) ^ 1
hs = frozenset(k for k, v in h.items() if v)
H = V.gr(hs)
print('    |supp h| =', len(hs))
H4 = V.grpow(H, 4)
H4b = V.grmul(V.grmul(H, H), V.grmul(H, H))               # honest products, no Frobenius shortcut
print('    pi f\' == h^4 in F2[(Z/37)^2] (via dilation):', np.array_equal(V.gr(pif), H4), ' (via 3 honest products):', np.array_equal(V.gr(pif), H4b))
print('(c) h invariant under T = diag(10, 26):', np.array_equal(V.grdil(H, 10, 26), H))
# (d) field side
L4850 = V.eig_all(f); L1 = V.eig_all(r1)
i2 = pow(2, -1, M)
ok_rot = all(L4850[(j, k)] == L1[((j + k) * i2 % M, (j - k) * i2 % M)] for j in range(M) for k in range(M))
print('(d) lambda_4850(j,k) = lambda\'((j+k)/2, (j-k)/2) at all characters:', ok_rot)
def W(a, b):
    v = 0
    for u in V.MU3:
        v ^= V.mul(V.t(u * a), V.t(b * pow(u, -1, M)))
    return v
okW = all(V.mul(L1[(a, b)], V.mul(V.t(a), V.t(b))) == V.power(W(a, b), 4) for a in range(M) for b in range(M))
okW2 = all(W(a, b) == V.eig(hs, a, b) for a in range(M) for b in range(M))
okT = all(W(10 * a % M, 26 * b % M) == W(a, b) for a in range(M) for b in range(M))
print('    lambda\'(a,b) t_a t_b == W(a,b)^4 at all 1369:', okW, '; W = h(zeta^a, zeta^b):', okW2, '; W(Tc) == W(c):', okT)
nz = [(j, k) for j in range(M) for k in range(M) if (j, k) != (0, 0)]
R4850 = {c: V.res(L4850[c]) for c in nz}
print('    4850: zeros off the trivial character:', sum(1 for c in nz if L4850[c] == 0),
      '; ninth-confined:', all(R4850[c] % 9 == 0 for c in nz), '; 27th-confined:', all(R4850[c] == 0 for c in nz))
reps = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
print('    4850 class residues (log omega of lambda^9709, my omega):', [R4850[c] for c in reps])
op = eigen.odd_part(f, 37)
print('(e) eigen.odd_part(4850, 37) =', op, '; divides 29127:', 29127 % op == 0, '; divides 9709:', 9709 % op == 0)
op1 = eigen.odd_part(r1, 37)
print('    eigen.odd_part(10491524, 37) =', op1, '; divides 29127:', 29127 % op1 == 0)
print('time', round(time.time() - t0, 1))
