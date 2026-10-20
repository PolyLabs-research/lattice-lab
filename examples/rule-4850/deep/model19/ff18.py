"""F(2^18) for the 19-model study of rule 4850 at m = 37.

Model: F(2^18) = F2[x]/(x^18 + x^9 + 1) = F2(zeta27), x = zeta27 (Phi_27 is irreducible, ord_27(2) = 18).
Elements are ints < 2^18 in the polynomial basis.  Log/exp tables (numpy) w.r.t. a generator g.

Inside this one field we locate
  zeta27 = x,  zeta19 (a root of Phi_19),  t_1 (a root of Q37, the min. poly of zeta37 + 1/zeta37),
and decompose F(2^18)* = F(2^9)* x mu27 x mu19 (orders 511, 27, 19).
"""
from __future__ import annotations
import functools
import numpy as np

DEG = 18
MODP = (1 << 18) | (1 << 9) | 1      # Phi_27
N = (1 << 18) - 1                    # 262143 = 3^3 7 19 73


def mul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> DEG & 1:
            a ^= MODP
    return r


def pw(a: int, e: int) -> int:
    r = 1
    e %= N
    while e:
        if e & 1:
            r = mul(r, a)
        a, e = mul(a, a), e >> 1
    return r


@functools.cache
def gen() -> int:
    for g in range(2, 1 << 18):
        if all(pw(g, N // p) != 1 for p in (3, 7, 19, 73)):
            return g


@functools.cache
def tables():
    g = gen()
    EXP = np.zeros(2 * N + 2, dtype=np.int64)
    LOG = np.full(1 << 18, -1, dtype=np.int64)
    x = 1
    for e in range(N):
        EXP[e] = x
        LOG[x] = e
        x = mul(x, g)
    EXP[N:2 * N] = EXP[:N]
    return EXP, LOG


def log(a):
    EXP, LOG = tables()
    return LOG[a]


def exp(e):
    EXP, LOG = tables()
    return EXP[np.asarray(e) % N]


def vmul(a, b):
    """vectorised multiplication of int arrays."""
    EXP, LOG = tables()
    a = np.asarray(a); b = np.asarray(b)
    out = EXP[(LOG[a] + LOG[b]) % N]
    return np.where((a == 0) | (b == 0), 0, out)


def vpow(a, e):
    EXP, LOG = tables()
    a = np.asarray(a)
    out = EXP[(LOG[a] * (np.asarray(e) % N)) % N]
    return np.where(a == 0, 0, out)


def inv(a):
    return pw(a, N - 1)


def frob(a, i=1):
    return pw(a, 2 ** (i % 18))


# --- component projections  F(2^18)* = F(2^9)* x mu27 x mu19 ---------------------------
# e511 = 1 mod 511, 0 mod 513 ; e27 = 1 mod 27, 0 mod 9709 ; e19 = 1 mod 19, 0 mod 13797
E511 = (513 * pow(513, -1, 511)) % N
E27 = (9709 * pow(9709, -1, 27)) % N
E19 = (13797 * pow(13797, -1, 19)) % N
assert (E511 + E27 + E19) % N == 1


def comps(a):
    """(alpha in F(2^9)*, omega in mu27, z in mu19) with a = alpha*omega*z."""
    return pw(a, E511), pw(a, E27), pw(a, E19)


@functools.cache
def zeta27() -> int:
    return 2


@functools.cache
def mu27_log_table():
    z = zeta27(); d = {}; x = 1
    for i in range(27):
        d[x] = i; x = mul(x, z)
    return d


def v27(a) -> int:
    """v(a) in Z/27: mu27-component of a equals zeta27^v.  a is a ninth power iff v = 0 mod 9."""
    return mu27_log_table()[pw(a, E27)]


# --- polynomials over F2 as int bitmasks ----------------------------------------------
def poly_eval(coeffs_mask: int, a: int) -> int:
    """evaluate F2-polynomial (bitmask, bit i = coeff of T^i) at a."""
    r = 0
    for i in range(coeffs_mask.bit_length() - 1, -1, -1):
        r = mul(r, a)
        if coeffs_mask >> i & 1:
            r ^= 1
    return r


def vpoly_eval(coeffs_mask: int, A):
    r = np.zeros_like(A)
    for i in range(coeffs_mask.bit_length() - 1, -1, -1):
        r = vmul(r, A)
        if coeffs_mask >> i & 1:
            r = r ^ 1
    return r


def pmul2(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1; b >>= 1
    return r


@functools.cache
def Q37() -> int:
    """min. poly over F2 of zeta37 + 1/zeta37: Phi37(x) = x^18 Q(x + 1/x); Q = 1 + sum_{n=1}^{18} D_n(T)."""
    D = [0, 0b10]  # D_0 = 2 = 0, D_1 = T
    for n in range(1, 18):
        D.append(pmul2(0b10, D[n]) ^ D[n - 1])
    q = 1
    for n in range(1, 19):
        q ^= D[n]
    return q


@functools.cache
def t_roots():
    A = np.arange(1 << 18, dtype=np.int64)
    vals = vpoly_eval(Q37(), A)
    return [int(a) for a in np.nonzero(vals == 0)[0]]


@functools.cache
def t1() -> int:
    """a fixed root t_1 of Q37: the 37-model generator t = zeta37 + 1/zeta37."""
    return min(t_roots())


def ind37(j: int) -> int:
    j %= 37
    x = 1
    for e in range(36):
        if x == j:
            return e
        x = 2 * x % 37
    raise ValueError(j)


@functools.cache
def tvec():
    """t_j for j = 0..36 (t_0 = 0), t_{2^e} = t_1^(2^e)."""
    out = [0] * 37
    for j in range(1, 37):
        out[j] = frob(t1(), ind37(j))
    return tuple(out)


@functools.cache
def zeta19() -> int:
    """canonical zeta19 := the mu19-component of t_1 (checked to be != 1)."""
    z = pw(t1(), E19)
    assert z != 1 and pw(z, 19) == 1
    return z


@functools.cache
def z19pows():
    z = zeta19(); out = [1]
    for i in range(18):
        out.append(mul(out[-1], z))
    return tuple(out)


@functools.cache
def _nb19():
    """Gaussian elimination data for coordinates in the normal basis zeta19^1..zeta19^18."""
    basis = list(z19pows()[1:19])
    return _elim(basis)


def _elim(basis):
    piv = []  # (pivot bit, vector, tag)
    for i, b in enumerate(basis):
        tag = 1 << i
        for pb, pv, pt in piv:
            if b >> pb & 1:
                b ^= pv; tag ^= pt
        assert b, "dependent"
        p = b.bit_length() - 1
        # reduce others
        newpiv = []
        for pb, pv, pt in piv:
            if pv >> p & 1:
                pv ^= b; pt ^= tag
            newpiv.append((pb, pv, pt))
        piv = newpiv + [(p, b, tag)]
    return piv


def _coords(piv, v: int):
    tag = 0
    for pb, pv, pt in piv:
        if v >> pb & 1:
            v ^= pv; tag ^= pt
    assert v == 0
    return tag


def nb19(v: int):
    """support S in {1..18}: v = sum_{i in S} zeta19^i."""
    tag = _coords(_nb19(), v)
    return [i + 1 for i in range(18) if tag >> i & 1]


@functools.cache
def _nb37():
    return _elim([tvec()[j] for j in range(1, 19)])


def nb37(v: int):
    """support S in {1..18}: v = sum_{j in S} t_j  (type II optimal normal basis)."""
    tag = _coords(_nb37(), v)
    return [i + 1 for i in range(18) if tag >> i & 1]


def poly27(v: int):
    """support in polynomial basis zeta27^0..zeta27^17."""
    return [i for i in range(18) if v >> i & 1]


def from_nb19(S) -> int:
    v = 0
    for i in S:
        v ^= z19pows()[i % 19]
    return v


def from_nb37(S) -> int:
    v = 0
    for j in S:
        v ^= tvec()[j % 37]
    return v


def in_F512(a: int) -> bool:
    return pw(a, 512) == a


# Gauss periods of index 2 (both are primitive cube roots of 1)
@functools.cache
def eta19():
    QR = sorted({i * i % 19 for i in range(1, 19)})
    return from_nb19(QR)


@functools.cache
def eta37():
    QR = sorted({i * i % 37 for i in range(1, 37)})
    # sum over QR of zeta37^a = sum over QR/{+-1} of t_a (QR is closed under -1 since 37 = 1 mod 4)
    return from_nb37([a for a in QR if a <= 18])


# --- rule values -----------------------------------------------------------------------
def orbit_value(o, j, k, T=None):
    T = T or tvec()
    a, b = o
    if a == 0 and b == 0:
        return 1
    if b == 0:
        return T[a * j % 37] ^ T[a * k % 37]
    if a == b:
        return mul(T[a * j % 37], T[a * k % 37])
    return mul(T[a * j % 37], T[b * k % 37]) ^ mul(T[b * j % 37], T[a * k % 37])


def orbits(radius):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def rule_orbits(n, radius):
    return [o for i, o in enumerate(orbits(radius)) if n >> i & 1]


def rule_value(n, radius, j, k):
    v = 0
    for o in rule_orbits(n, radius):
        v ^= orbit_value(o, j, k)
    return v


CLASSES = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
