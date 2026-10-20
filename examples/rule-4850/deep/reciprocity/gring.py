"""Group ring F_2[Z_37^2] helpers: elements as 37x37 uint8 arrays (index [x-exponent, y-exponent])."""
import numpy as np
M = 37

def elem(points):
    a = np.zeros((M, M), dtype=np.uint8)
    for p, q in points:
        a[p % M, q % M] ^= 1
    return a

def mul(a, b):
    out = np.zeros((M, M), dtype=np.uint8)
    for p, q in zip(*np.nonzero(a)):
        out ^= np.roll(np.roll(b, p, axis=0), q, axis=1)
    return out

def dil(a, d):
    """a(x^d, y^d)"""
    out = np.zeros((M, M), dtype=np.uint8)
    for p, q in zip(*np.nonzero(a)):
        out[(d * p) % M, (d * q) % M] ^= 1
    return out

def power(a, e):
    r = elem([(0, 0)])
    base = a.copy()
    while e:
        if e & 1:
            r = mul(r, base)
        e >>= 1
        if e:
            base = dil(base, 2)  # squaring = Frobenius = dilation by 2
    return r

def norm10(a):
    """N(a) = a * a(x^10, y^10) * a(x^26, y^26): the norm over <[10]> (order 3)"""
    return mul(mul(a, dil(a, 10)), dil(a, 26))
