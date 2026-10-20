"""Step 11. Integer realisations of M-invariant numerators at m (exponent reps in (-m/2, m/2)), and their odd parts:
   N(e) = D4-closure of the <M>-orbit of e mod m,  M = [[1/2, r/2], [r/2, 1/2]] (exponent action),  rule = N / s.
Used for (i) the hexagon with minimal reps (check against hex_rule), (ii) hexagon + 24-point sums found in step 9."""
import sys, json
import famlib as L


def rep(x, m):
    x %= m
    return x - m if x > m // 2 else x


def orbit_numerator(e, m, r):
    h = pow(2, -1, m)
    M = ((h, r * h % m), (r * h % m, h))
    pts = set()
    x = (e[0] % m, e[1] % m)
    for _ in range(6):
        pts.add(x)
        x = ((M[0][0] * x[0] + M[0][1] * x[1]) % m, (M[1][0] * x[0] + M[1][1] * x[1]) % m)
    allp = set()
    for a, b in pts:
        for c in ((a, b), (b, a)):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    allp.add((s1 * c[0] % m, s2 * c[1] % m))
    return {(rep(a, m), rep(b, m)) for a, b in allp}


def rule_from(numerators, m):
    G = set()
    for N in numerators:
        G ^= N
    if any(a == b or a == -b for a, b in G):
        return None, 'diagonal points'
    return L.quotient_by_s(G), 'ok'


def eig_coords_to_e(A, B, m):
    h = pow(2, -1, m)
    return ((A + B) * h % m, (A - B) * h % m)


if __name__ == '__main__':
    m, r = 37, 16
    out = []
    # hexagon, A = 4 (4850): e = (2p, 0), p = 2
    N4 = orbit_numerator(eig_coords_to_e(4, 4, m), m, r)
    f, st = rule_from([N4], m)
    print('hexagon A=4 minimal reps == rule 4850:', f == L.hex_rule(2, 5), st)
    for A, A2 in ((1, 7), (3, 16), (4, 9), (9, 11), (2, 14), (5, 35)):
        Nh = orbit_numerator(eig_coords_to_e(A, A, m), m, r)
        N3 = orbit_numerator(eig_coords_to_e(A2, 3 * A2, m), m, r)
        f, st = rule_from([Nh, N3], m)
        if f is None:
            print(A, A2, st); continue
        op = L.odd_part(f, m)
        rn = L.rule_number(f)
        rad = max(max(abs(a), abs(b)) for a, b in f)
        rec = dict(A_hex=A, A_L3=A2, chi_A=L.legendre(A, m), numerator_terms=len(Nh ^ N3), terms=len(f), radius=rad,
                   rule=rn[0] if rn else None, odd_part=op)
        out.append(rec); print(rec, flush=True)
    json.dump(out, open('step11_orbitrules.json', 'w'), indent=1)
