"""Band maxima of d/sqrt(n) sit at step positions; size of the parity sawtooth vs the trend."""
from common import *
import numpy as np
E = ENTRIES
print("band maxima (50-wide), where attained:")
for lo in range(0, 400, 50):
    es = [e for e in E if lo < e["n"] <= lo + 50]
    if not es: continue
    b = max(es, key=lambda e: e["d"] / math.sqrt(e["n"]))
    b2 = max(es, key=lambda e: e["d"] / math.sqrt(e["n"] * math.log(e["n"])))
    print(f"  ({lo},{lo+50}]: max d/sqrt(n) {b['d']/math.sqrt(b['n']):.3f} at [[{b['n']},{b['k']},{b['d']}]]; "
          f"max d/sqrt(n ln n) {b2['d']/math.sqrt(b2['n']*math.log(b2['n'])):.3f} at [[{b2['n']},{b2['k']},{b2['d']}]]")
rows = json.load(open("groups.json"))
top = defaultdict(int)
for r in rows:
    top[r["n"]] = max(top[r["n"]], r["dbest"])
comb = sorted(n for n in top if (n // 2) % 3 == 0)
pl = defaultdict(list)
for n in comb:
    pl[top[n]].append(n)
print("\nplateaus on the 6-comb: d, first n, last n, ratio first->last, drop")
for d, ns in sorted(pl.items()):
    a, b = d / math.sqrt(ns[0]), d / math.sqrt(ns[-1])
    print(f"  d={d:2d} n {ns[0]}..{ns[-1]} ({len(ns)} cols)  d/sqrt(n) {a:.3f} -> {b:.3f}  drop {1-b/a:.1%}   "
          f"d/sqrt(n ln n) {d/math.sqrt(ns[0]*math.log(ns[0])):.3f} -> {d/math.sqrt(ns[-1]*math.log(ns[-1])):.3f}")
print("\nquantum in ratio units 2/sqrt(n): n=150 %.3f, n=300 %.3f, n=400 %.3f" % (2/math.sqrt(150), 2/math.sqrt(300), 2/math.sqrt(400)))
print("quantum relative to d: d=12 %.1f%%, d=20 %.1f%%, d=28 %.1f%%" % (200/12, 200/20, 200/28))
