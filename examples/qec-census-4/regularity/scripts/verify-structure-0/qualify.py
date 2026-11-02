"""Independent check of which odd e <= 199 'qualify': exists zeta in mu_e (over GF(2)-bar)
with zeta != 1 and 1 + zeta in mu_e.

Method A (primary): build GF(2^t), t = ord_e(2), by a random irreducible polynomial (Rabin test);
find h of exact order e; enumerate mu_e = {h^i}; test (1 + h^i)^e == 1.
Method B (cross-check): gcd(x^e + 1, (x+1)^e + 1) over GF(2) by bit-polynomials.
"""
import random, math, json, sys

random.seed(12345)


def deg(a):
    return a.bit_length() - 1


def pmod(a, f):
    df = deg(f)
    while a and deg(a) >= df:
        a ^= f << (deg(a) - df)
    return a


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1; b >>= 1
    return r


def mulmod(a, b, f):
    return pmod(pmul(a, b), f)


def powmod(a, n, f):
    r = 1; a = pmod(a, f)
    while n:
        if n & 1:
            r = mulmod(r, a, f)
        a = mulmod(a, a, f); n >>= 1
    return r


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def primes_of(n):
    ps, p = [], 2
    while p * p <= n:
        if n % p == 0:
            ps.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        ps.append(n)
    return ps


def irreducible(f):
    t = deg(f)
    x = 2
    # x^(2^t) == x mod f
    y = x
    for _ in range(t):
        y = mulmod(y, y, f)
    if y != pmod(x, f):
        return False
    for q in primes_of(t):
        y = x
        for _ in range(t // q):
            y = mulmod(y, y, f)
        if pgcd(f, y ^ x) != 1:
            return False
    return True


def rand_irred(t):
    while True:
        f = (1 << t) | random.getrandbits(t) | 1
        if irreducible(f):
            return f


def order2(e):
    t, v = 1, 2 % e
    while v != 1:
        v = v * 2 % e; t += 1
    return t


def qualifies_field(e):
    t = order2(e)
    f = rand_irred(t)
    N = (1 << t) - 1
    assert N % e == 0
    ps = primes_of(e)
    while True:
        g = random.getrandbits(t) or 1
        h = powmod(g, N // e, f)
        if all(powmod(h, e // p, f) != 1 for p in ps):
            break
    sols = []
    z = 1
    for i in range(1, e):
        z = mulmod(z, h, f)
        if powmod(z ^ 1, e, f) == 1:  # 1 + zeta in mu_e
            sols.append(i)
    return len(sols) > 0, len(sols), t


def qualifies_gcd(e):
    xe1 = (1 << e) | 1
    # (x+1)^e + 1
    p = 1
    for _ in range(e):
        p = pmul(p, 0b11)
    return pgcd(xe1, p ^ 1) != 1


if __name__ == "__main__":
    out = {}
    for e in range(3, 200, 2):
        qa, ns, t = qualifies_field(e)
        qb = qualifies_gcd(e)
        assert qa == qb, (e, qa, qb)
        out[e] = {"qualifies": qa, "num_zeta": ns, "t": t}
    Q = [e for e in out if out[e]["qualifies"]]
    minimal = [e for e in Q if not any(e % f == 0 for f in Q if f < e)]
    print("qualifying odd e <= 199:", Q)
    print("minimal qualifying:", minimal)
    claimed = (3, 7, 31, 73, 85, 127)
    pred = [e for e in range(3, 200, 2) if any(e % c == 0 for c in claimed)]
    print("matches 'divisible by 3,7,31,73,85,127':", pred == Q)
    print("diff:", sorted(set(pred) ^ set(Q)))
    for e in minimal:
        print(f"  e={e} t=ord_e(2)={out[e]['t']} #zeta={out[e]['num_zeta']}")
    for e in (5, 17, 89, 151, 23, 43, 127):
        print("  e=%d t=%d qualifies=%s #zeta=%d" % (e, out[e]["t"], out[e]["qualifies"], out[e]["num_zeta"]))
    json.dump(out, open(sys.argv[1], "w"))
