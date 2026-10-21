"""check-chain c5: step (3) is stated with theta (index-3 period theta(x) = eta(x) + eta(8x)) in the task text and in
norms/s9, but the F2[x] certificate yields the eta form (eta(al) eta(be))^(4n-2).  The two agree iff
(eta/theta)^(4n-2) = 1, which follows from eta = theta * rho (rho(x) = eta(x)+eta(4x)+eta(16x) in F4) and 3 | 4n-2.
Check eta = theta * rho (a) exactly in F2[Z/37] modulo J = sum_i x^i, (b) in our field; and the theta form of
N(lambda_4850) at all off-diagonal characters."""
import json
import functools
import clib
from clib import p

F = clib.GF36()
z = [F.pow(F.zeta, i) for i in range(p)]
mu6 = clib.mu(6)
L2 = clib.LOG2
def eset(x):
    return {x * u % p for u in mu6}
eta_s = lambda x: eset(x)
theta_s = lambda x: eset(x) ^ eset(8 * x)
rho_s = lambda x: eset(x) ^ eset(4 * x) ^ eset(16 * x)
def gmul(A, B):
    o = set()
    for i in A:
        for j in B:
            o ^= {(i + j) % p}
    return o
J = set(range(p))
exact = all(gmul(theta_s(x), rho_s(x)) in (eta_s(x), eta_s(x) ^ J) for x in range(1, p))
val = lambda S: functools.reduce(lambda a, b: a ^ b, (z[i] for i in S), 0)
field = all(F.mul(val(theta_s(x)), val(rho_s(x))) == val(eta_s(x)) for x in range(1, p))
rho_in_F4 = all(F.in_sub(val(rho_s(x)), 2) for x in range(1, p))
theta_in_F8 = all(F.in_sub(val(theta_s(x)), 3) for x in range(1, p))
n_claim = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
pts = clib.rule_points(clib.RULE4850_ORBITS)
h = pow(2, -1, p)
bad = 0
for j in range(p):
    for k in range(p):
        al, be = (j + k) * h % p, (j - k) * h % p
        if not (al and be):
            continue
        L = 0
        for a, b in pts:
            L ^= z[(a * j + b * k) % p]
        d = (L2[be] - L2[al]) % 6
        TT = F.mul(val(theta_s(al)), val(theta_s(be)))
        if F.norm_K_k(L) != F.pow(TT, 2 * (2 * n_claim[d] - 1)):
            bad += 1
out = {'eta = theta*rho exactly in F2[Z/37]/(J)': exact, 'eta = theta*rho in field': field,
       'rho in F4': rho_in_F4, 'theta in F8': theta_in_F8,
       'N(lambda) = (theta theta)^(2(2n-1)) failures (off-diagonal)': bad}
json.dump(out, open('c5_theta_form.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
