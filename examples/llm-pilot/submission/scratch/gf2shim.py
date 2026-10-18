import sys, types, random

def pmod(a, b):
    db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        a ^= b << (a.bit_length() - 1 - db)
    return a

def pmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r

def pdivmod(a, b):
    q = 0; db = b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        s = a.bit_length() - 1 - db
        q ^= 1 << s; a ^= b << s
    return q, a

def pgcd(a, b):
    while b: a, b = b, pmod(a, b)
    return a

def cyclotomic_gf2(m):
    # Phi_m over Z via division of x^m - 1 by Phi_k, k | m, k < m; then reduce mod 2.
    def zdiv(a, b):  # integer polys as lists, low degree first, exact division
        a = a[:]; q = [0] * (len(a) - len(b) + 1)
        for i in range(len(q) - 1, -1, -1):
            c = a[i + len(b) - 1] // b[-1]; q[i] = c
            for j, bj in enumerate(b): a[i + j] -= c * bj
        assert all(x == 0 for x in a)
        return q
    phi = {}
    for k in range(1, m + 1):
        if m % k: continue
        p = [-1] + [0] * (k - 1) + [1]
        for j in range(1, k):
            if k % j == 0: p = zdiv(p, phi[j])
        phi[k] = p
    return sum((c % 2) << i for i, c in enumerate(phi[m]))

def ord2(m):
    d, x = 1, 2 % m
    while x != 1 % m: x = x * 2 % m; d += 1
    return d

def modulus(m):
    f = cyclotomic_gf2(m); d = ord2(m)
    rng = random.Random(m)
    stack, out = [f], []
    while stack:
        g = stack.pop()
        if g.bit_length() - 1 == d: out.append(g); continue
        while True:
            a = rng.randrange(2, 1 << (g.bit_length() - 1))
            t, s = 0, a
            for _ in range(d):
                t ^= s; s = pmod(pmul(s, s), g)
            h = pgcd(g, t)
            if 0 < h.bit_length() - 1 < g.bit_length() - 1:
                stack += [h, pdivmod(g, h)[0]]; break
    return min(out)

def install():
    try:
        import sympy  # noqa: F401
        return False
    except ModuleNotFoundError:
        sys.modules["sympy"] = types.ModuleType("sympy")
        import gf2
        gf2._modulus = modulus
        return True
