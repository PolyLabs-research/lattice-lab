"""Transport of a symmetric rule at m = 37 to the '19-torus' (mu19*)^2, and tools.

Because ord_37(2) = 36 and ord_19(2) = 18, phi: (Z/37)*/{+-1} -> (Z/19)*, 2^e -> 2^e, is an
isomorphism, and t_j = T(zeta19^phi(j)) with T(x) = sum_{i in S} x^i, S = support of t_1 in the
zeta19 normal basis.  A symmetric rule F(a, b) has eigenvalue F(t_j, t_k) = Ft(zeta19^phi(j), zeta19^phi(k))
with Ft(x, y) = F(T(x), T(y)): its eigenvalues off the axes ARE the eigenvalues of the 19-torus
rule Ft on (mu19*)^2 (18 Frobenius orbits, reps (1, b), b in F19*).
"""
import functools
import ff18 as F

P19 = [pow(2, e, 19) for e in range(18)]          # 2^e mod 19
IND19 = {P19[e]: e for e in range(18)}


def phi(j):
    return pow(2, F.ind37(j) % 18, 19)


def k_of_b(b):
    """the k in 1..36 with phi(k) = b and k = 2^e, e = ind19(b) (one of +-k)."""
    return pow(2, IND19[b % 19], 37)


def torus_values(valfun):
    """valfun(j, k) -> eigenvalue at 37; returns h[b] = value at 19-torus point (1, b), b = 1..18."""
    return {b: valfun(1, k_of_b(b)) for b in range(1, 19)}


@functools.cache
def _system():
    """F2-linear map: coefficient c_{il} (i, l in 1..18) of x^i y^l -> values at (zeta, zeta^b), b = 1..18,
    in zeta19 normal-basis coordinates.  Returns elimination data to solve for c."""
    cols = []
    for i in range(1, 19):
        for l in range(1, 19):
            vec = 0
            for bi, b in enumerate(range(1, 19)):
                n = (i + l * b) % 19
                coords = ((1 << 18) - 1) if n == 0 else (1 << (n - 1))
                vec |= coords << (18 * bi)
            cols.append(vec)
    return F._elim(cols)


def poly_of(h):
    """the unique Ft in span{x^i y^l : 1 <= i, l <= 18} with Ft(zeta, zeta^b) = h[b]; returns list of (i, l)."""
    target = 0
    for bi, b in enumerate(range(1, 19)):
        S = F.nb19(h[b])
        for n in S:
            target |= 1 << (18 * bi + n - 1)
    tag = F._coords(_system(), target)
    idx = [(i, l) for i in range(1, 19) for l in range(1, 19)]
    return [idx[m] for m in range(324) if tag >> m & 1]


def s_function(h):
    """mu19 exponent s(1, b) of h[b] (canonical zeta19)."""
    z = F.z19pows()
    return {b: z.index(F.pw(h[b], F.E19)) for b in h}


def s_full(sb):
    """s(a, b) on the whole torus from s(1, b): s(a, ab) = a s(1, b)."""
    return {(a, a * b % 19): a * sb[b] % 19 for a in range(1, 19) for b in range(1, 19)}


def fourier19(sab):
    """coefficients C_{il} (i, l mod 18) with s(a, b) = sum C_il a^i b^l over F19 (a, b in F19*)."""
    inv324 = pow(324 % 19, -1, 19)
    C = {}
    for i in range(18):
        for l in range(18):
            acc = 0
            for p in range(18):
                for q in range(18):
                    a, b = P19[p], P19[q]
                    acc += sab[(a, b)] * pow(2, (-(p * i + q * l)) % 18, 19)
            c = acc * inv324 % 19
            if c:
                C[(i, l)] = c
    return C
