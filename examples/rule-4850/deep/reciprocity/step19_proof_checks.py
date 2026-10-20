"""Step 19: direct checks of every link in the reduction of 4850 to a single condition.

 1. lambda_N(R3^T c) = lambda_N(c) at every character (N = e(4,0) + e(5,2)).
 2. lambda_4850(R3^T c) / lambda_4850(c) is a 63rd power wherever e(1,0) is nonzero at c and R3^T c.
 3. e(1,0)(j,k) = t_{(j+k)/2} t_{(j-k)/2} and R3 multiplies (j+k)/2 by 10 and (j-k)/2 by 26 (or
    the other way), with t_{10u} = t_u^(2^24), t_{26v} = t_v^(2^12), 63 | 2^12 - 1, 2^24 - 1.
 4. The tie groups of the 11 classes under R3 (with D4 and Frobenius).
 5. Class B: lambda_4850(1,2) = t_4 t_12 / t_18 exactly, and t_u^29127 = rho^((u/37)).
 6. Class C: lambda_4850(1,3) = eta / (t_1 t_2), eta = t_1 + t_4 + t_11 + t_12 + t_13 + t_17.
 7. Axis classes of 20982139 and 178279803: F(t, 0) factorisations (complete cyclotomic?).
 8. Independent check: examples/linear-atlas-3/eigen.py odd_part at m = 37 for the rules."""
import sys
import numpy as np
from rlib import *
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')

M = 37
L2 = {pow(2, e, M): e for e in range(36)}
def t(u):
    u %= M
    if u == 0:
        return 0
    return f18_pow(0b10, 2 ** L2[u])  # t_u = t_1^(2^L(u))

def lam(Fset, j, k):
    """lambda at the character (j, k), any j, k"""
    j, k = j % M, k % M
    if j == 0 and k == 0:
        raise ValueError
    if j == 0:
        j, k = k, 0
    kk = (k * pow(j, -1, M)) % M
    v = val_t1(Q_dickson(Fset, kk)) if kk else val_t1(subst_line(Fset, 0))
    return f18_pow(v, 2 ** L2[j])

def orbset(*orbs):
    out = set()
    for o in orbs:
        out ^= orbit_F(o)
    return frozenset(out)

N = orbset((4, 0), (5, 2))
F = rule_F(4850, 4)
E = orbset((1, 0))
R3 = (18, 29, 29, 18)  # symmetric, so R3^T = R3
def act(c):
    j, k = c
    return ((R3[0] * j + R3[2] * k) % M, (R3[1] * j + R3[3] * k) % M)

ok1 = ok2 = ok3 = True
for j in range(M):
    for k in range(M):
        if (j, k) == (0, 0):
            continue
        c2 = act((j, k))
        if lam(N, *c2) != lam(N, j, k):
            ok1 = False
        e1, e2 = lam(E, j, k), lam(E, *c2)
        if e1 and e2:
            r = f18_mul(lam(F, *c2), f18_pow(lam(F, j, k), N18 - 1))
            if f18_pow(r, N18 // 63) != 1:
                ok2 = False
        # 3. e(1,0) as a product
        h = pow(2, -1, M)
        if lam(E, j, k) != f18_mul(t((j + k) * h), t((j - k) * h)):
            ok3 = False
print('1. lambda_N invariant under R3 at all 1368 characters:', ok1)
print('2. lambda_4850(R3 c)/lambda_4850(c) a 63rd power wherever e(1,0) != 0 at c, R3 c:', ok2)
print('3. e(1,0)(j,k) = t_{(j+k)/2} t_{(j-k)/2}:', ok3,
      '; R3 (1,1) =', act((1, 1)), ' R3 (1,-1) =', act((1, M - 1)),
      '; L(10) =', L2[10], ' L(26) =', L2[26], '; (2^24-1) % 63 =', (2**24 - 1) % 63, ' (2^12-1) % 63 =', (2**12 - 1) % 63)

# 4. tie groups
CLASS_REPS = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
def cls(c):
    for i, (rj, rk) in enumerate(CLASS_REPS):
        for a in range(36):
            s = pow(2, a, M)
            for u, v in (((s * rj) % M, (s * rk) % M), ((s * rk) % M, (s * rj) % M)):
                for su in (1, -1):
                    for sv in (1, -1):
                        if ((su * u) % M, (sv * v) % M) == (c[0] % M, c[1] % M):
                            return i
ties = {}
for i, c in enumerate(CLASS_REPS):
    ties.setdefault(i, set()).add(cls(act(c)))
groups = []
seen = set()
for i in range(11):
    if i in seen:
        continue
    g = {i}
    frontier = [i]
    while frontier:
        x = frontier.pop()
        for y in ties[x] | {z for z in range(11) if x in ties[z]}:
            if y not in g:
                g.add(y)
                frontier.append(y)
    seen |= g
    groups.append(sorted(g))
print('4. tie groups under R3:', [[CLASS_REPS[i] for i in g] for g in groups])

# 5. class B
v12 = lam(F, 1, 2)
prod = f18_mul(f18_mul(t(4), t(12)), f18_pow(t(18), N18 - 1))
print('5. lambda_4850(1,2) == t_4 t_12 / t_18:', v12 == prod)
rho = None
leg = {u: (1 if pow(u, 18, M) == 1 else -1) for u in range(1, M)}
vals = {u: f18_pow(t(u), NINTH) for u in range(1, M)}
r_plus = {vals[u] for u in range(1, M) if leg[u] == 1}
r_minus = {vals[u] for u in range(1, M) if leg[u] == -1}
print('   t_u^29127 takes one value on residues and one on non-residues, of order 3:', len(r_plus) == 1 and len(r_minus) == 1,
      [f18_pow(x, 3) == 1 and x != 1 for x in r_plus | r_minus])
print('   Legendre sum (4) + (12) - (18) =', leg[4] + leg[12] - leg[18], '(= 0 mod 3: ninth power)')
# 6. class C
eta = t(1) ^ t(4) ^ t(11) ^ t(12) ^ t(13) ^ t(17)
print('6. N(1,3) == eta:', lam(N, 1, 3) == eta, '; lambda_4850(1,3) == eta/(t_1 t_2):',
      lam(F, 1, 3) == f18_mul(eta, f18_pow(f18_mul(t(1), t(2)), N18 - 1)), '; eta ninth power:', is_ninth(eta),
      '; t_1 t_2 ninth power:', is_ninth(f18_mul(t(1), t(2))))
# 7. axis classes
cyc = cyclo_table()
for n in (10491524, 20982139, 178279803):
    Fa = subst_line(rule_F(n, 6), 0)
    facs = factor2(Fa)
    print(f'7. axis of {n}: F(t,0) =', ' * '.join(f'({pstr(p)})^{e}' if e > 1 else f'({pstr(p)})' for p, e in facs),
          '| labels', [('T' if p == 2 else f'Psi{cyc.get(p)}') for p, e in facs], '| degrees of Psi_e:', [deg(psi(cyc[p])) if p in cyc and p != 2 and cyc[p] > 1 else 1 for p, e in facs])
# 8. independent eigenvalue check
import eigen as E8
for n, r in [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6)]:
    od = E8.odd_part(rule_points(n, r), 37)
    print(f'8. odd_part({n}, 37) = {od}; divides 29127: {29127 % od == 0}')
