"""
Reformulations of 4850's eigenvalues at m = 37 (x = t_j, y = t_k, rule-90 values), checked at
every character against direct evaluation (no logs):
  (i)   lambda_4850 (x + y) = x^32 y^2 + x^2 y^32 + x^4 + y^4                  (all characters)
  (ii)  lambda_4850 = (x + y) * R^2,  R = x + y + x y (x^15 + y^15)/(x + y)      (x != y)
  (iii) lambda_10491524 = (x y)^3 * Lambda,  Lambda = 1 + A B (A^64 + B^64),
        A = x^252, B = y^252                                                   (x y != 0)
So 4850 (equivalently its rotation) is ninth-power confined iff Lambda is a ninth power for
all j k != 0 (and the axis of 10491524, t^2 Psi_5(t)^2, is: it is).
    python lam.py
"""
import sys
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import run_targets as RT  # noqa: E402
import tables  # noqa: E402

F = RT.F36
f18 = tables.f18
M = 37
f, g = RT.expset(4850), RT.expset(10491524)
bad = [0, 0, 0]
n = [0, 0, 0]
logs9 = set()
for j in range(M):
    for k in range(M):
        x, y = f18.t(j), f18.t(k)
        lf, lg = RT.value(f, j, k), RT.value(g, j, k)
        P = lambda e, v: F.pow(v, e)  # noqa: E731
        rhs = F.mul(P(32, x), P(2, y)) ^ F.mul(P(2, x), P(32, y)) ^ P(4, x) ^ P(4, y)
        n[0] += 1
        bad[0] += F.mul(lf, x ^ y) != rhs
        if x != y:
            psi = F.mul(P(15, x) ^ P(15, y), F.inv(x ^ y))
            R = x ^ y ^ F.mul(F.mul(x, y), psi)
            n[1] += 1
            bad[1] += lf != F.mul(x ^ y, P(2, R))
        if j and k:
            A, B = P(252, x), P(252, y)
            Lam = 1 ^ F.mul(F.mul(A, B), P(64, A) ^ P(64, B))
            n[2] += 1
            bad[2] += lg != F.mul(P(3, F.mul(x, y)), Lam)
            lg_ = f18.log(Lam)
            logs9.add(None if lg_ is None else lg_ % 27)
print("(i) checked", n[0], "failures", bad[0])
print("(ii) checked", n[1], "failures", bad[1])
print("(iii) checked", n[2], "failures", bad[2], "; Lambda logs mod 27 seen:", sorted(logs9, key=str))
