"""Partial norm of 10491524: Nx(alpha, beta) = prod_{h in 1,27,26} lambda'(h alpha, beta).
Claim (P1 & P2): B = Nx * c19(t_beta)^3 lies in F(2^9).  Look at B's structure."""
import ff18 as F
from partialnorm2 import lamfun
T = F.tvec()
for n, r in [(10491524, 6), (20982139, 6), (178279803, 6)]:
    L = lamfun(n, r)
    allreal = True
    Bs = {}
    for al in range(1, 19):
        for be in range(1, 19):
            v = 1
            for h in (1, 27, 26):
                v = F.mul(v, L(h * al, be))
            Bv = F.mul(v, F.pw(F.pw(T[be], 3), F.E19))
            if not F.in_F512(Bv):
                allreal = False
            Bs[(al, be)] = Bv
    # dependence: on beta only? on alpha's H-class only?
    dep_beta = all(Bs[(al, be)] == Bs[(1, be)] for al in range(1, 19) for be in range(1, 19))
    print(n, 'B in F(2^9) everywhere:', allreal, ' B depends on beta only:', dep_beta)
    # B in t-basis for a few
    for be in (1, 2, 3):
        print('   beta=%d:' % be, [F.nb37(Bs[(al, be)]) for al in (1, 2, 3)])
    # compare B for the three rules
    if n == 10491524:
        B0 = Bs
    else:
        same = all(Bs[k] == B0[k] for k in Bs)
        ratio_real = all(F.in_F512(F.mul(Bs[k], F.inv(B0[k]))) for k in Bs)
        print('   B equal to 10491524 B:', same)
