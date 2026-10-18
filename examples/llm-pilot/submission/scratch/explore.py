import sys
sys.path.insert(0, "/home/user/pilot-sandbox/tools")
from tori import square, hexagon, torus, period, H1
for m in [3, 5, 7, 9]:
    Pm = period(square(m), H1)
    sub = torus(2*m, m, lambda d: (d[0] + 2*d[1], d[1]))
    Ps = period(sub, H1)
    print("m", m, "P(m)", Pm, "P(G')", Ps)
    for v in [1, 2]:
        n = 2**v * m
        if 2*n * (n//2) > 400: continue
        Ph = period(hexagon(n), H1)
        print("  v", v, "n", n, "hexPeriod", Ph, "ratio", Ph / Pm, "2^(v+1)", 2**(v+1))
