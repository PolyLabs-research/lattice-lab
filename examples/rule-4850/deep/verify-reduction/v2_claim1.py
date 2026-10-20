"""v2 (claim 1): does T-invariance (the hidden order-3 symmetry) force mu27-level invariance under P = diag(1, 27)?
Algebra: P = diag(1,-1) o (scalar 26 = 2^12) o T  (26*T = diag(260, 676) = diag(1, 10); then y -> -y gives diag(1, 27)).
So for any D4-symmetric rule with R(Tc) = R(c):  R(Pc) = R(2^12 T c) = 2^12 R(c) = 19 R(c)  (mod 27; 2^12 = 4096 = 19 mod 27).
Hence P-invariance at the mu27 level  <=>  18 R = 0 mod 27  <=>  R = 0 mod 3 (cube).  Only R mod 9 is forced (19 = 1 mod 9).
Test: (i) the matrix identity; (ii) 4850 / 10491524; (iii) the whole 'same-identity' family f_O = G_O^4 / pi, O any
<D4,T>-orbit off the axes (G_O = sum of x^c over O, centred lift): pi f_O = G_O^4 exactly, G_O T-invariant, so every
premise of normform's argument holds.  For each: T-invariance (mu27, off axes), P-invariance (mu27 and mod 9, off axes),
R(Pc) = 19 R(c), cube-confinement off axes."""
import json, time
import numpy as np
import vlib as V
M = V.M
t0 = time.time()
def mm(A, B):
    return tuple(tuple(sum(A[i][s] * B[s][j] for s in range(2)) % M for j in range(2)) for i in range(2))
T = ((10, 0), (0, 26)); P = ((1, 0), (0, 27)); Sy = ((1, 0), (0, M - 1)); S26 = ((26, 0), (0, 26))
print('(i) P == Sy * 26 * T:', mm(Sy, mm(S26, T)) == P, '; 2^12 mod 37 =', pow(2, 12, M), '; 2^12 mod 27 =', pow(2, 12, 27), '; 64 mod 27 =', 64 % 27)
def act(A, c):
    return ((A[0][0] * c[0] + A[0][1] * c[1]) % M, (A[1][0] * c[0] + A[1][1] * c[1]) % M)
OFF = [(a, b) for a in range(1, M) for b in range(1, M)]
def analyse(L):
    R = {c: V.res(L[c]) for c in L if c != (0, 0)}
    zero = sum(1 for c in OFF if R[c] < 0)
    offz = [c for c in OFF if R[c] >= 0 and R[act(T, c)] >= 0]
    Tinv = all(R[act(T, c)] == R[c] for c in offz)
    Pinv27 = all(R[act(P, c)] == R[c] for c in offz)
    Pinv9 = all((R[act(P, c)] - R[c]) % 9 == 0 for c in offz)
    p19 = all(R[act(P, c)] == 19 * R[c] % 27 for c in offz)
    cube = all(R[c] % 3 == 0 for c in offz)
    ninth = all(R[c] % 9 == 0 for c in offz)
    return dict(zeros_off_axis=zero, T_inv_mu27=Tinv, P_inv_mu27=Pinv27, P_inv_mod9=Pinv9, P_acts_as_19=p19, cube_off_axis=cube, ninth_off_axis=ninth)
out = {}
for n, r in ((10491524, 6),):
    out[str(n)] = analyse(V.eig_all(V.rule(n, r)))
    print('(ii)', n, out[str(n)])
# 4850 in its own frame: P^B = Rot^-1 P Rot, T^B = Rot^-1 T Rot  (Rot c = ((j+k)/2, (j-k)/2))
# (equivalent to (ii) by the rotation identity of v1; skipped)
# (iii) the family
def cen(p):
    p %= M
    return p - M if p > M // 2 else p
def Torbit(p, q):
    s = set()
    for c in V.MU6:
        for e in (1, -1):
            x, y = c * p % M, e * pow(c, -1, M) * q % M
            s.add((x, y)); s.add((y, x))
    return frozenset(s)
orbs = sorted({Torbit(p, q) for p in range(1, M) for q in range(1, M)}, key=lambda o: (len(o), min(o)))
def divide_pi(S):
    """exact division of a Laurent support S by pi = (x+1/x)(y+1/y) over F2; returns support or None."""
    xs = [p for p, q in S]; ys = [q for p, q in S]
    x0, y0 = min(xs), min(ys)
    A = np.zeros((max(xs) - x0 + 1, max(ys) - y0 + 1), dtype=np.uint8)
    for p, q in S:
        A[p - x0, q - y0] ^= 1
    # S = pi * Q  <=>  x y S = (x^2+1)(y^2+1) Q ; divide A by (x^2+1) along axis 0, then along axis 1
    def div_axis(A, ax):
        A = A.copy() if ax == 0 else A.T.copy()
        n = A.shape[0]
        Q = np.zeros((n - 2, A.shape[1]), dtype=np.uint8)
        for d in range(n - 1, 1, -1):
            if A[d].any():
                Q[d - 2] ^= A[d]; A[d] ^= A[d]; A[d - 2] ^= Q[d - 2]
        if A.any():
            return None
        return Q if ax == 0 else Q.T
    Q = div_axis(A, 0)
    if Q is None: return None
    Q = div_axis(Q, 1)
    if Q is None: return None
    # x y S = (x^2+1)(y^2+1) Q with Q's index (i,j) <-> x^(i+x0) y^(j+y0); so pi Q' = S with Q' = x^(x0+1) y^(y0+1) Q
    return frozenset((i + x0 + 1, j + y0 + 1) for i, j in zip(*np.nonzero(Q)))
PI = frozenset({(1, 1), (1, -1), (-1, 1), (-1, -1)})
rows = []
for O in orbs:
    G = frozenset((cen(p), cen(q)) for p, q in O)
    G4 = frozenset((4 * p, 4 * q) for p, q in G)          # G^4 = G(x^4, y^4) exactly
    f = divide_pi(G4)
    assert f is not None and V.lmul(PI, f) == G4
    L = V.eig_all(f)
    a = analyse(L)
    a.update(orbit_rep=min(O), size=len(O), terms=len(f), radius=max(max(abs(p), abs(q)) for p, q in f))
    rows.append(a)
keys = ['T_inv_mu27', 'P_inv_mu27', 'P_inv_mod9', 'P_acts_as_19', 'cube_off_axis', 'ninth_off_axis']
print('(iii) family f_O = G_O^4/pi over all', len(rows), '<D4,T>-orbits off the axes (sizes 12/24):')
for k in keys:
    print('     %-16s true for %d / %d' % (k, sum(r[k] for r in rows), len(rows)))
print('     P_inv_mu27 == cube_off_axis for every member:', all(r['P_inv_mu27'] == r['cube_off_axis'] for r in rows))
bad = [r for r in rows if r['T_inv_mu27'] and not r['P_inv_mu27']]
print('     members with T-invariance but NOT mu27 P-invariance:', len(bad), ' e.g.', [(r['orbit_rep'], r['size'], r['radius']) for r in bad[:5]])
# a fully explicit counterexample character
if bad:
    r0 = bad[0]
    O = next(o for o in orbs if min(o) == r0['orbit_rep'])
    G = frozenset((cen(p), cen(q)) for p, q in O)
    f = divide_pi(frozenset((4 * p, 4 * q) for p, q in G))
    L = V.eig_all(f)
    c = next(c for c in OFF if L[c] and V.res(L[c]) % 3)
    print('     explicit: O rep', r0['orbit_rep'], ' character c =', c, ' R(c) =', V.res(L[c]), ' R(Tc) =', V.res(L[act(T, c)]),
          ' R(Pc) =', V.res(L[act(P, c)]), ' 19 R(c) mod 27 =', 19 * V.res(L[c]) % 27)
json.dump(dict(r10491524=out, family=rows), open('v2_claim1.json', 'w'), indent=1, default=str)
print('time', round(time.time() - t0, 1))
