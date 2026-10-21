"""sc7 (check-scope): m = 4033 = 37 * 109, the only other size where sigma = Frob^6 acts as a primitive cube root
and k = F64 (but the mu6-cosets are not one Frobenius orbit).  Are -3-type hexagon members confined there?
Members with q^2 + 3 p^2 = 4033: (28, 41), (32, 31).  Off the diagonals lambda = G(c)/s(c) (12-point G), so the
test needs no large polynomial.  Random characters; report how many are cubes / ninth powers in F(2^18)."""
import json
import random
import cslib

m = 4033
F = cslib.Field(36, seed=4033)
assert F.N % m == 0
z = F.root_of_unity(m)
zp = [1]
for _ in range(m - 1):
    zp.append(F.mul(zp[-1], z))
assert pow(2, 18, m) == m - 1
Q3, Q9 = (2 ** 18 - 1) // 3, (2 ** 18 - 1) // 9
rng = random.Random(1)
out = {}
for p, q in ((28, 41), (32, 31)):
    assert q * q + 3 * p * p == m
    r = q * pow(p, -1, m) % m
    u = (1 + r) * pow(2, -1, m) % m
    aligned = u in {pow(64, i, m) for i in range(6)}
    G = cslib.hex_G(p, q)
    n = cube = ninth = 0
    for _ in range(4000):
        j, k = rng.randrange(m), rng.randrange(m)
        s = zp[j] ^ zp[(-j) % m] ^ zp[k] ^ zp[(-k) % m]
        if s == 0:
            continue
        g = 0
        for a, b in G:
            g ^= zp[(a * j + b * k) % m]
        if g == 0:
            continue
        lam = F.mul(g, F.inv(s))
        assert F.frob(lam, 18) == lam
        n += 1
        cube += F.pow(lam, Q3) == 1
        ninth += F.pow(lam, Q9) == 1
    out['%d,%d' % (p, q)] = dict(
        mu6_of_hexagon_is_frobenius_mu6=aligned, sampled=n, cubes=cube, ninth=ninth)
    print((p, q), out['%d,%d' % (p, q)], flush=True)
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc7_size4033.json', 'w'), indent=1)
