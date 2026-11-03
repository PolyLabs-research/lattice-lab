"""Which stage-4 tori are not yet in records.jsonl, and which of them can have codes (criterion E,
re-implemented here in pure Python: some odd e > 1 dividing lcm of the odd parts has a != 1 in mu_e
with 1 + a in mu_e, computed in GF(2^r), r = ord_e(2))."""
import json, math
from pathlib import Path
REPO = Path('/home/user/lattice-lab/examples')
EXPOSED = {(11, 14), (12, 13), (13, 13), (13, 14), (14, 14), (6, 30)}
every = sorted(((l, m) for l in range(2, 15) for m in range(l, 101) if 150 < l * m <= 200), key=lambda t: (t[0] * t[1], t))
order = [t for t in every if t not in EXPOSED] + [t for t in every if t in EXPOSED]
done = {(r['l'], r['m']) for r in map(json.loads, open(REPO / 'qec-census-4' / 'records.jsonl')) if r.get('job') == 'torus'}

def odd(x):
    while x % 2 == 0: x //= 2
    return x

def irreducible(r):
    # smallest irreducible poly of degree r over GF(2) (bitmask), by trial (r small here)
    def mulmod(a, b, p, r):
        res = 0
        while b:
            if b & 1: res ^= a
            b >>= 1; a <<= 1
            if a >> r & 1: a ^= p
        return res
    for p in range(1 << r, 1 << (r + 1)):
        if not p & 1: continue
        # Rabin-ish: x^(2^r) == x mod p and gcd conditions skipped -> check no factor of degree <= r/2 by brute force
        ok = True
        for q in range(2, 1 << (r // 2 + 1)):
            # polynomial mod
            a = p; dq = q.bit_length() - 1
            while a.bit_length() - 1 >= dq:
                a ^= q << (a.bit_length() - 1 - dq)
            if a == 0: ok = False; break
        if ok: return p, mulmod

def crit(l, m):
    E = math.lcm(odd(l), odd(m))
    for e in range(3, E + 1, 2):
        if E % e: continue
        r = 1
        while pow(2, r, e) != 1: r += 1
        if r > 24:  # too big for this brute force; report unknown
            return None
        p, mm = irreducible(r)
        N = (1 << r) - 1
        # find a generator-ish element: try g = x, x+1, ... until order N
        def pw(a, k):
            res = 1
            while k:
                if k & 1: res = mm(res, a, p, r)
                a = mm(a, a, p, r); k >>= 1
            return res
        g = None
        for c in range(2, 1 << r):
            if all(pw(c, N // q) != 1 for q in {q for q in range(2, N + 1) if N % q == 0 and all(q % s for s in range(2, int(q ** .5) + 1))}):
                g = c; break
        z = pw(g, N // e)  # element of order e
        mu = set(); a = 1
        for _ in range(e):
            mu.add(a); a = mm(a, z, p, r)
        if any((1 ^ a) in mu for a in mu if a != 1):
            return True
    return False

rem = [t for t in order if t not in done]
print('done', len(done), 'remaining', len(rem))
for t in rem:
    print(t, 2 * t[0] * t[1], 'exposed' if t in EXPOSED else 'fresh', 'gcd/lcm', (math.gcd(*t), t[0]*t[1]//math.gcd(*t)), 'criterionE', crit(*t))
# sanity: compare criterion on done tori
bad = 0
for r in map(json.loads, open(REPO / 'qec-census-4' / 'records.jsonl')):
    if r.get('job') == 'torus':
        c = crit(r['l'], r['m'])
        if c is not None and c != r['criterion_e']: bad += 1; print('MISMATCH', r['l'], r['m'], c, r['criterion_e'])
print('criterion mismatches on done tori:', bad)
