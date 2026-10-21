"""sc8 (check-scope): small leftovers at 37 in our own field: the theta form of claim (3), the aux equation for
eta_0, and which d the earlier residual class {(1,3),(1,5),(1,13)} has in the 45-degree coordinates."""
import json
import cslib
m = 37
S = cslib.Setting(m, seed=11)
F = S.F
mul = F.mul
lg = {pow(2, k, m): k for k in range(36)}
h = pow(2, -1, m)
e0 = S.eta(1)
out = {}
out['eta0^24 + eta0^9 + 1 = 0'] = F.pow(e0, 24) ^ F.pow(e0, 9) ^ 1 == 0
theta = lambda x: S.eta(x) ^ S.eta(8 * x)
out['theta(x) = eta(x)^15 for all x'] = all(theta(x) == F.pow(S.eta(x), 15) for x in range(1, m))
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
f = cslib.divide_by_s(cslib.hex_G(2, 5))
ok = True
for j in range(m):
    for k in range(m):
        al, be = (j + k) * h % m, (j - k) * h % m
        if not (al and be):
            continue
        lam = 0
        for x, y in f:
            lam ^= S.zp[(x * j + y * k) % m]
        d = (lg[be] - lg[al]) % 6
        TT = mul(theta(al), theta(be))
        ok &= S.norm(lam) == F.pow(TT, (2 * (2 * n[d] - 1)) % F.N)
out['N(lambda_4850) = (theta theta)^(2(2n-1)) off j=+-k'] = ok
cls = {}
for (j, k) in ((1, 3), (1, 5), (1, 13)):
    orbit_ds = set()
    for c in range(36):
        jj, kk = pow(2, c, m) * j % m, pow(2, c, m) * k % m
        for (a, b) in ((jj, kk), (kk, jj), (jj, -kk % m), (-jj % m, kk)):
            al, be = (a + b) * h % m, (a - b) * h % m
            orbit_ds.add((lg[be] - lg[al]) % 6)
    cls['%d,%d' % (j, k)] = sorted(orbit_ds)
out['d values on the residual class (with D4 images)'] = cls
others = {}
for (j, k) in ((1, 2), (1, 4), (1, 6), (1, 7), (1, 8), (1, 10), (0, 1)):
    ds = set()
    for c in range(36):
        jj, kk = pow(2, c, m) * j % m, pow(2, c, m) * k % m
        for (a, b) in ((jj, kk), (kk, jj), (jj, -kk % m), (-jj % m, kk)):
            al, be = (a + b) * h % m, (a - b) * h % m
            if al and be:
                ds.add((lg[be] - lg[al]) % 6)
    others['%d,%d' % (j, k)] = sorted(ds)
out['d values on the other off-diagonal classes'] = others
for k_, v in out.items():
    print(k_, v)
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc8_odds.json', 'w'), indent=1)
