"""Independent check of the 'theory' claim: sqrt(n ln n) vs n^b indistinguishable on n=50-400,
plain sqrt and n^(3/4) worse, separation ~1 even step at n~1000, 5 steps at n~2000."""
import json, math, collections
import numpy as np
from scipy.optimize import least_squares

D = json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E = D['entries']

# per-n best d (isomorphic tori share n, so max-by-n is already deduplicated)
F = collections.defaultdict(int)
stage = {}
for e in E:
    F[e['n']] = max(F[e['n']], e['d'])
    stage[e['n']] = e['stage']
ns = np.array(sorted(F)); Fd = np.array([F[n] for n in ns], float)

# selections
first = {}  # first n reaching each d (n>=48 filter applied after)
for n, d in zip(ns, Fd):
    for dd in range(2, int(d) + 1, 2):
        if dd not in first:
            first[dd] = n
fr = sorted((n, d) for d, n in first.items() if n >= 48)
# true "record" points: strictly new maximum
strict = []; m = 0
for n, d in zip(ns, Fd):
    if d > m:
        strict.append((n, d)); m = d
strict = [(n, d) for n, d in strict if n >= 48]
# their staircase (non-decreasing points incl. plateau)
stair = []; m = 0
for n, d in zip(ns, Fd):
    if d >= m and n >= 48:
        stair.append((n, d))
    m = max(m, d)
allp = [(n, d) for n, d in zip(ns, Fd) if n >= 48]

print("first-reach points (n>=48):", [(int(a), int(b)) for a, b in fr])
print("strict-record points:", [(int(a), int(b)) for a, b in strict])
print("counts: first-reach %d, staircase %d, all-n %d" % (len(fr), len(stair), len(allp)))
print("n with F(n) below running max (dropped by staircase):",
      [(int(n), int(d)) for n, d in allp if (n, d) not in stair])

forms = {
    'c sqrt(n)': (lambda n, p: p[0] * np.sqrt(n), [1.0]),
    'c sqrt(n ln n)': (lambda n, p: p[0] * np.sqrt(n * np.log(n)), [0.6]),
    'c n^b': (lambda n, p: p[0] * n ** p[1], [0.7, 0.6]),
    'c n^(2/3)': (lambda n, p: p[0] * n ** (2 / 3), [0.5]),
    'c n^(3/4)': (lambda n, p: p[0] * n ** 0.75, [0.3]),
    'sqrt(n)(a+b ln n)': (lambda n, p: np.sqrt(n) * (p[0] + p[1] * np.log(n)), [0.3, 0.2]),
    'c sqrt(n) (ln n)^g': (lambda n, p: p[0] * np.sqrt(n) * np.log(n) ** p[1], [0.6, 0.5]),
}

def fit(name, pts):
    f, p0 = forms[name]
    n = np.array([a for a, b in pts], float); d = np.array([b for a, b in pts], float)
    r = least_squares(lambda p: f(n, p) - d, p0)
    res = f(n, r.x) - d
    return r.x, math.sqrt(np.mean(res ** 2)), np.abs(res).max(), res

for label, pts in [('STAIRCASE (theirs)', stair), ('FIRST-REACH', fr), ('ALL n>=48 (F(n))', allp)]:
    print("\n==", label, "N=%d" % len(pts))
    for name in forms:
        p, rms, mx, res = fit(name, pts)
        f = forms[name][0]
        print("  %-20s p=%s rms=%.3f max|res|=%.2f  pred1000=%.1f pred2000=%.1f" % (
            name, np.round(p, 4), rms, mx, f(1000, p), f(2000, p)))

# Residual sign structure of c sqrt(n ln n) on first-reach points vs n^b
print("\nresiduals (fit-d) on first-reach points:")
for name in ['c sqrt(n)', 'c sqrt(n ln n)', 'c n^b', 'c n^(3/4)']:
    p, rms, mx, res = fit(name, fr)
    print("  %-16s" % name, np.round(res, 2))

# 1.7% claim: spread of sqrt(n ln n)/n^b on [50,400] for b in 0.60..0.65
nn = np.linspace(50, 400, 2001)
print("\nshape spread max/min of sqrt(n ln n)/n^b on [50,400]:")
for b in [0.58, 0.59, 0.60, 0.603, 0.607, 0.61, 0.62, 0.63, 0.64, 0.6413, 0.65]:
    r = np.sqrt(nn * np.log(nn)) / nn ** b
    print("  b=%.4f spread=%.2f%%  (=> best-c max rel dev ~ +-%.2f%%)" % (b, 100 * (r.max() / r.min() - 1), 50 * (r.max() / r.min() - 1)))
print("local log-slope of sqrt(n ln n): n=50 %.3f, n=100 %.3f, n=200 %.3f, n=400 %.3f, n=1000 %.3f" %
      tuple(0.5 + 0.5 / math.log(x) for x in [50, 100, 200, 400, 1000]))

# separation of the two fitted curves (in units of an even step = 2)
def sep_table(pts, label):
    p1, *_ = fit('c sqrt(n ln n)', pts); p2, *_ = fit('c n^b', pts)
    f1 = forms['c sqrt(n ln n)'][0]; f2 = forms['c n^b'][0]
    grid = np.arange(50, 20001)
    diff = f2(grid, p2) - f1(grid, p1)
    out = []
    inr = (grid >= 48) & (grid <= 400)
    out.append("max |diff| in [50,400] = %.2f" % np.abs(diff[inr]).max())
    for steps in [1, 2, 3, 5]:
        idx = np.where((grid > 400) & (np.abs(diff) >= 2 * steps))[0]
        out.append("%d step(s) (|diff|>=%d) first at n=%s" % (steps, 2 * steps, grid[idx[0]] if len(idx) else 'never<=20000'))
    for N in [400, 600, 1000, 2000]:
        out.append("n=%d: sqrt(nlnn)=%.1f n^b=%.1f diff=%.1f" % (N, f1(N, p1), f2(N, p2), f2(N, p2) - f1(N, p1)))
    print("\nseparation using fits on", label, "b=%.4f" % p2[1], "\n  " + "\n  ".join(out))
sep_table(stair, 'STAIRCASE'); sep_table(fr, 'FIRST-REACH'); sep_table(allp, 'ALL n')

# Out-of-sample: fit on n<=300 (stages 3a/3b/3c), predict stage-4 n (302..400)
print("\nOUT-OF-SAMPLE: fit on n<=300, test on n>300 (stage 4, ~75% complete)")
for label, pts in [('staircase', stair), ('first-reach', fr), ('all-n', allp)]:
    train = [(n, d) for n, d in pts if n <= 300]; test = [(n, d) for n, d in pts if n > 300]
    print(" ", label, "train %d test %d" % (len(train), len(test)))
    for name in forms:
        p, *_ = fit(name, train)
        f = forms[name][0]
        tn = np.array([a for a, b in test], float); td = np.array([b for a, b in test], float)
        res = f(tn, p) - td
        print("    %-20s test rms=%.3f mean=%.2f  b=%s" % (name, math.sqrt(np.mean(res ** 2)), res.mean(), np.round(p, 3)))

# Bootstrap over d-levels (first-reach) for b and for the sep at 1000
rng = np.random.default_rng(1)
frn = np.array(fr, float)
bs_b = []; bs_sep = []; bs_lng = []
for _ in range(2000):
    idx = rng.integers(0, len(frn), len(frn))
    pts = [tuple(frn[i]) for i in idx]
    if len(set(p[0] for p in pts)) < 3: continue
    p2, *_ = fit('c n^b', pts); p1, *_ = fit('c sqrt(n ln n)', pts); p3, *_ = fit('c sqrt(n) (ln n)^g', pts)
    bs_b.append(p2[1]); bs_lng.append(p3[1])
    bs_sep.append(forms['c n^b'][0](1000, p2) - forms['c sqrt(n ln n)'][0](1000, p1))
print("\nbootstrap (first-reach, resample d-levels): b 2.5/50/97.5%% = %s ; log-exponent g = %s ; sep@1000 = %s" % (
    np.round(np.percentile(bs_b, [2.5, 50, 97.5]), 3), np.round(np.percentile(bs_lng, [2.5, 50, 97.5]), 3),
    np.round(np.percentile(bs_sep, [2.5, 50, 97.5]), 2)))
