"""Which of 4850's 11 classes are forced by the hexagon structure, and which two are free.
4850 class (j, k) -> diagonal coordinates alpha = (j+k)/2, beta = (j-k)/2 -> d = ind(beta/alpha) mod 6,
up to d ~ -d (swap).  d = 0: W(A,A) = A^2 (forced);  d = 3: the F(2^9) class of 10491524 (forced);
d in {1,5} and {2,4}: free.  Axis classes (alpha or beta = 0) are 4850's diagonal-type... handled separately."""
import json
import ff18 as F
h = pow(2, -1, 37)
out = {}
for j, k in F.CLASSES:
    al, be = (j + k) * h % 37, (j - k) * h % 37
    if al == 0 or be == 0:
        out[str((j, k))] = dict(alpha=al, beta=be, d=None, status='s = 0 here (j = +-k): value from the polynomial (4850 diagonal class, cyclotomic)')
        continue
    d = (F.ind37(be) - F.ind37(al)) % 6
    dd = min(d, (-d) % 6)
    status = {0: 'forced (W = A^2 class)', 3: 'forced (F(2^9) class)', 1: 'FREE #1', 2: 'FREE #2'}[dd]
    out[str((j, k))] = dict(alpha=al, beta=be, d=d, status=status)
for c, v in out.items():
    print(c, v)
json.dump(out, open('classmap.json', 'w'), indent=1)
