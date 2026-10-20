"""Are the new structures 37-specific?  At m in {37, 109, 185} (all with 2^18 = -1 mod m, so symmetric
eigenvalues lie in F(2^18) and Frob^6 is the dilation by 64 mod m) test, for 4850 and its rotation
10491524, using an independent field implementation (pilot tools' gf2.Field(m), F(2^36)):
  ninth : all nonzero eigenvalues ninth powers
  P0    : v27(lambda(Dc)) = v27(lambda(c)),  D = partial dilation by 64 (diagonal frame for 4850,
          standard frame for 10491524)
  (I)   : G(Mc)/G(c) in F(2^9),  M = diag(64, 1/64) in the frame, G = f * (frame multiplier)
"""
import sys, math
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
from gf2 import Field

ORB4850 = [(1, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 3), (4, 2)]


def orbits(radius):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def rule_orbits(n, radius):
    return [o for i, o in enumerate(orbits(radius)) if n >> i & 1]


def study(m, n, radius, frame):
    Fd = Field(m)
    N36 = Fd.order
    assert Fd.degree == 36 and pow(2, 18, m) == m - 1
    z = Fd.zeta
    zp = [1]
    for i in range(m - 1):
        zp.append(Fd.mul(zp[-1], z))
    t = [zp[i] ^ zp[(-i) % m] for i in range(m)]
    orbs = rule_orbits(n, radius)

    def lam(j, k):
        v = 0
        for a, b in orbs:
            if a == 0 and b == 0:
                v ^= 1
            elif b == 0:
                v ^= t[a * j % m] ^ t[a * k % m]
            elif a == b:
                v ^= Fd.mul(t[a * j % m], t[a * k % m])
            else:
                v ^= Fd.mul(t[a * j % m], t[b * k % m]) ^ Fd.mul(t[b * j % m], t[a * k % m])
        return v

    # primitive 27th root for v27
    g27 = None
    for cand in range(2, 400):
        w = Fd.pow(cand, N36 // 27)
        if Fd.pow(w, 9) != 1:
            g27 = w; break
    tab27 = {}
    x = 1
    for i in range(27):
        tab27[x] = i; x = Fd.mul(x, g27)
    # Frobenius orbit reps
    rep = {}
    reps = []
    for j in range(m):
        for k in range(m):
            if (j, k) in rep or (j, k) == (0, 0):
                continue
            c = (j, k); i = 0
            while c not in rep:
                rep[c] = ((j, k), i)
                c = (2 * c[0] % m, 2 * c[1] % m); i += 1
            reps.append((j, k))
    val = {r: lam(*r) for r in reps}
    v27r = {r: (None if val[r] == 0 else tab27[Fd.pow(val[r], N36 // 27)]) for r in reps}

    def v27(c):
        r, i = rep[(c[0] % m, c[1] % m)]
        return None if v27r[r] is None else v27r[r] * pow(2, i, 27) % 27

    def value(c):
        r, i = rep[(c[0] % m, c[1] % m)]
        return Fd.pow(val[r], 2 ** i)

    ninth = all(v27r[r] is None or v27r[r] % 9 == 0 for r in reps)
    u = 64 % m; ui = pow(u, -1, m); h = pow(2, -1, m)
    if frame == 'diag':
        # c = alpha(1,1) + beta(1,-1);  D: alpha -> u alpha;  M: alpha -> u alpha, beta -> beta/u
        def D(c):
            al, be = (c[0] + c[1]) * h % m, (c[0] - c[1]) * h % m
            al = u * al
            return ((al + be) % m, (al - be) % m)
        def Mm(c):
            al, be = (c[0] + c[1]) * h % m, (c[0] - c[1]) * h % m
            al, be = u * al, ui * be
            return ((al + be) % m, (al - be) % m)
        mult = lambda c: t[c[0] % m] ^ t[c[1] % m]          # s = a + b
    else:
        D = lambda c: (u * c[0] % m, c[1])
        Mm = lambda c: (u * c[0] % m, ui * c[1] % m)
        mult = lambda c: Fd.mul(t[c[0] % m], t[c[1] % m])  # P = ab
    p0 = True; I_ok = True; checked = 0
    for r in reps:
        if r[0] == 0 or r[1] == 0:
            continue
        a, b = v27(r), v27(D(r))
        if a is not None and b is not None and a != b:
            p0 = False
        g1 = Fd.mul(val[r], mult(r)); c2 = Mm(r); g2 = Fd.mul(value(c2), mult(c2))
        if g1 and g2:
            checked += 1
            # g2/g1 in F(2^9)  <=>  g2 * g1^512 == g1 * g2^512
            if Fd.mul(g2, Fd.pow(g1, 512)) != Fd.mul(g1, Fd.pow(g2, 512)):
                I_ok = False
    return dict(m=m, rule=n, frame=frame, orbits=len(reps), ninth=ninth, P0=p0, I=I_ok, I_checked=checked)


if __name__ == '__main__':
    import json
    out = []
    for m in (37, 109, 185):
        for n, r, fr in ((4850, 4, 'diag'), (10491524, 6, 'std')):
            res = study(m, n, r, fr)
            out.append(res)
            print(res, flush=True)
    json.dump(out, open('sizes.json', 'w'), indent=1)
