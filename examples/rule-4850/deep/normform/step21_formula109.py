"""Step 21: is the norm formula a general phenomenon?  At m = 109 (same field: K = F(2^18), sigma = Frob^6 =
dilation by 64, 64 in mu6 mod 109, k = F64, ninth power <=> N_{K/F64} in F8) test:
  (i)  t_j cubes in K?  (rule 90's cube property)            (ii) eta(x) = sum_{mu6} zeta^(ux) cubes in F64?
  (iii) N_{K/F64}(W(al,be)) = eta(4 al^2/be) when be/al is a QR?   (iv) N(W) in F8 / an index-3 period when NQR?
and the same four at m = 37 for comparison.  Field: linear-atlas-3 eigen.field(m) (F(2^36))."""
import sys, json, collections
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen

def study(m):
    mod, d = eigen.field(m)
    mul = lambda a, b: eigen._mul(a, b, mod, d)
    pw = lambda a, e: eigen._pow(a, e, mod, d)
    N = 2 ** d - 1
    z = [pw(2, e) for e in range(m)]
    t = [z[i] ^ z[(-i) % m] for i in range(m)]
    K18 = lambda v: pw(v, 2 ** 18) == v
    mu3 = [u for u in range(1, m) if pow(u, 3, m) == 1]
    mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
    mu12 = [u for u in range(1, m) if pow(u, 12, m) == 1]
    assert pow(64, 6, m) == 1
    NK = 2 ** 18 - 1
    inK = all(K18(t[j]) for j in range(1, m))
    tcube = all(pw(t[j], NK // 3) == 1 for j in range(1, m))  # in K*: z^(NK/3) = 1
    def eta(x):
        v = 0
        for u in mu6:
            v ^= z[u * x % m]
        return v
    def theta(x):
        v = 0
        for u in mu12:
            v ^= z[u * x % m]
        return v
    F64 = lambda v: pw(v, 64) == v
    F8 = lambda v: pw(v, 8) == v
    etacube = all(pw(eta(x), 21) == 1 for x in range(1, m))
    def legendre(a):
        return 1 if pow(a, (m - 1) // 2, m) == 1 else -1
    qr_ok = qr_tot = 0; nqr_F8 = nqr_theta = nqr_tot = 0
    thetas = {theta(x) for x in range(1, m)}
    seen = set()
    for al in range(1, m):
        for be in range(1, m):
            c = (al, be)
            if c in seen:
                continue
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            W = 0
            for u in mu3:
                W ^= mul(t[u * al % m], t[be * pow(u, -1, m) % m])
            nw = 1
            for cc in mu3:
                Wc = 0
                for u in mu3:
                    Wc ^= mul(t[u * al % m], t[cc * be * pow(u, -1, m) % m])
                nw = mul(nw, Wc)
            assert F64(nw)
            if legendre(be * pow(al, -1, m)) == 1:
                qr_tot += 1; qr_ok += nw == eta(4 * al * al * pow(be, -1, m) % m)
            else:
                nqr_tot += 1; nqr_F8 += F8(nw); nqr_theta += nw in thetas
    return dict(m=m, t_in_K=inK, t_cubes=tcube, eta_cubes_in_F64=etacube,
                QR_formula=f'{qr_ok}/{qr_tot}', NQR_in_F8=f'{nqr_F8}/{nqr_tot}', NQR_is_theta=f'{nqr_theta}/{nqr_tot}')
out = [study(37), study(109)]
for r in out:
    print(r)
json.dump(out, open('step21_formula109.json', 'w'), indent=1)
