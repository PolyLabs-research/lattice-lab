"""Step 20: soundness of the shape at other sizes.  For primes m = 1 mod 3 (so mu3, mu6 lie in F_m*), with
d = ord_m(2) <= 60, build the analogue of the core: h_m = sum_{u in mu6(F_m), e = +-1} x^u y^(e/u),
f0_m = h_m / pi (eigenvalue W/pi off the axes; h_m is T-invariant, T = diag(c, 1/c), c in mu3 mod m), and test
cube / ninth-confinement of W/pi off the axes, in F(2^d) (an independent field: linear-atlas-3/eigen.field).
Also test the three census rules and 4850 at the same sizes (their pi*f = 37-specific orbit is not T-invariant mod m)."""
import sys, json, math
import sympy
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import eigen, census

def field_ops(m):
    mod, d = eigen.field(m)
    mul = lambda a, b: eigen._mul(a, b, mod, d)
    pw = lambda a, e: eigen._pow(a, e, mod, d)
    return mod, d, mul, pw
out = []
for m in sympy.primerange(7, 230):
    if m % 3 != 1:
        continue
    d = sympy.n_order(2, m)
    if d > 60:
        continue
    N = 2 ** d - 1
    v3 = sympy.multiplicity(3, N)
    mod, d, mul, pw = field_ops(m)
    z = [pw(2, e) for e in range(m)]
    t = [z[i] ^ z[(-i) % m] for i in range(m)]
    mu3 = [u for u in range(1, m) if pow(u, 3, m) == 1]
    inv = lambda u: pow(u, -1, m)
    cube = True; ninth = True if v3 >= 2 else None; fails = 0; zeros = 0
    seen = set()
    for al in range(1, m):
        for be in range(1, m):
            if (al, be) in seen:
                continue
            c = (al, be)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            W = 0
            for u in mu3:
                W ^= mul(t[u * al % m], t[be * inv(u) % m])
            if W == 0:
                zeros += 1; continue
            lam = mul(W, pw(mul(t[al], t[be]), N - 1))
            if pw(lam, N // 3) != 1:
                cube = False
            if ninth is not None and pw(lam, N // 9) != 1:
                ninth = False; fails += 1
    rec = dict(m=m, d=d, v3=v3, f0_cube=cube, f0_ninth=ninth, ninth_fail_orbits=fails, W_zero_orbits=zeros)
    # the actual rules at m (if not wrapped): ninth?
    if v3 >= 2:
        for n, r in ((4850, 4), (10491524, 6), (20982139, 6), (178279803, 6)):
            op = eigen.odd_part(census.rule(n, r), m)
            rec['rule%d_ninth' % n] = (N // 9) % op == 0
    out.append(rec); print(rec, flush=True)
json.dump(out, open('step20_othersizes.json', 'w'), indent=1)
