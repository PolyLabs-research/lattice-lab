"""
Core library for the reciprocity angle on rule 4850 at m = 37.

Conventions
- GF(2)[T] polynomials are Python ints (bit i = coefficient of T^i).
- F_64 = GF(2)[w]/(w^6 + w + 1); elements are ints 0..63, w = 2 is a primitive element.
- Polynomials over F_64 are tuples/lists of ints, low degree first, no trailing zeros.
- F(2^18) = GF(2)[X]/(m37(X)) with m37 the minimal polynomial of t_1 = zeta + 1/zeta (degree 18);
  so t_1 = X = 0b10 in this representation.
- A symmetric rule f(x, y) = F(a, b), a = x + 1/x, b = y + 1/y; F is a set of monomials (i, j).
"""
from __future__ import annotations

import functools
import random

# ----------------------------------------------------------------------------- GF(2)[T]


def deg(a: int) -> int:
    return a.bit_length() - 1


def sq2(a: int) -> int:
    """a(T)^2 over GF(2): spread the bits."""
    if a == 0:
        return 0
    return int('0'.join(bin(a)[2:]), 2)


def clmul(a: int, b: int) -> int:
    if a.bit_length() < b.bit_length():
        a, b = b, a
    r = 0
    i = 0
    while b:
        if b & 1:
            r ^= a << i
        b >>= 1
        i += 1
    return r


def pmod(a: int, m: int) -> int:
    dm = deg(m)
    while a and deg(a) >= dm:
        a ^= m << (deg(a) - dm)
    return a


def pdivmod(a: int, m: int):
    dm = deg(m)
    q = 0
    while a and deg(a) >= dm:
        s = deg(a) - dm
        q ^= 1 << s
        a ^= m << s
    return q, a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def pmulmod(a: int, b: int, m: int) -> int:
    return pmod(clmul(a, b), m)


def ppowmod(a: int, e: int, m: int) -> int:
    r = 1
    a = pmod(a, m)
    while e:
        if e & 1:
            r = pmulmod(r, a, m)
        e >>= 1
        if e:
            a = pmod(sq2(a), m)
    return r


def pderiv(a: int) -> int:
    # derivative over GF(2): keep odd-degree coefficients, shifted down
    r = 0
    i = 1
    a >>= 1
    while a:
        if a & 1:
            r |= 1 << (i - 1)
        a >>= 2
        i += 2
    return r


def psqrt(a: int) -> int:
    """square root of a polynomial with only even exponents"""
    r, i = 0, 0
    while a >> (2 * i):
        if a >> (2 * i) & 1:
            r |= 1 << i
        assert not (a >> (2 * i + 1) & 1)
        i += 1
    return r


def _sqfree(f: int):
    """square-free decomposition over GF(2): list of (g, e) with f = prod g^e, g square-free."""
    out = []

    def rec(f, mult):
        if deg(f) <= 0:
            return
        d = pderiv(f)
        if d == 0:
            rec(psqrt(f), 2 * mult)
            return
        c = pgcd(f, d)
        w = pdivmod(f, c)[0]
        i = 1
        while deg(w) > 0:
            y = pgcd(w, c)
            z = pdivmod(w, y)[0]
            if deg(z) > 0:
                out.append((z, i * mult))
            i += 1
            w = y
            c = pdivmod(c, y)[0]
        if deg(c) > 0:
            rec(psqrt(c), 2 * mult)

    rec(f, 1)
    return out


def _ddf(f: int):
    """distinct-degree factorisation of a square-free f: list of (product, degree)."""
    out = []
    h = 0b10
    d = 0
    while deg(f) >= 2 * (d + 1):
        d += 1
        h = pmod(sq2(h), f)
        g = pgcd(h ^ 0b10, f)
        if g != 1:
            out.append((g, d))
            f = pdivmod(f, g)[0]
            h = pmod(h, f)
    if deg(f) > 0:
        out.append((f, deg(f)))
    return out


def _edf(f: int, d: int, rng):
    """equal-degree factorisation over GF(2) (trace map)."""
    if deg(f) == d:
        return [f]
    while True:
        r = rng.getrandbits(deg(f)) | 1
        r = pmod(r, f)
        t = r
        s = r
        for _ in range(d - 1):
            s = pmod(sq2(s), f)
            t ^= s
        g = pgcd(t, f)
        if 0 < deg(g) < deg(f):
            return _edf(g, d, rng) + _edf(pdivmod(f, g)[0], d, rng)


def factor2(f: int):
    """factor f over GF(2): sorted list of (irreducible, multiplicity)."""
    assert f
    rng = random.Random(12345)
    out = {}
    # strip powers of T first
    v = 0
    while not (f >> v) & 1:
        v += 1
    if v:
        out[0b10] = v
        f >>= v
    for g, e in _sqfree(f):
        for h, d in _ddf(g):
            for p in _edf(h, d, rng):
                out[p] = out.get(p, 0) + e
    return sorted(out.items(), key=lambda pe: (deg(pe[0]), pe[0]))


def pstr(a: int, var='T') -> str:
    if a == 0:
        return '0'
    terms = []
    for i in range(deg(a), -1, -1):
        if a >> i & 1:
            terms.append('1' if i == 0 else (var if i == 1 else f'{var}^{i}'))
    return ' + '.join(terms)


# ----------------------------------------------------------------------------- Dickson, Psi

@functools.cache
def dickson(n: int) -> int:
    """D_n(t) with x^n + x^-n = D_n(x + 1/x); D_0 = 0 (it is 2)."""
    if n == 0:
        return 0
    a, b = 0, 0b10  # D_0 (=0 in char 2), D_1
    for _ in range(n - 1):
        a, b = b, (b << 1) ^ a
    return b


@functools.cache
def psi(e: int) -> int:
    """Psi_e(t) for odd e >= 3: minimal-type polynomial of zeta_e + 1/zeta_e (product over
    primitive e-th roots up to inversion)."""
    num, rem = pdivmod(dickson(e), 0b10)
    assert rem == 0
    for e2 in range(3, e, 2):
        if e % e2 == 0:
            for _ in range(2):
                num, rem = pdivmod(num, psi(e2))
                assert rem == 0
    return psqrt(num)


@functools.cache
def cyclo_table(maxe: int = 400):
    """irreducible factor of some Psi_e -> smallest such e"""
    tab = {}
    for e in range(3, maxe, 2):
        for p, _ in factor2(psi(e)):
            tab.setdefault(p, e)
    tab.setdefault(0b10, 1)   # T = Psi_1? (t = zeta+1/zeta with zeta = 1 is 0)  mark as 'T'
    tab.setdefault(0b11, 3)   # T + 1 = Psi_3
    return tab


# ----------------------------------------------------------------------------- rules

def orbits(radius: int):
    return sorted({(a, b) for a in range(radius + 1) for b in range(a + 1)})


def points(orbit):
    a, b = orbit
    return {(sp * p, sq * q) for p, q in ((a, b), (b, a)) for sp in (1, -1) for sq in (1, -1)}


def rule_points(n: int, radius: int) -> frozenset:
    out = set()
    for i, o in enumerate(orbits(radius)):
        if n >> i & 1:
            out ^= points(o)
    return frozenset(out)


def rule_orbits(n: int, radius: int):
    return [o for i, o in enumerate(orbits(radius)) if n >> i & 1]


def _monos_of(poly: int):
    return [i for i in range(poly.bit_length()) if poly >> i & 1]


def orbit_F(orbit) -> set:
    """the orbit's symmetric Laurent polynomial as a polynomial in a, b (set of monomials)."""
    p, q = orbit
    out = set()

    def add(A: int, B: int):  # add A(a) * B(b)
        for i in _monos_of(A):
            for j in _monos_of(B):
                out.symmetric_difference_update({(i, j)})

    if p == 0 and q == 0:
        add(1, 1)
    elif q == 0:
        add(dickson(p), 1)
        add(1, dickson(p))
    elif p == q:
        add(dickson(p), dickson(p))
    else:
        add(dickson(p), dickson(q))
        add(dickson(q), dickson(p))
    return out


def rule_F(n: int, radius: int) -> frozenset:
    out = set()
    for o in rule_orbits(n, radius):
        out ^= orbit_F(o)
    return frozenset(out)


def F_str(F) -> str:
    return ' + '.join(f'a^{i}b^{j}' for i, j in sorted(F, reverse=True))


def subst_line(F, B: int) -> int:
    """F(T, B(T)) over GF(2) as an int polynomial."""
    powers = {0: 1}
    maxj = max((j for _, j in F), default=0)
    for j in range(1, maxj + 1):
        powers[j] = clmul(powers[j - 1], B)
    out = 0
    for i, j in F:
        out ^= powers[j] << i
    return out


def Q_dickson(F, n: int) -> int:
    """F(T, D_n(T)); for n = 2^i this is F(T, T^(2^i))."""
    return subst_line(F, dickson(n) if n else 0)


def g_line(f, k: int):
    """g_k(x) = f(x, x^k) as (polynomial int, shift): g_k = x^(-shift) * poly."""
    exps = {}
    for p, q in f:
        e = p + k * q
        exps[e] = exps.get(e, 0) ^ 1
    es = [e for e, c in exps.items() if c]
    if not es:
        return 0, 0
    lo = min(es)
    poly = 0
    for e in es:
        poly |= 1 << (e - lo)
    return poly, -lo


# ----------------------------------------------------------------------------- F_64

F64_MOD = 0b1000011  # w^6 + w + 1
EXP64 = [0] * 126
LOG64 = [None] * 64
_x = 1
for _e in range(63):
    EXP64[_e] = _x
    LOG64[_x] = _e
    _x <<= 1
    if _x & 64:
        _x ^= F64_MOD
assert _x == 1
for _e in range(63, 126):
    EXP64[_e] = EXP64[_e - 63]


def m64(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return EXP64[LOG64[a] + LOG64[b]]


def inv64(a: int) -> int:
    return EXP64[(63 - LOG64[a]) % 63]


def pow64(a: int, e: int) -> int:
    if a == 0:
        return 0 if e else 1
    return EXP64[(LOG64[a] * e) % 63]


def mu9_index(s: int) -> int:
    """for s in mu_9 subset F_64*, the k (mod 9) with s = w^(7k)."""
    l = LOG64[s]
    assert l % 7 == 0, s
    return (l // 7) % 9


# ----------------------------------------------------------------------------- F_64[T]

def q_trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def q_from2(p: int):
    return [(p >> i) & 1 for i in range(p.bit_length())]


def q_add(a, b):
    n = max(len(a), len(b))
    return q_trim([(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0) for i in range(n)])


def q_mul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    la = [LOG64[c] if c else None for c in a]
    for j, cb in enumerate(b):
        if cb == 0:
            continue
        lb = LOG64[cb]
        for i, l in enumerate(la):
            if l is not None:
                out[i + j] ^= EXP64[l + lb]
    return q_trim(out)


def q_scale(a, c):
    return q_trim([m64(x, c) for x in a])


def q_divmod(a, b):
    a = list(a)
    b = q_trim(b)
    db = len(b) - 1
    inv_lead = inv64(b[-1])
    q = [0] * max(len(a) - db, 1)
    lb = [LOG64[c] if c else None for c in b]
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c == 0:
            continue
        f = m64(c, inv_lead)
        q[i - db] = f
        lf = LOG64[f]
        for j, l in enumerate(lb):
            if l is not None:
                a[i - db + j] ^= EXP64[l + lf]
    return q_trim(q), q_trim(a[:db] if db > 0 else [])


def q_mod(a, b):
    return q_divmod(a, b)[1]


def q_monic(a):
    a = q_trim(a)
    return q_scale(a, inv64(a[-1]))


def q_gcd(a, b):
    a, b = q_trim(a), q_trim(b)
    while b:
        a, b = b, q_mod(a, b)
    return q_monic(a) if a else a


def q_mulmod(a, b, m):
    return q_mod(q_mul(a, b), m)


def q_sqmod(a, m):
    # squaring is linear over F_2 in char 2: (sum c_i T^i)^2 = sum c_i^2 T^{2i}
    out = [0] * (2 * len(a))
    for i, c in enumerate(a):
        out[2 * i] = m64(c, c)
    return q_mod(q_trim(out), m)


def q_powmod(a, e: int, m):
    r = [1]
    a = q_mod(a, m)
    while e:
        if e & 1:
            r = q_mulmod(r, a, m)
        e >>= 1
        if e:
            a = q_sqmod(a, m)
    return r


def q_frob(a):
    """apply the Frobenius x -> x^2 to the coefficients"""
    return [m64(c, c) for c in a]


def q_deg(a):
    return len(q_trim(a)) - 1


def q_eval(a, x):
    r = 0
    for c in reversed(a):
        r = m64(r, x) ^ c
    return r


def q_edf(f, d, rng):
    """equal-degree factorisation over F_64 of a square-free monic product of degree-d irreducibles.
    Uses the absolute trace Tr_{F_{64^d}/F_2} (char 2 Cantor-Zassenhaus)."""
    f = q_monic(f)
    if q_deg(f) == d:
        return [f]
    n = q_deg(f)
    while True:
        r = q_trim([rng.randrange(64) for _ in range(n)])
        if q_deg(r) < 1:
            continue
        t, s = list(r), list(r)
        for _ in range(6 * d - 1):
            s = q_sqmod(s, f)
            t = q_add(t, s)
        g = q_gcd(t, f)
        if g and 0 < q_deg(g) < n:
            return q_edf(g, d, rng) + q_edf(q_divmod(f, g)[0], d, rng)


def split_over_64(p: int):
    """an irreducible p in GF(2)[T] of degree d splits over F_64 into gcd(d,6) factors of degree
    d/gcd(d,6); return them (monic, over F_64)."""
    import math
    d = deg(p)
    g = math.gcd(d, 6)
    if g == 1:
        return [q_from2(p)]
    rng = random.Random(p)
    return q_edf(q_from2(p), d // g, rng)


def symbol9(A, R) -> int:
    """the ninth-power residue symbol (A/R)_9 for R irreducible monic over F_64, as an element of
    mu_9 in F_64 (computed by Euler's criterion A^((64^deg R - 1)/9) mod R)."""
    d = q_deg(R)
    v = q_powmod(A, (64 ** d - 1) // 9, R)
    assert len(v) <= 1, v
    if not v:
        return 0
    return v[0]


# ----------------------------------------------------------------------------- F(2^18) via t_1

@functools.cache
def m37() -> int:
    """minimal polynomial over GF(2) of t_1 = zeta_37 + 1/zeta_37: it is Psi_37 (degree 18)."""
    p = psi(37)
    assert deg(p) == 18
    return p


N18 = 2 ** 18 - 1
NINTH = N18 // 9  # 29127


def f18_mul(a, b):
    return pmulmod(a, b, m37())


def f18_pow(a, e):
    return ppowmod(a, e, m37())


def val_t1(Q: int, power2: int = 0) -> int:
    """Q(t_1^(2^power2)) in F(2^18) = GF(2)[X]/m37, where t_1 = X."""
    m = m37()
    x = ppowmod(0b10, 2 ** power2, m)
    # Horner
    r = 0
    for i in range(deg(Q), -1, -1):
        r = pmulmod(r, x, m) ^ (Q >> i & 1)
    return r


def is_ninth(v: int) -> bool:
    return v != 0 and f18_pow(v, NINTH) == 1


@functools.cache
def f18_generator() -> int:
    for g in range(2, 1 << 18):
        if all(f18_pow(g, N18 // p) != 1 for p in (3, 7, 19, 73)):
            return g


@functools.cache
def rho9() -> int:
    return f18_pow(f18_generator(), NINTH)


@functools.cache
def _mu9_table():
    r = rho9()
    tab = {}
    x = 1
    for k in range(9):
        tab[x] = k
        x = f18_mul(x, r)
    return tab


def log9(v: int) -> int:
    """log of v in F(2^18)* modulo 9 (generator f18_generator())"""
    return _mu9_table()[f18_pow(v, NINTH)]


@functools.cache
def f64_in_f18():
    """an embedding of F_64 = GF(2)[w]/(w^6+w+1) into F(2^18): dict F_64 element -> F(2^18)."""
    g = f18_generator()
    u = f18_pow(g, N18 // 63)  # order 63
    for j in range(1, 63):
        import math
        if math.gcd(j, 63) != 1:
            continue
        c = f18_pow(u, j)
        # test c^6 + c + 1 == 0
        if f18_pow(c, 6) ^ c ^ 1 == 0:
            emb = {0: 0}
            x = 1
            for e in range(63):
                emb[EXP64[e]] = x
                x = f18_mul(x, c)
            return emb
    raise RuntimeError


@functools.cache
def f18_to_f64():
    return {v: k for k, v in f64_in_f18().items()}


@functools.cache
def pis():
    """the six monic cubic factors over F_64 of m37: pis()[a] has roots t_1^(2^(a + 6l)), l=0,1,2."""
    m = m37()
    back = f18_to_f64()
    out = []
    for a in range(6):
        roots = [ppowmod(0b10, 2 ** (a + 6 * l), m) for l in range(3)]
        # (T + r0)(T + r1)(T + r2) with coefficients in F(2^18)
        e1 = roots[0] ^ roots[1] ^ roots[2]
        e2 = f18_mul(roots[0], roots[1]) ^ f18_mul(roots[0], roots[2]) ^ f18_mul(roots[1], roots[2])
        e3 = f18_mul(f18_mul(roots[0], roots[1]), roots[2])
        out.append([back[e3], back[e2], back[e1], 1])
    return out


def to64_from18(v: int) -> int:
    return f18_to_f64()[v]


# ----------------------------------------------------------------------------- factoring over F_64

def q_deriv(a):
    return q_trim([c if i % 2 == 1 else 0 for i, c in enumerate(a)][1:])


def q_sqrt(a):
    """square root of a polynomial over F_64 with only even exponents (sqrt(c) = c^32)."""
    assert all(c == 0 for c in a[1::2])
    return q_trim([pow64(c, 32) for c in a[0::2]])


def q_sqfree(f):
    out = []

    def rec(f, mult):
        f = q_monic(f)
        if q_deg(f) <= 0:
            return
        d = q_deriv(f)
        if not d:
            rec(q_sqrt(f), 2 * mult)
            return
        c = q_gcd(f, d)
        w = q_divmod(f, c)[0]
        i = 1
        while q_deg(w) > 0:
            y = q_gcd(w, c)
            z = q_divmod(w, y)[0]
            if q_deg(z) > 0:
                out.append((q_monic(z), i * mult))
            i += 1
            w = y
            c = q_divmod(c, y)[0]
        if q_deg(c) > 0:
            rec(q_sqrt(c), 2 * mult)

    rec(f, 1)
    return out


def q_pow64_mod(h, f):
    for _ in range(6):
        h = q_sqmod(h, f)
    return h


def q_ddf(f):
    out = []
    h = [0, 1]
    d = 0
    f = q_monic(f)
    while q_deg(f) >= 2 * (d + 1):
        d += 1
        h = q_pow64_mod(h, f)
        g = q_gcd(q_add(h, [0, 1]), f)
        if q_deg(g) > 0:
            out.append((g, d))
            f = q_divmod(f, g)[0]
            h = q_mod(h, f)
    if q_deg(f) > 0:
        out.append((q_monic(f), q_deg(f)))
    return out


def factor64(f, seed=0):
    """factor f over F_64: (leading coefficient, sorted list of (monic irreducible, multiplicity))."""
    f = q_trim(f)
    lc = f[-1]
    rng = random.Random(seed)
    res = {}
    for g, e in q_sqfree(f):
        for h, d in q_ddf(g):
            for p in q_edf(h, d, rng):
                key = tuple(p)
                res[key] = res.get(key, 0) + e
    return lc, sorted(res.items(), key=lambda kv: (len(kv[0]), kv[0]))


def jacobi9(A, B, n=9):
    """the n-th power residue (Jacobi) symbol (A/B)_n in F_64[T] (n | 63), computed from the
    factorisation of B by Euler's criterion at each monic irreducible factor (lead coeff of B is
    ignored, as in the definition).  Returns an element of mu_n in F_64, or 0 if not coprime."""
    _, facs = factor64(B)
    out = 1
    for R, e in facs:
        R = list(R)
        d = q_deg(R)
        v = q_powmod(A, (64 ** d - 1) // n, R)
        if not v:
            return 0
        assert len(v) == 1
        out = m64(out, pow64(v[0], e))
    return out


def resultant64(A, B):
    """Res(A, B) over F_64 via the Euclidean algorithm (char 2: no signs)."""
    A, B = q_trim(A), q_trim(B)
    if not A or not B:
        return 0
    res = 1
    while True:
        da, db = q_deg(A), q_deg(B)
        if db == 0:
            return m64(res, pow64(B[0], da))
        r = q_mod(A, B)
        if not r:
            return 0
        # Res(A,B) = lc(B)^(da - deg r) * Res(r, B) ; Res(r,B) = Res(B,r) (char 2)
        res = m64(res, pow64(B[-1], da - q_deg(r)))
        A, B = B, r


# ----------------------------------------------------------------------------- F(2^36) = GF(2)[z]/Phi_37

@functools.cache
def phi37() -> int:
    return (1 << 37) - 1  # 1 + z + ... + z^36 (irreducible over GF(2): 2 is primitive mod 37)


N36 = 2 ** 36 - 1
NINTH36 = N36 // 9


def f36_mul(a, b):
    return pmulmod(a, b, phi37())


def f36_pow(a, e):
    return ppowmod(a, e, phi37())


@functools.cache
def f36_generator() -> int:
    import sympy
    ps = sympy.primefactors(N36)
    for g in range(2, 1 << 20):
        if all(f36_pow(g, N36 // p) != 1 for p in ps):
            return g


@functools.cache
def _mu9_36():
    r = f36_pow(f36_generator(), NINTH36)
    tab, x = {}, 1
    for k in range(9):
        tab[x] = k
        x = f36_mul(x, r)
    return tab


def log9_36(v: int) -> int:
    return _mu9_36()[f36_pow(v, NINTH36)]


@functools.cache
def f64_in_f36():
    """embedding F_64 -> F(2^36) compatible with w^6 + w + 1"""
    import math
    g = f36_generator()
    u = f36_pow(g, N36 // 63)
    for j in range(1, 63):
        if math.gcd(j, 63) != 1:
            continue
        c = f36_pow(u, j)
        if f36_pow(c, 6) ^ c ^ 1 == 0:
            emb = {0: 0}
            x = 1
            for e in range(63):
                emb[EXP64[e]] = x
                x = f36_mul(x, c)
            return emb
    raise RuntimeError


@functools.cache
def f36_to_f64():
    return {v: k for k, v in f64_in_f36().items()}


@functools.cache
def phis():
    """the six monic sextic factors of Phi_37 over F_64: phis()[a] has roots zeta^(2^(a+6l))."""
    back = f36_to_f64()
    out = []
    for a in range(6):
        poly = [1]  # over F(2^36) as list of ints (F(2^36) elements)
        for l in range(6):
            r = f36_pow(0b10, 2 ** (a + 6 * l))
            # multiply poly by (X + r)
            new = [0] * (len(poly) + 1)
            for i, c in enumerate(poly):
                new[i + 1] ^= c
                new[i] ^= f36_mul(c, r)
            poly = new
        out.append([back[c] for c in poly])
    return out
