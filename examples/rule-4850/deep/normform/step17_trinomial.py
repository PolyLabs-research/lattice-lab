"""Step 17: on the lines be = 2^d al, B = t_be = A^(2^d) (A = t_al), so with a = sigma(A)/A = A^63 (norm 1,
a primitive 1387th root of unity since A has order 87381 = 63 * 1387):
   f0(al, 2^d al) = 1 + X + Y,  X = a sigma(b) b,  Y = sigma(a) a b,  b = a^(2^d),  sigma = ^64.
 d=1: 1 + a^67 + a^131;  d=2: 1 + a^69 + a^261 (= t_11 t_14 t_17 / (t_1 t_4) at a = t_1^63).
Calibration: over ALL primitive 1387th roots a (72 Frobenius orbits), how often are these trinomials ninth
powers?  If about 1/9, the d = 1 condition is a 1-in-9 coincidence for the particular a = t_1^63."""
import json
import numpy as np
import nf

EXP, LOG = nf.tables()
NK = nf.NK
V = nf.V27()
T = nf.tvec()
A = T[1]
a0 = nf.kpow(A, 63)
assert nf.kpow(a0, 1387) == 1 and nf.kpow(a0, 73) != 1 and nf.kpow(a0, 19) != 1
def X_Y(a, d):
    b = nf.kpow(a, 1 << d)
    X = nf.kmul(nf.kmul(a, nf.kpow(b, 64)), b)
    Y = nf.kmul(nf.kmul(nf.kpow(a, 64), a), b)
    return X, Y
# check against f0 values
f0 = nf.vrule(24583649143032555859, 10) if False else None
for d in range(6):
    X, Y = X_Y(a0, d)
    val = 1 ^ X ^ Y
    # compare with W/pi at (1, 2^d)
    be = pow(2, d, 37)
    Wv = 0
    for u in (1, 10, 26):
        Wv ^= nf.kmul(T[u % 37], T[be * pow(u, -1, 37) % 37])
    assert val == nf.kmul(Wv, nf.kinv(nf.kmul(T[1], T[be]))), d
print('f0(1, 2^d) = 1 + X + Y with a = t_1^63 verified for d = 0..5')
# all primitive 1387th roots: g^(189 k), gcd(k, 1387) = 1
g1387 = nf.kpow(nf.gen(), NK // 1387)
res = {}
for d in range(6):
    seen = set(); ninth = 0; tot = 0; zero = 0
    for k in range(1, 1387):
        if k % 19 == 0 or k % 73 == 0:
            continue
        # Frobenius orbit representative: k * 2^i mod 1387
        rep = min(k * pow(2, i, 1387) % 1387 for i in range(18))
        if rep in seen:
            continue
        seen.add(rep)
        a = nf.kpow(g1387, rep)
        X, Y = X_Y(a, d)
        v = 1 ^ X ^ Y
        tot += 1
        if v == 0:
            zero += 1; continue
        ninth += (V[v] % 9 == 0)
    X, Y = X_Y(a0, d)
    mine = V[1 ^ X ^ Y]
    res[d] = dict(orbits=tot, ninth=int(ninth), zero=zero, rate=ninth / tot, at_t1=int(mine))
    print('d=%d: over %d orbits of primitive 1387th roots: ninth powers %d (rate %.3f), zeros %d;  at a = t_1^63: v27 = %d' % (d, tot, ninth, ninth / tot, zero, mine))
json.dump(res, open('step17_trinomial.json', 'w'), indent=1)
