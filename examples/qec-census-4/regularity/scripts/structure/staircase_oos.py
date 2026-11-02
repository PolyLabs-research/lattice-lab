"""Misses of the quantized one-parameter curve, and a train(n<=300)/test(n>300) split."""
from common import *
import numpy as np
rows = json.load(open("groups.json"))
top = defaultdict(int)
for r in rows:
    top[r["n"]] = max(top[r["n"]], r["dbest"])
comb = sorted(x for x in top if (x // 2) % 3 == 0)
n = np.array(comb, float); d = np.array([top[x] for x in comb], float)
f1 = lambda n, a: a * np.sqrt(n * np.log(n))
fp = lambda n, a, b: a * n ** b
q = lambda v: 2 * np.floor(v / 2)
pred = q(f1(n, 0.6175))
print("misses of 2*floor(0.6175 sqrt(n ln n)/2):", [(int(a), int(b), int(c)) for a, b, c in zip(n, d, pred) if b != c])
# interval of a consistent with every column: d <= f < d+2  => a in [d/s, (d+2)/s)
s = np.sqrt(n * np.log(n))
lo, hi = d / s, (d + 2) / s
print("a-interval per column; columns where the common interval breaks:")
L, H = -1, 9
for x, a1, a2 in zip(comb, lo, hi):
    L2, H2 = max(L, a1), min(H, a2)
    if L2 >= H2:
        print("   conflict at n =", x, "running interval", (round(L, 4), round(H, 4)), "column", (round(a1, 4), round(a2, 4)))
    else:
        L, H = L2, H2
print("final running interval (skipping conflicts):", round(L, 4), round(H, 4))
# train/test
tr = n <= 300; te = n > 300
for name, grid, f in (("a sqrt(n ln n)", [(a, 0) for a in np.linspace(0.4, 0.9, 5001)], lambda n, a, b: f1(n, a)),
                      ("a n^b", [(a, b) for a in np.linspace(0.3, 1.5, 601) for b in np.linspace(0.45, 0.8, 351)], fp),
                      ("a sqrt(n)+b", [(a, b) for a in np.linspace(1.0, 2.5, 601) for b in np.linspace(-10, 4, 281)],
                       lambda n, a, b: a * np.sqrt(n) + b)):
    sc = [(int((q(f(n[tr], a, b)) == d[tr]).sum()), a, b) for a, b in grid]
    m = max(s_[0] for s_ in sc)
    best = [s_ for s_ in sc if s_[0] == m]
    tests = [int((q(f(n[te], a, b)) == d[te]).sum()) for _, a, b in best]
    print(f"{name:15s} train exact {m}/{tr.sum()} ({len(best)} tied params); test exact over tied params: "
          f"min {min(tests)}, max {max(tests)} of {te.sum()}")
