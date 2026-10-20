"""Step 8. Complete classification of the hexagon family at m = 37 and m = 13.
By the reduction theorem (step 2) the spectrum of f_{p,q} (q = +-r p mod m, m not dividing p) depends only on
k = ind_2(p) mod e (e = 18 at 37, 6 at 13; 2 is a primitive root, W and t_al t_be lie in F(2^e)) and on whether
p = q mod 2.  So the odd part of every member is one of 2e numbers: computed here from one representative per
(k, parity) with linear-atlas-3/eigen.odd_part on the polynomial itself."""
import json
import famlib as L

out = {}
for m, r, e in ((37, 16, 18), (13, 6, 6)):
    ind = {pow(2, k, m): k for k in range(m - 1)}
    rows = []
    for k in range(e):
        for same in (True, False):
            best = None
            for p in range(1, 2 * m):
                if p % m == 0 or ind[p % m] % e != k:
                    continue
                for q in range(1, 2 * m):
                    if (q - r * p) % m and (q + r * p) % m:
                        continue
                    if ((p - q) % 2 == 0) != same:
                        continue
                    rad = max(2 * p, q)
                    if best is None or rad < best[0]:
                        best = (rad, p, q)
            _, p, q = best
            f = L.hex_rule(p, q)
            op = L.odd_part(f, m)
            pred = None
            if m == 37:
                pred = 29127 if L.legendre(p, m) == -1 else 87381
            else:
                pred = 21 if (L.legendre(p, m) == -1 and same) else 63
            rows.append(dict(k=k, same_parity=same, p=p, q=q, chi_p=L.legendre(p, m), terms=len(f), odd_part=op, predicted=pred))
            print(m, rows[-1], flush=True)
    out[m] = rows
    print('m = %d: %d classes, all agree with the rule: %s' % (m, len(rows), all(x['odd_part'] == x['predicted'] for x in rows)))
json.dump(out, open('step8_classify.json', 'w'), indent=1)
