"""How much of the column-top sequence on n = 0 mod 6 is 'smooth curve, floored to even'?
Grid-search 2-parameter curves; count columns reproduced exactly by d = 2*floor(f(n)/2)."""
from common import *
import numpy as np

rows = json.load(open("groups.json"))
top = defaultdict(int)
for r in rows:
    top[r["n"]] = max(top[r["n"]], r["dbest"])
comb = sorted(n for n in top if (n // 2) % 3 == 0)
n = np.array(comb, float); d = np.array([top[x] for x in comb], float)
# all columns with k_min in {4,6}
k46 = sorted(x for x in top if (x // 2) % 3 == 0 or (x // 2) % 7 == 0)
n2 = np.array(k46, float); d2 = np.array([top[x] for x in k46], float)

fams = {
    "a*sqrt(n)+b": lambda n, a, b: a * np.sqrt(n) + b,
    "a*sqrt(n ln n)+b": lambda n, a, b: a * np.sqrt(n * np.log(n)) + b,
    "a*n^b": lambda n, a, b: a * n ** b,
    "a*sqrt(n)": lambda n, a, b: a * np.sqrt(n),
    "a*sqrt(n ln n)": lambda n, a, b: a * np.sqrt(n * np.log(n)),
}
grids = {
    "a*sqrt(n)+b": (np.linspace(1.0, 2.5, 601), np.linspace(-10, 4, 281)),
    "a*sqrt(n ln n)+b": (np.linspace(0.4, 1.0, 601), np.linspace(-8, 6, 281)),
    "a*n^b": (np.linspace(0.3, 1.5, 601), np.linspace(0.45, 0.8, 351)),
    "a*sqrt(n)": (np.linspace(1.0, 2.0, 2001), np.array([0.0])),
    "a*sqrt(n ln n)": (np.linspace(0.4, 0.9, 2001), np.array([0.0])),
}
for name, f in fams.items():
    for lab, (NN, DD) in (("6-comb (63 cols)", (n, d)), ("k_min 4 or 6 (80 cols)", (n2, d2))):
        best = (-1, None)
        A, B = grids[name]
        for a in A:
            for b in B:
                pred = 2 * np.floor(f(NN, a, b) / 2)
                s = int((pred == DD).sum())
                if s > best[0]:
                    best = (s, (round(a, 4), round(b, 4)))
        # also nearest-even rounding
        best2 = (-1, None)
        for a in A:
            for b in B:
                pred = 2 * np.round(f(NN, a, b) / 2)
                s = int((pred == DD).sum())
                if s > best2[0]:
                    best2 = (s, (round(a, 4), round(b, 4)))
        print(f"{name:18s} {lab:24s} floor-to-even exact {best[0]}/{len(DD)} at {best[1]};  "
              f"round-to-even exact {best2[0]}/{len(DD)} at {best2[1]}")
# null: what does a 'random monotone staircase' give? compare with a pure-step baseline:
print("\nbaseline: predict each column by its left neighbour's top:",
      int((d[1:] == d[:-1]).sum()), "of", len(d) - 1)
