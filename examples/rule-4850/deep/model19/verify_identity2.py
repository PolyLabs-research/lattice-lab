"""Exact group-ring checks, F2[Z_37^2] (verify_identity.py helpers):
 (H)  4850 * s = Hex(x,y) + Hex(y,x), Hex = {+-(4,0), +-(2,5), +-(2,-5)}  (Laurent identity, any size)
 (Minv) G = 4850*s is invariant under M = [[19,8],[8,19]];  G' = 10491524*ab under diag(27, 11)
 (Dil) 20982139*ab = (10491524*ab)^[27],  178279803*ab = (10491524*ab)^[26]   (dilations of the 12-term G')
 (Q)  q^2 + 3 p^2 = 25 + 12 = 37: the two hexagons' 120-degree rotations agree mod 37 (and mod no other prime)."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census
from verify_identity import arr, mul, dil, S, AB

out = {}
f = arr(census.rule(4850, 4))
G = mul(f, S)
Hex = arr({(4, 0), (-4, 0), (2, 5), (-2, -5), (2, -5), (-2, 5)})
out['H'] = bool(np.array_equal(G, Hex ^ Hex.T))
out['Minv_4850'] = bool(np.array_equal(dil(G, ((19, 8), (8, 19))), G))
G1 = mul(arr(census.rule(10491524, 6)), AB)
out['Minv_10491524'] = bool(np.array_equal(dil(G1, ((27, 0), (0, 11))), G1))
out['Dil_20982139'] = bool(np.array_equal(mul(arr(census.rule(20982139, 6)), AB), dil(G1, ((27, 0), (0, 27)))))
out['Dil_178279803'] = bool(np.array_equal(mul(arr(census.rule(178279803, 6)), AB), dil(G1, ((26, 0), (0, 26)))))
# rotation of 4850's frame to 10491524's: (x, y) -> (xy, x/y) on exponents: (p,q) -> (p+q, p-q)
R = ((1, 1), (1, 36))
out['rotation_4850_to_10491524'] = bool(np.array_equal(dil(f, R), arr(census.rule(10491524, 6))))
print(out)
json.dump(out, open('verify_identity2.json', 'w'), indent=1)
