"""Step 12. Diagonal-free realisations.  If every exponent of the numerator N is even, d/dy N vanishes identically, so
f = N/s is 0 on the diagonal classes (lemma (a') of the report) and the nonzero spectrum is the off-diagonal one.
Build N with even representatives (in (-m, m)) for the ninth-level pairs of step 9 at 37 and compute odd parts."""
import sys, json
import famlib as L
from step11_orbitrules import orbit_numerator, eig_coords_to_e


def evenrep(x, m):
    x %= m
    y = x - m if x > m // 2 else x
    if y % 2:
        y = y - m if y > 0 else y + m
    return y


def even_numerator(e, m, r):
    pts = orbit_numerator(e, m, r)            # small reps
    return {(evenrep(a, m), evenrep(b, m)) for a, b in pts}


def build(parts, m, r):
    G = set()
    for (A, B) in parts:
        G ^= even_numerator(eig_coords_to_e(A, B, m), m, r)
    assert not any(a == b or a == -b for a, b in G)
    return L.quotient_by_s(G)


if __name__ == '__main__':
    m, r = 37, 16
    todo = [('hex(1)+L3(7)', [(1, 1), (7, 21)]),
            ('hex(4) [= f_{2,32}-type, check]', [(4, 4)])]
    out = []
    for name, parts in todo:
        f = build(parts, m, r)
        op = L.odd_part(f, m)
        rad = max(max(abs(a), abs(b)) for a, b in f)
        out.append(dict(name=name, parts=parts, terms=len(f), radius=rad, odd_part=op))
        print(out[-1], flush=True)
    json.dump(out, open('step12_evenreps.json', 'w'), indent=1)
