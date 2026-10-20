"""Check nf.py against census.py (independent F(2^36) model) and eigen.odd_part."""
import sys, time
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import numpy as np
import nf
import census, eigen

t0 = time.time()
nf.tables(); T = nf.tvec()
print('tables', time.time() - t0)
lt = census.log_table()
def census_logs(n, r):
    f = census.rule(n, r)
    zeta = [census.power(2, e) for e in range(37)]
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in f:
            v ^= zeta[(p * j + q * k) % 37]
        out.append(int(lt[census.coord(v)]))
    return out
assert census.characters() == nf.CLASSES, census.characters()
rules = [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6), (7, 1), (90 and 2, 1)]
units = None
for n, r in rules:
    a = nf.class_v27(nf.vrule(n, r))
    b = census_logs(n, r)
    # find unit u with a = u b mod 27 (zero-marks aside)
    cand = [u for u in range(27) if u % 3 and all((x == -1 and y == 255) or (x != -1 and y != 255 and x % 27 == u * y % 27) for x, y in zip(a, b))]
    print(n, r, 'nf v27', a, 'census', b, 'units', cand, 'ninth-confined (nf, all chars):', nf.is_ninth_confined(nf.vrule(n, r)))
    units = set(cand) if units is None else units & set(cand)
print('common unit relating the two log conventions:', units)
for n, r in [(4850, 4), (20982139, 6), (178279803, 6), (10491524, 6)]:
    o = eigen.odd_part(census.rule(n, r), 37)
    print('eigen.odd_part', n, o, '29127 % o =', 29127 % o)
