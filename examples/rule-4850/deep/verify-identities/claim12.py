"""Claims 1 and 2, checked from scratch (vlib only; census.rule used once, only to confirm we
are talking about the same rule numbers).

Claim 1: s * f_4850 = Hex(x,y) + Hex(y,x) in F2[x^+-1, y^+-1]   (s = x + 1/x + y + 1/y)
   (a) Laurent product (exponent sets);  (b) F2[a, b] identity with Dickson polynomials (sympy);
   (c) eigenvalues at all 1369 characters in vlib's F(2^36) (trinomial modulus).
Claim 2: G = s * f_4850 mod 37 is invariant under M = [[19, 8], [8, 19]] in SL2(F_37);
   M has order 3 mod +-1; diagonal-frame form; the full stabiliser of G in GL2(F_37);
   the 'because 5^2 + 3 * 2^2 = 37' derivation (common 120-degree rotation of the two hexagons).
"""
import json
import sys
from fractions import Fraction

import sympy as sp

sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-identities')
import vlib as V  # noqa: E402

out = {}
M37 = 37

# ---------------------------------------------------------------- claim 1
f = V.rule(4850, 4)
dossier_orbits = [(1, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 3), (4, 2)]
f_from_orbits = V.lp(p for o in dossier_orbits for p in V.orbit_points(*o))
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census  # noqa: E402

out['rule4850_matches_dossier_orbits'] = f == f_from_orbits
out['rule4850_matches_census'] = f == frozenset(census.rule(4850, 4))
s = V.lp([(1, 0), (-1, 0), (0, 1), (0, -1)])
Hex = V.lp([(4, 0), (-4, 0), (2, 5), (-2, -5), (2, -5), (-2, 5)])
HexT = V.lp((b, a) for a, b in Hex)
G = V.lmul(f, s)
out['claim1_hex_disjoint'] = not (Hex & HexT)
out['claim1_laurent_identity'] = G == V.ladd(Hex, HexT)
out['claim1_equals_Sh52_plus_Sh40'] = G == V.ladd(V.shell(5, 2), V.shell(4, 0))
out['claim1_G_terms'] = len(G)
out['claim1_f_terms'] = len(f)

# (b) in F2[a, b]: x^n + x^-n = D_n(a)
a, b = sp.symbols('a b')


def dick(n, z):
    D = [sp.Integer(0), z]  # D_0 = x^0 + x^0 = 0 mod 2
    for i in range(1, n):
        D.append(sp.expand(z * D[i] - D[i - 1]))
    return D[n]


def orbit_poly(p, q):
    """sum over the D4 orbit of (p, q) of x^. y^. as a polynomial in a, b (mod 2)."""
    if p == 0 and q == 0:
        return sp.Integer(1)
    if q == 0:
        return dick(p, a) + dick(p, b)
    if p == q:
        return dick(p, a) * dick(p, b)
    return dick(p, a) * dick(q, b) + dick(q, a) * dick(p, b)


F = sum(orbit_poly(*o) for o in dossier_orbits)
S_, P_ = a + b, a * b
out['claim1b_F_equals_dossier_form'] = sp.Poly(F - (S_**3 + P_**2 * S_**2 + P_**3 + P_**2 + P_), a, b, modulus=2).is_zero
out['claim1b_F_times_s_equals_orbits_40_52'] = sp.Poly(F * (a + b) - orbit_poly(4, 0) - orbit_poly(5, 2), a, b,
                                                     modulus=2).is_zero

# (c) eigenvalues, all 1369 characters
bad = 0
for j in range(M37):
    for k in range(M37):
        lhs = V.fmul(V.value(f, j, k), V.t(j) ^ V.t(k))
        rhs = V.value(Hex, j, k) ^ V.value(HexT, j, k)
        bad += lhs != rhs
out['claim1c_eigen_failures_of_1369'] = bad

# ---------------------------------------------------------------- claim 2
Mm = ((19, 8), (8, 19))
det = (19 * 19 - 8 * 8) % M37


def mm(A, B, m=M37):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))


M2 = mm(Mm, Mm)
M3 = mm(M2, Mm)
out['claim2_det_M'] = det
out['claim2_M3'] = M3
out['claim2_M_order3_mod_pm1'] = M3 == ((36, 0), (0, 36)) and Mm != ((1, 0), (0, 1)) and Mm != ((36, 0), (0, 36))
G37 = V.red(G)
out['claim2_G_mod37_terms'] = len(G37)
out['claim2_G_invariant_under_M'] = V.gdil(G37, Mm) == G37
out['claim2_G_invariant_under_M_over_Z'] = V.lp(((19 * p + 8 * q), (8 * p + 19 * q)) for p, q in G) == G
# eigenvalue form: lambda_G(M^T c) = lambda_G(c) for all c
bad = 0
for j in range(M37):
    for k in range(M37):
        jj, kk = (19 * j + 8 * k) % M37, (8 * j + 19 * k) % M37
        bad += V.value(G, j, k) != V.value(G, jj, kk)
out['claim2_eigen_invariance_failures'] = bad
# Does f itself (not G) have the symmetry?  (G = f s; s is not M-invariant, so f's eigenvalues
# transform with the factor s(Mc)/s(c).)
out['claim2_f_invariant_under_M'] = V.gdil(V.red(f), Mm) == V.red(f)
out['claim2_s_invariant_under_M'] = V.gdil(V.red(s), Mm) == V.red(s)

# diagonal frame: R = [[1,1],[1,-1]] (exponent map of (x,y) -> (xy, x/y)); R M R^-1
R = ((1, 1), (1, 36))
Rinv = tuple(tuple(v * pow(-2, -1, M37) % M37 for v in row) for row in ((36, 36), (36, 1)))
out['claim2_R_Rinv_identity'] = mm(R, Rinv) == ((1, 0), (0, 1))
out['claim2_RMRinv'] = mm(mm(R, Mm), Rinv)
Gp = V.gdil(G37, R)
f0 = V.rule(10491524, 6)
ab = V.lp([(1, 1), (1, -1), (-1, 1), (-1, -1)])
out['claim2_rotated_f_is_10491524'] = V.gdil(V.red(f), R) == V.red(f0)
out['claim2_rotated_G_is_10491524_ab'] = Gp == V.red(V.lmul(f0, ab))
out['claim2_Gp_invariant_diag_27_11'] = V.gdil(Gp, ((27, 0), (0, 11))) == Gp
out['claim2_Gp_invariant_diag_10_26'] = V.gdil(Gp, ((10, 0), (0, 26))) == Gp
out['claim2_10_26_cube_roots'] = (pow(10, 3, 37), pow(26, 3, 37), 10 * 26 % 37, pow(27, 3, 37), 27 * 11 % 37)

# stabiliser of G37 in GL2(F_37) (brute force over 37^4 matrices; prefilter on one point)
pts = sorted(G37)
Gset = set(G37)
stab = []
p0 = pts[0]
for a11 in range(M37):
    for a12 in range(M37):
        img0 = ((a11 * p0[0] + a12 * p0[1]) % M37)
        for a21 in range(M37):
            for a22 in range(M37):
                if (a11 * a22 - a12 * a21) % M37 == 0:
                    continue
                if (img0, (a21 * p0[0] + a22 * p0[1]) % M37) not in Gset:
                    continue
                A = ((a11, a12), (a21, a22))
                if V.gdil(G37, A) == G37:
                    stab.append(A)
out['claim2_stabiliser_order'] = len(stab)
out['claim2_stabiliser_dets'] = sorted({(A[0][0] * A[1][1] - A[0][1] * A[1][0]) % M37 for A in stab})
out['claim2_M_in_stabiliser'] = Mm in stab
# does the stabiliser of f (rule 4850 itself) contain anything beyond D4?
f37 = V.red(f)
fset = set(f37)
q0 = sorted(f37)[0]
stab_f = []
for A in stab:  # anything stabilising f and G... but check f's stabiliser among all of GL2 too
    if V.gdil(f37, A) == f37:
        stab_f.append(A)
out['claim2_stabG_also_stabilising_f'] = len(stab_f)

# 'because 5^2 + 3*2^2 = 37': the 120-degree rotation of Hex_{p,q} = {+-(2p,0), +-(p,q), +-(p,-q)}
# maps v1=(2p,0) -> v2-v1, v2=(p,q) -> -v1. Exact rational matrices, then compared mod primes.


def rot(p, q):
    v1, v2 = (Fraction(2 * p), Fraction(0)), (Fraction(p), Fraction(q))
    # R B = B C, B = [v1 v2] columns, C = [[-1,-1],[1,0]]
    B = ((v1[0], v2[0]), (v1[1], v2[1]))
    detB = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    Bi = ((B[1][1] / detB, -B[0][1] / detB), (-B[1][0] / detB, B[0][0] / detB))
    C = ((-1, -1), (1, 0))

    def mmq(X, Y):
        return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    return mmq(mmq(B, C), Bi)


Rq = rot(2, 5)
RqT = ((Rq[0][0], Rq[1][0]), (Rq[0][1], Rq[1][1]))  # conjugate by the swap = transpose here? check below
swap = ((0, 1), (1, 0))


def mmq(X, Y):
    return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)) for i in range(2))


Rq_swapped = mmq(mmq(swap, Rq), swap)  # rotation of the transposed hexagon
out['claim2_rotation_Q'] = [[str(v) for v in row] for row in Rq]
out['claim2_rotation_transposed_Q'] = [[str(v) for v in row] for row in Rq_swapped]
diff = [Rq[i][j] - Rq_swapped[i][j] for i in range(2) for j in range(2)]
nums = sorted({abs(d.numerator) for d in diff if d != 0})
out['claim2_numerators_of_R_minus_Rswap'] = nums
out['claim2_primes_where_rotations_agree'] = sorted({p for n in nums for p in sp.primefactors(n)})


def modp(Q, m):
    return tuple(tuple(v.numerator * pow(v.denominator, -1, m) % m for v in row) for row in Q)


out['claim2_rotation_mod37'] = modp(Rq, 37)
out['claim2_minus_rotation_mod37_equals_M'] = tuple(tuple((-v) % 37 for v in row) for row in modp(Rq, 37)) == Mm
out['claim2_hex_maps_to_itself_over_Q'] = V.lp((int(Rq[0][0] * x + Rq[0][1] * y), int(Rq[1][0] * x + Rq[1][1] * y))
                                               for x, y in Hex) == Hex

for k_, v_ in out.items():
    print(k_, ':', v_)
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/verify-identities/claim12.json', 'w'),
          indent=1, default=str)
