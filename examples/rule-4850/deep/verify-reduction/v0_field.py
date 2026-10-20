"""v0: sanity of the independent field model."""
import time, random
import vlib as V
t0 = time.time()
print('Phi37 irreducible over F2 (Rabin):', V.rabin_irreducible())
print('zeta^37 = 1:', V.power(2, 37) == 1, ' zeta != 1:', V.ZETA[1] != 1)
print('MU3', V.MU3, 'MU6', V.MU6, 'MU12', V.MU12)
print('2^9 mod 37 =', pow(2, 9, 37), ' 2^6 =', pow(2, 6, 37), ' 2^12 =', pow(2, 12, 37), ' 2^24 =', pow(2, 24, 37))
w = V.omega(); print('omega order 27:', V.power(w, 27) == 1 and V.power(w, 9) != 1, ' omega in K:', V.in_K(w))
# res is a homomorphism: res(ab) = res(a)+res(b); res(a^9) = 9 res(a)
random.seed(1)
ok = True
for _ in range(200):
    a = V.power(random.randrange(1, 1 << 36), (1 << 18) + 1)   # random element of K
    b = V.power(random.randrange(1, 1 << 36), (1 << 18) + 1)
    if a == 0 or b == 0: continue
    ok &= V.in_K(a) and V.res(V.mul(a, b)) == (V.res(a) + V.res(b)) % 27
    ok &= V.res(V.power(a, 9)) == 9 * V.res(a) % 27
    ok &= V.res(V.frob(a, 1)) == 2 * V.res(a) % 27
print('res homomorphic, Frobenius-equivariant on 200 random elements of K:', ok)
# t_j in K, cube, not ninth power; Legendre pattern
rs = {j: V.res(V.t(j)) for j in range(1, 37)}
print('t_j in K:', all(V.in_K(V.t(j)) for j in range(1, 37)))
print('res(t_j) mod 9:', sorted({(V.legendre(j), rs[j] % 9) for j in rs}))
print('time', round(time.time() - t0, 2))
