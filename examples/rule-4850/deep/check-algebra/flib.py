"""check-algebra field library (verifier's own construction).

F(2^d), d = ord_p(2), is built as F2[x]/(M) with M an irreducible factor of the cyclotomic polynomial Phi_p over F2
(sympy factor_list mod 2, irreducibility re-checked here by a Rabin test), and zeta = x mod M.  So no search for
an element of order p is needed: zeta has order p by construction.  Elements are int bitmasks.
Norms are computed from the definition N_{K/k}(z) = z^((|K|-1)/(|k|-1)) = z^(1 + q + q^2), q = |k| = 2^(e/3).
"""
import sympy as sp


def ordmod(a, m):
    x, k = a % m, 1
    while x != 1:
        x = x * a % m
        k += 1
    return k


def pmod(a, m):
    dm = m.bit_length()
    while a and a.bit_length() >= dm:
        a ^= m << (a.bit_length() - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def prime_factors(n):
    out, q = [], 2
    while q * q <= n:
        if n % q == 0:
            out.append(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        out.append(n)
    return out


def rabin_irreducible(M):
    n = M.bit_length() - 1

    def x2k(k):
        r = 2
        for _ in range(k):
            r = pmod(clmul(r, r), M)
        return r
    if x2k(n) != 2:
        return False
    return all(pgcd(x2k(n // q) ^ 2, M) == 1 for q in prime_factors(n))


def cyclotomic_factor(p):
    x = sp.symbols('x')
    fl = sp.Poly(sum(x ** i for i in range(p)), x, modulus=2).factor_list()[1]
    d = ordmod(2, p)
    for f, mult in fl:
        assert f.degree() == d and mult == 1
    f = fl[0][0]
    coeffs = [int(c) % 2 for c in f.all_coeffs()]  # high to low
    M = 0
    for c in coeffs:
        M = (M << 1) | c
    assert rabin_irreducible(M)
    return M, len(fl)


class Field:
    def __init__(self, p):
        self.p = p
        self.d = ordmod(2, p)
        self.M, self.nfactors = cyclotomic_factor(p)
        assert self.M.bit_length() - 1 == self.d
        self.order = (1 << self.d) - 1
        self.zeta = pmod(2, self.M)  # x
        self.zp = [1]
        for _ in range(p - 1):
            self.zp.append(self.mul(self.zp[-1], self.zeta))
        assert self.mul(self.zp[-1], self.zeta) == 1 and self.zeta != 1

    def mul(self, a, b):
        return pmod(clmul(a, b), self.M)

    def pow(self, a, n):
        r = 1
        while n:
            if n & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            n >>= 1
        return r

    def inv(self, a):
        assert a
        return self.pow(a, self.order - 1)

    def frob(self, a, k):
        for _ in range(k):
            a = self.mul(a, a)
        return a

    def z(self, j):
        return self.zp[j % self.p]

    def t(self, j):
        return self.z(j) ^ self.z(-j)

    def mu(self, n):
        return [u for u in range(1, self.p) if pow(u, n, self.p) == 1]

    def eta(self, x, mu6=None):
        mu6 = mu6 or self.mu(6)
        v = 0
        for u in mu6:
            v ^= self.z(x * u)
        return v
