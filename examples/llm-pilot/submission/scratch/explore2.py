import sys
sys.path.insert(0, "/home/user/pilot-sandbox/tools")
sys.path.insert(0, "/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad")
import gf2shim; print("shim", gf2shim.install())
from tori import torus, check_jordan, H1
from gf2 import Field
for m in [3, 5, 7, 9, 11, 13, 15, 21, 25]:
    F = Field(m); z = F.zeta
    # sanity: z has order exactly m
    assert F.pow(z, m) == 1 and all(F.pow(z, k) != 1 for k in range(1, m))
    T = torus(2*m, m, lambda d: (d[0] + 2*d[1], d[1]))
    psi1 = lambda w: F.pow(z, w[0] + w[1])
    psi2 = lambda w: F.pow(z, w[0] + w[1]) if w[0] % 2 == 0 else 0
    lam = F.sum(F.pow(z, e) for e in [1, -1, 2, -2, 3, -3])
    mu = F.sum(F.pow(z, e) for e in [1, -1, 2, -2])
    print(m, F.degree, check_jordan(T, H1, psi1, psi2, lam, mu, F))
