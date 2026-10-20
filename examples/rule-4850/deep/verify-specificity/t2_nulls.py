"""t2 (claim 1c, 1d): null rates, recomputed from scratch.

(1d-exact) the 3-adic (digit2) symmetry null: ALL 3^10 Frobenius-odd D4-symmetric digit functions on the 1368
    characters (class (1,6) forced 0), exhaustively: the fraction invariant under P_g^A = diag(1, 2^g) or
    P_g^B = Rot^-1 diag(1, 2^g) Rot (g = 1..17); per-P counts; the invariant-subspace dimensions.
(1d-empirical) the mu3-symbol (log mod 3) of real rules: every radius-4 rule and a random sample of radius-5 rules
    with no zero eigenvalue and not cube-confined: rate of invariance under g1 = P_6^B (4850's frame) and under any
    P_g; values from own F(2^36) at the 11 class representatives, expanded with own bookkeeping (c37), and the
    expansion checked against direct evaluation at all 1368 characters for 40 rules.
(1c) the partial-twist relation (grouping): R1 = 10491524, r = diag(1, 27) on exponents.  For 1000 random
    zero-free radius-6 rules X: is log X on the 36 off-axis lines in span{log R1, log rR1, log r^2R1} mod 19,
    mod 27?  R2 = 20982139, R3 = 178279803 as positive controls; and the same membership for confined rules
    (own radius-4 list + recorded radius-5/6 lists) to measure specificity among confined rules."""
import sys, json, time, itertools
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
import c37
t0 = time.time()
out = {}
M = 37
L = S.Logs37(); E = L.E; F = E.F
KEYS = [(g, fr) for g in range(1, 18) for fr in 'AB']
PERMS = {k: c37.perm(c37.partial(*k)) for k in KEYS}
# ---------------------------------------------------------------- 1d exact
free = [i for i in range(c37.NCL) if not any(k % 2 for k in c37.STAB[i])]
print('free classes for a Frobenius-odd digit function:', [c37.REPS[i] for i in free])
X = np.array(list(itertools.product(range(3), repeat=len(free))), dtype=np.int64)  # (3^10, 10)
cv = np.zeros((c37.NCL, X.shape[0]), dtype=np.int64)
cv[free, :] = X.T
# digit functions: delta(2^i g rep) = 2^i delta(rep) = (-1)^i delta(rep) mod 3
D = c37.expand(cv, 3).astype(np.int8)  # (1368, 59049)
# consistency of the expansion: delta(2c) = -delta(c), delta(gc) = delta(c) (by construction; check a few)
any_inv = np.zeros(X.shape[0], dtype=bool)
per = {}
for k, p in PERMS.items():
    inv = np.all(D[p] == D, axis=0)
    per['g=%d,%s' % k] = int(inv.sum()) - 1  # exclude the zero pattern
    any_inv |= inv
nonzero = np.any(X != 0, axis=1)
out['digit2_exact'] = dict(patterns=int(X.shape[0]), nonzero=int(nonzero.sum()),
                           any_partial_symmetry=int((any_inv & nonzero).sum()),
                           rate_any=float((any_inv & nonzero).sum() / nonzero.sum()),
                           per_P=per, rate_P6B=(per['g=6,B']) / int(nonzero.sum()),
                           dims={k: round(float(np.log(v + 1) / np.log(3)), 3) for k, v in per.items()})
print('1d exact:', {k: v for k, v in out['digit2_exact'].items() if k not in ('per_P', 'dims')})
print('   per-P invariant nonzero patterns:', per)
del D
# ---------------------------------------------------------------- 1d empirical (mu3 symbols of real rules)
def orbit_values(r, chars):
    vals = []
    for o in S.orbits(r):
        pts = S.orbit_points(*o)
        v = []
        for j, k in chars:
            x = 0
            for p, q in pts:
                x ^= int(E.zp[(p * j + q * k) % M])
            v.append(x)
        vals.append(v)
    return np.array(vals, dtype=np.uint64)  # (n_orbits, n_chars)
def rule_class_values(r, ids):
    ov = orbit_values(r, c37.REPS)  # (no, 11)
    no = ov.shape[0]
    ids = np.asarray(ids, dtype=np.int64)
    out_ = np.zeros((c37.NCL, ids.size), dtype=np.uint64)
    for i in range(no):
        sel = ((ids >> i) & 1).astype(bool)
        out_[:, sel] ^= ov[i][:, None]
    return out_
emp = {}
rng = np.random.default_rng(20261020)
for r, ids in ((4, np.arange(1, 1 << 15)), (5, rng.choice(np.arange(1, 1 << 21), 300000, replace=False))):
    V = rule_class_values(r, ids)
    nz = np.all(V != 0, axis=0)
    l3 = np.full(V.shape, -1, dtype=np.int64)
    w = F.vpow(V[:, nz], L.N18 // 3)
    lut = L.tab[3]
    l3[:, nz] = np.vectorize(lambda x: lut[int(x)])(w)
    cube = nz & np.all(l3 == 0, axis=0)
    sel = nz & ~cube
    sym = c37.expand(l3[:, sel], 3)  # (1368, nsel)
    rec = {'rules': int(ids.size), 'zero_free': int(nz.sum()), 'used(zero-free, not cube)': int(sel.sum())}
    anyP = np.zeros(sel.sum(), dtype=bool)
    for k, p in PERMS.items():
        inv = np.all(sym[p] == sym, axis=0)
        anyP |= inv
        if k == (6, 'B'):
            rec['g1=P6B'] = int(inv.sum()); rec['rate_g1'] = float(inv.mean())
    rec['any_P'] = int(anyP.sum()); rec['rate_any_P'] = float(anyP.mean())
    emp[r] = rec
    print('1d empirical radius', r, rec)
    if r == 4:
        V4 = V; ids4 = ids
out['mu3_symbol_empirical'] = emp
# expansion check against direct evaluation at all characters, 40 radius-4 zero-free rules
chk = 0
for n in rng.choice(np.flatnonzero(np.all(V4 != 0, axis=0)) + 1, 40, replace=False):
    f = S.rule(int(n), 4)
    v = E.values(f)
    direct = L.log(np.array([v[c] for c in c37.NZ], dtype=np.uint64), 27)
    cl = L.log(V4[:, int(n) - 1], 27)
    exp = c37.expand(cl[:, None], 27)[:, 0]
    chk += int(np.array_equal(direct, exp))
out['expansion_check_40'] = chk
print('expansion (class -> all characters) agrees with direct evaluation on', chk, 'of 40 rules')
# ---------------------------------------------------------------- 1c partial twist
LINES = [(1, k) for k in range(M)] + [(0, 1)]
OFF = [i for i, c in enumerate(LINES) if c not in ((1, 0), (0, 1))]
def line_logs(pts, mod):
    v = E.values(pts)
    vals = np.array([v[c] for c in LINES], dtype=np.uint64)
    if np.any(vals == 0):
        return None
    return L.log(vals, mod)
def twist(pts, i):
    u = pow(27, i, M)
    return frozenset((p, (u * q) % M if True else q) for p, q in pts)
R1 = S.rule(10491524, 6)
cols19 = [line_logs(twist(R1, i), 19)[OFF] for i in range(3)]
cols27 = [line_logs(twist(R1, i), 27)[OFF] for i in range(3)]
def rank_mod_p(A, p):
    A = [list(map(int, r)) for r in A]
    rk = 0; ncol = len(A[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(A)) if A[i][c] % p), None)
        if piv is None:
            continue
        A[rk], A[piv] = A[piv], A[rk]
        iv = pow(A[rk][c], -1, p)
        A[rk] = [x * iv % p for x in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c] % p:
                f_ = A[i][c]
                A[i] = [(x - f_ * y) % p for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk
r19 = rank_mod_p(cols19, 19)
G27 = np.array(list(itertools.product(range(27), repeat=3)), dtype=np.int64)
A27 = np.stack(cols27) % 27
SPAN27 = (G27 @ A27) % 27
span27_set = {tuple(r) for r in SPAN27}
def member(b19, b27):
    in19 = rank_mod_p(cols19 + [b19], 19) == r19
    in27 = tuple(int(x) for x in b27 % 27) in span27_set
    return in19, in27
out['twist_span_rank_mod19'] = r19
out['twist_span27_all_multiples_of_9'] = bool(np.all(SPAN27 % 9 == 0))
ctrl = {}
for n in (20982139, 178279803, 10491524):
    f = S.rule(n, 6)
    ctrl[n] = member(line_logs(f, 19)[OFF], line_logs(f, 27)[OFF])
out['twist_controls'] = ctrl
print('partial twist: rank of span mod 19 =', r19, '; span mod 27 lies in 9Z/27:', out['twist_span27_all_multiples_of_9'], '; controls (in19, in27):', ctrl)
tried = n19 = n27 = nboth = notninth = 0
while tried < 1000:
    x = int(rng.integers(1, 1 << 28))
    f = S.rule(x, 6)
    b19 = line_logs(f, 19)
    if b19 is None:
        continue
    b27 = line_logs(f, 27)
    tried += 1
    a, b = member(b19[OFF], b27[OFF])
    n19 += a; n27 += b; nboth += a and b
    notninth += bool(np.any(b27[OFF] % 9))
out['twist_random'] = dict(tried=tried, in_span_mod19=n19, in_span_mod27=n27, both=nboth,
                           random_rules_with_some_offaxis_log_not_0_mod_9=notninth)
print('random zero-free radius-6 rules:', out['twist_random'])
# confined rules: own radius-4 confined list + recorded radius-5/6
conf = []
l9 = np.full(V4.shape, -1, dtype=np.int64)
nz4 = np.all(V4 != 0, axis=0)
for n in np.flatnonzero(nz4) + 1:
    vv = V4[:, n - 1]
    if np.all(F.vpow(vv, L.N18 // 9) == 1):
        conf.append((int(n), 4))
d = json.load(open('/home/user/lattice-lab/examples/llm-pilot-37c/data/ninth37.json'))
own4 = sorted(n for n, r in conf)
rec4 = sorted(r['id'] for fam in d['families'] if fam['radius'] == 4 for r in fam['ninth_power_rules'])
out['own_radius4_zero_free_ninth'] = own4
print('own radius-4 zero-free ninth-confined:', len(own4), ' (recorded radius-4 ninth list, incl. zero-allowing:', len(rec4), ')')
for fam in d['families']:
    if fam['radius'] == 5:
        conf += [(r['id'], 5) for r in fam['ninth_power_rules']]
for line in open('/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl'):
    r = json.loads(line)
    if 'id' in r:
        conf.append((r['id'], 6))
hits = []; nontriv = []; checked = 0
for n, r in sorted(set(conf)):
    f = S.rule(n, r)
    b19 = line_logs(f, 19)
    if b19 is None:
        continue
    checked += 1
    b27 = line_logs(f, 27)
    a, b = member(b19[OFF], b27[OFF])
    if a and b:
        hits.append(n)
        if np.any(b19[OFF] % 19):
            nontriv.append(n)
out['twist_confined'] = dict(zero_free_confined_checked=checked, in_span=len(hits), in_span_with_nonzero_19part=len(nontriv),
                             rules_nonzero_19part=nontriv)
print('zero-free confined rules checked:', checked, '; in span (mod 19 and 27):', len(hits), '; of which with a nonzero 19-part:', len(nontriv), nontriv)
out['time'] = round(time.time() - t0, 1)
print('time', out['time'])
json.dump(out, open('t2_nulls.json', 'w'), indent=1, default=str)
