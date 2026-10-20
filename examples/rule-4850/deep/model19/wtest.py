"""Is the 37-structure general?  For primes m = 1 mod 3 with cube root of unity w mod m, define
   W(alpha, beta) = sum_{u in {1, w, w^2}} t_{u alpha} t_{beta/u},   t_n = zeta^n + zeta^-n,
(at 37 this is the eigenvalue whose 4th power is 10491524 * t_alpha t_beta, i.e. 4850 * s in the diagonal frame).
Test, over all characters (alpha, beta) with alpha beta != 0: is W a cube?  is W * (t_alpha t_beta)^2 a ninth power?
(=> the analogue of 4850, (Hex + Hex^T)/s with the hexagon {+-(4,0), +-(2, +-2 sqrt(-3))}, would be ninth-confined.)"""
import sys, json, math
import sympy
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
from gf2 import Field

out = []
for m in sympy.primerange(7, 260):
    if m % 3 != 1:
        continue
    d = sympy.n_order(2, m)
    if d > 60:
        continue
    N = 2 ** d - 1
    if N % 3:
        continue
    Fd = Field(m)
    z = Fd.zeta
    zp = [1]
    for i in range(m - 1):
        zp.append(Fd.mul(zp[-1], z))
    t = [zp[i] ^ zp[(-i) % m] for i in range(m)]
    w = next(x for x in range(2, m) if pow(x, 3, m) == 1)
    U = [1, w, w * w % m]
    cube_W = True; ninth = True if N % 9 == 0 else None; zeros = 0; seen = set()
    for al in range(1, m):
        for be in range(1, m):
            if (al, be) in seen:
                continue
            c = (al, be)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            Wv = 0
            for u in U:
                Wv ^= Fd.mul(t[u * al % m], t[be * pow(u, -1, m) % m])
            if Wv == 0:
                zeros += 1; continue
            if Fd.pow(Wv, N // 3) != 1:
                cube_W = False
            if ninth is not None:
                th = Fd.mul(Wv, Fd.pow(Fd.mul(t[al], t[be]), 2))
                if Fd.pow(th, N // 9) != 1:
                    ninth = False
    two = {pow(2, e, m) for e in range(d)}
    rec = dict(m=m, d=d, minus1_in_2=(m - 1) in two, w_in_2=w in two, v3_of_N=sympy.multiplicity(3, N),
               W_zeros=zeros, W_cube=cube_W, W_s2_ninth=ninth)
    out.append(rec); print(rec, flush=True)
json.dump(out, open('wtest.json', 'w'), indent=1)
