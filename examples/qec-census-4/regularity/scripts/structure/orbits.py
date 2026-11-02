"""Admissible character orders t (a zero of 1 + u + v at a character of exact order t needs
a, 1 + a with lcm(ord a, ord(1+a)) = t), Frobenius orbit sizes, and the k ladder per group."""
from common import *
from common import _pgcd, _ppow
import itertools

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

def mobius(n):
    f = factor(n)
    if any(v > 1 for v in f.values()):
        return 0
    return -1 if len(f) % 2 else 1

@functools.lru_cache(None)
def c(f, g):
    """# a in closure(GF2) with a^f = 1 and (1+a)^g = 1."""
    return _pgcd((1 << f) | 1, _ppow(0b11, g) ^ 1).bit_length() - 1

@functools.lru_cache(None)
def exact(f, g):
    return sum(mobius(f // f1) * mobius(g // g1) * c(f1, g1)
               for f1 in divisors(f) for g1 in divisors(g))

@functools.lru_cache(None)
def admissible(t):
    """characters of exact order t can be zeros of some A = 1 + u + v."""
    return any(exact(f, g) > 0 for f in divisors(t) for g in divisors(t) if math.lcm(f, g) == t)

T = [t for t in range(3, 200, 2) if admissible(t)]
print("admissible orders t <= 199:", T)
print("orbit sizes ord_t(2):", {t: ord2(t) for t in T})

def char_counts(g):
    """number of characters of exact order t of Z_a x Z_b (t odd), for all t."""
    a, b = g
    out = Counter()
    # count elements of each order in dual (iso to group): brute force on (i, j)
    for i in range(a):
        for j in range(b):
            o = math.lcm(a // math.gcd(a, i), b // math.gcd(b, j))
            out[o] += 1
    return out

def orbit_profile(g):
    cc = char_counts(g)
    prof = {}
    for t, cnt in cc.items():
        if t % 2 and t > 1 and admissible(t):
            prof[t] = (cnt // ord2(t), ord2(t))   # (number of orbits, orbit size)
    return prof

if __name__ == "__main__":
    rows = json.load(open("groups.json"))
    ok = bad = 0
    single = Counter()
    out = []
    for r in rows:
        g = tuple(r["g"]); kset = sorted(int(k) for k in r["kd"])
        prof = orbit_profile(g)
        kmin_pred = 2 * min(s for (no, s) in prof.values())
        norb = sum(no for (no, s) in prof.values())
        out.append((g, prof, kset))
        if kmin_pred == min(kset):
            ok += 1
        else:
            bad += 1; print("kmin mismatch", g, prof, kset)
        single[(norb == 1, r["r2"] <= 1, len(kset) == 1)] += 1
    print("k_min = 2 x smallest admissible orbit:", ok, "of", ok + bad, "groups")
    print("(exactly one admissible orbit, r2<=1, single frontier k):", dict(single))
    # profiles of the high-score groups
    for gg in [(1, 155), (1, 186), (1, 189), (3, 63), (1, 170), (6, 12), (12, 12), (4, 36), (3, 60), (6, 30), (1, 180), (2, 90)]:
        print(gg, orbit_profile(gg))
