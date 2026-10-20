"""Step 7 (norms): the mechanism at other sizes.  For each prime m with ord_m(2) = 2e:
  * setting: f = [k:F2] = e/3, v3|k*|, index of <2> in F_m*, whether 1-w, 2-w, 2-w^2 lie in <2> mu6 (single
    Frobenius orbit), their coset exponents (a, b, b'), whether all periods eta are cubes in k;
  * the 37 MECHANISM's hypotheses: H1 f = 6 (k = F64: ninth powers + 0 = F8, a subfield), H2 single orbit,
    H3 a = 4 and (b, b' odd or b = b'), H0 eta cubes;  verdict 'applies' iff all hold;
  * the exact norm criterion (an equivalence, from (*)) for the core f0_m = h_m/pi: N(lambda) = (*)/(X^2 Y^2),
    cube / ninth tests in k (ninth only decidable by N when v3|k*| >= 2), versus the DIRECT 3-adic class of
    lambda = W/(t_al t_be) in K;
  * the two smallest '-3 type' hexagon rules f_{p,q} at m (q^2 + 3p^2 = 0 mod m): find r with
    R(G_{p,q}) = r * S_m (R = 45-degree rotation (a,b) -> (a+b, a-b), S_m = {(u, +-1/u)}), so that off the
    diagonals lambda_f = W(r al, r be)/(t_al t_be); predicted N vs direct N, and the confinement levels.
Characters are reduced to mu6-coset pairs (N depends only on those) for speed; direct checks use the
actual eigenvalue at one representative of each pair."""
import sys, json, math, time
import nlib

sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/model19')
from hexfamily import f_pq, hex_pts


def v3(n):
    k = 0
    while n % 3 == 0:
        n //= 3
        k += 1
    return k


def analyse(m, hex_count=2):
    t0 = time.time()
    S = nlib.Setting(m)
    F = S.F
    mul = F.mul
    d, e = S.d, S.e
    rec = dict(m=m, ord=d, e=e)
    if e % 3:
        rec['note'] = '3 does not divide e: no cubic subextension K/k'
        return rec
    f = e // 3
    w = (-pow(2, f, m)) % m
    assert pow(w, 3, m) == 1 and w != 1
    kord = (1 << f) - 1
    Kord = (1 << e) - 1
    rec.update(f=f, v3_k=v3(kord), v3_K=v3(Kord), w=w)
    two = S.two
    idx2 = (m - 1) // d
    rec['index_of_<2>'] = idx2
    mu6 = S.mu6
    # coset of x in F_m*/mu6 relative to <2>: exponent c with x in 2^c mu6, or None
    def frob_exp(x):
        for c in range(f):
            if any((pow(2, c, m) * u - x) % m == 0 for u in mu6):
                return c
        return None
    a, b, b2 = frob_exp(1 - w), frob_exp(2 - w), frob_exp(2 - w * w)
    rec['coset_exps(a,b,b2)'] = (a, b, b2)
    # mu6-coset representatives
    reps, seen = [], set()
    for x in range(1, m):
        if x in seen:
            continue
        reps.append(x)
        for u in mu6:
            seen.add(x * u % m)
    rec['n_mu6_cosets'] = len(reps)
    eta = {x: S.eta(x) for x in reps}
    def eta_of(x):
        x %= m
        for u in mu6:
            y = x * u % m
            if y in eta:
                return eta[y]
    cubes_k = all(F.pow(z, kord // 3) == 1 for z in eta.values()) if kord % 3 == 0 else None
    rec['eta_cubes_in_k'] = cubes_k
    H1 = f == 6
    H3 = (a == 4 and ((b % 2 == 1 and b2 % 2 == 1) or b == b2)) if (H1 and None not in (a, b, b2)) else False
    rec['H0_eta_cubes'] = cubes_k
    rec['H1_k=F64'] = H1
    rec['H2_single_orbit'] = bool(len(reps) == f)
    rec['H3_cosets'] = H3
    rec['mechanism_applies'] = bool(cubes_k and H1 and len(reps) == f and H3)

    def star(al, be):
        X, Y = eta_of(al), eta_of(be)
        Xa, Ya = eta_of((1 - w) * al), eta_of((1 - w) * be)
        Xb, Yb = eta_of((2 - w) * al), eta_of((2 - w) * be)
        Xc, Yc = eta_of((2 - w * w) * al), eta_of((2 - w * w) * be)
        XY = mul(X, Y)
        v = mul(mul(XY, XY), 1 ^ X ^ Y)
        v ^= mul(XY, mul(X, Ya) ^ mul(Xa, Y))
        v ^= mul(XY, mul(Xa, Ya))
        v ^= mul(mul(Xa, Ya), X ^ Y)
        v ^= mul(Xb, Yb) ^ mul(Xc, Yc)
        return v, X, Y

    def levels_k(z):
        # no 3-part in |k*| means every element is a cube (resp. ninth power): report True
        cube = F.pow(z, kord // 3) == 1 if kord % 3 == 0 else True
        ninth = F.pow(z, kord // 9) == 1 if kord % 9 == 0 else (True if kord % 3 else None)
        return cube, ninth

    def levels_K(z):
        cube = F.pow(z, F.order // 3) == 1
        ninth = F.pow(z, F.order // 9) == 1 if F.order % 9 == 0 else None
        return cube, ninth

    # core f0: lambda = W/(t_al t_be)
    pairs = [(x, y) for x in reps for y in reps]
    core = dict(n_pairs=len(pairs), star_mismatch=0, pred_cube=True, pred_ninth=True, act_cube=True, act_ninth=True,
                classes_failing_ninth=0, classes_failing_cube=0)
    for al, be in pairs:
        Nst, X, Y = star(al, be)
        Wv = S.W(al, be)
        if S.norm_Kk(Wv) != Nst:
            core['star_mismatch'] += 1
        Nl = mul(Nst, F.inv(mul(mul(X, X), mul(Y, Y))))
        c, n9 = levels_k(Nl)
        lam = mul(Wv, F.inv(mul(S.t[al], S.t[be])))
        C, N9 = levels_K(lam)
        core['pred_cube'] &= bool(c)
        core['act_cube'] &= bool(C)
        if not C:
            core['classes_failing_cube'] += 1
        if N9 is not None:
            core['act_ninth'] &= bool(N9)
            if not N9:
                core['classes_failing_ninth'] += 1
        if n9 is not None:
            core['pred_ninth'] &= bool(n9)
        if c is not None and c != C:
            core['norm_vs_direct_cube_disagree'] = core.get('norm_vs_direct_cube_disagree', 0) + 1
        if rec['v3_k'] >= 2 and n9 != N9:
            core['norm_vs_direct_ninth_disagree'] = core.get('norm_vs_direct_ninth_disagree', 0) + 1
    if rec['v3_k'] < 2:
        core['pred_ninth'] = 'not decidable by N (v3|k*| < 2)'
    if F.order % 9:
        core['act_ninth'] = None
    rec['core_f0'] = core
    # hexagon -3 type rules
    S_m = {(u % m, s * pow(u, -1, m) % m) for u in mu6 for s in (1, -1)}
    cands = sorted([(max(2 * P, Q), P, Q) for P in range(1, 12) for Q in range(1, 30)
                    if (Q * Q + 3 * P * P) % m == 0 and math.gcd(P, Q) == 1])[:hex_count]
    hexes = []
    for _, P, Q in cands:
        H = hex_pts(P, Q)
        G = H ^ {(y, x) for x, y in H}
        RG = {((x + y) % m, (x - y) % m) for x, y in G}
        rr = [r for r in range(1, m) if {(r * u % m, r * v % m) for u, v in S_m} == RG]
        hrec = dict(p=P, q=Q, r=rr[0] if rr else None)
        if not rr:
            hrec['note'] = 'R(G) is not a dilate of S_m'
            hexes.append(hrec)
            continue
        r = rr[0]
        fset = f_pq(P, Q)
        inv2 = pow(2, -1, m)
        mism = 0; pc = pn = ac = an = True
        for al, be in pairs:
            j, k = (al + be) % m, (al - be) % m
            lam = 0
            for x, y in fset:
                lam ^= S.zp[(x * j + y * k) % m]
            if lam == 0:
                continue
            Nst, _, _ = star(r * al % m, r * be % m)
            X, Y = eta_of(al), eta_of(be)
            Np = mul(Nst, F.inv(mul(mul(X, X), mul(Y, Y))))
            if S.norm_Kk(lam) != Np:
                mism += 1
            c, n9 = levels_k(Np)
            C, N9 = levels_K(lam)
            pc &= bool(c); ac &= bool(C)
            if n9 is not None:
                pn &= bool(n9)
            if N9 is not None:
                an &= bool(N9)
        hrec.update(pred_norm_mismatch=mism, pred_cube_offdiag=pc, act_cube_offdiag=ac,
                    pred_ninth_offdiag=(pn if rec['v3_k'] >= 2 else 'n/a'), act_ninth_offdiag=an)
        # full direct confinement over ALL nonzero characters (orbit representatives under doubling),
        # including the diagonals j = +-k where s(c) = 0
        seen = set(); fc = fn = True; zeros = 0; diag = set()
        for j in range(m):
            for k in range(m):
                if (j, k) == (0, 0) or (j, k) in seen:
                    continue
                c = (j, k)
                while c not in seen:
                    seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
                lam = 0
                for x, y in fset:
                    lam ^= S.zp[(x * j + y * k) % m]
                if lam == 0:
                    zeros += 1
                    continue
                C, N9 = levels_K(lam)
                fc &= bool(C)
                if N9 is not None:
                    fn &= bool(N9)
                if (j - k) % m == 0 or (j + k) % m == 0:
                    diag.add('ninth' if N9 else ('cube' if C else 'none'))
        hrec.update(direct_all_cube=fc, direct_all_ninth=fn if F.order % 9 == 0 else None,
                    zero_orbits=zeros, diagonal_levels=sorted(diag))
        hexes.append(hrec)
    rec['hexagons'] = hexes
    rec['seconds'] = round(time.time() - t0, 1)
    return rec


if __name__ == '__main__':
    out = []
    for m in [int(a) for a in sys.argv[1:]] or [13, 19, 37, 61, 97, 109]:
        r = analyse(m)
        print(json.dumps(r), flush=True)
        out.append(r)
    name = 's7_other_sizes.json' if len(sys.argv) <= 1 else 's7_other_sizes_%s.json' % '_'.join(sys.argv[1:])
    json.dump(out, open(name, 'w'), indent=1)
