"""t1 (claim 1a, 1b): specificity of the shape 'pi * f is a single <D4,T>-orbit' (T = diag(10, 26)), from scratch.

(a) Orbits of <D4, T> on (Z/37)^2 off the axes, computed here by closure.  For every orbit O, G_O = sum of x^c over
    the centred lift of O; f_O = G_O / pi by exact Laurent division (own ldiv).  Completeness for radius <= 6: if f has
    radius <= 6 then pi*f has radius <= 7 < 37/2, so its support mod 37 lifts uniquely to the centred box, and pi*f
    = (single orbit O) forces f = f_O.  So the radius-<=6 rules with the shape are exactly the f_O of radius <= 6.
    Each f_O: full confinement (cube / ninth / 27th) by exact group ring, and eigenvalues in own F(2^36), and
    eigen.odd_part for the radius <= 6 ones.  Same for unions of orbits in the box (to see the shape is not generic).
(b) all 45 24-point orbits: is f_O = G_O/pi confined (full rule, axes included)?
(c) the same in 4850's frame: s * f a union of <D4, M0>-orbits, M0 = [[18,29],[29,18]], radius <= 6.
(d) cross-check against the recorded ninth-power rules (radius 4, 5 from data/ninth37.json; radius 6 from
    llm-pilot-37c/records.jsonl): which recorded confined rules have pi*f (resp. s*f) a single <D4,T>- (<D4,M0>-) orbit."""
import sys, json, time, itertools
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen
t0 = time.time()
m = 37
GR = S.GroupRing(m); E = S.Eig(m)
D4 = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
      ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
def act(g, c):
    return ((g[0][0] * c[0] + g[0][1] * c[1]) % m, (g[1][0] * c[0] + g[1][1] * c[1]) % m)
def closure_orbits(gens, pts):
    seen, orbs = set(), []
    for c in pts:
        if c in seen:
            continue
        O = {c}; fr = [c]
        while fr:
            nf = []
            for x in fr:
                for g in gens:
                    y = act(g, x)
                    if y not in O:
                        O.add(y); nf.append(y)
            fr = nf
        seen |= O; orbs.append(frozenset(O))
    return orbs
cen = lambda p: (p % m) - m if (p % m) > m // 2 else (p % m)
def lift(O):
    return frozenset((cen(p), cen(q)) for p, q in O)
def status(pts, with_odd=False):
    a = GR.elem(pts); v = E.values(pts)
    rec = dict(cube=GR.confined(a, 3), ninth=GR.confined(a, 9), q27=GR.confined(a, 27),
               eig_ninth=E.confined(v, 9), zero_chars=int((v == 0).sum()))
    assert rec['ninth'] == rec['eig_ninth']
    if with_odd:
        rec['odd_part'] = eigen.odd_part(frozenset(pts), m)
        rec['odd_divides_29127'] = 29127 % rec['odd_part'] == 0
    return rec
out = {}
T = ((10, 0), (0, 26)); M0 = ((18, 29), (29, 18))
offax = [(p, q) for p in range(1, m) for q in range(1, m)]
allnz = [(p, q) for p in range(m) for q in range(m) if (p, q) != (0, 0)]
# ---------------- (a), (b): T frame
orbs = closure_orbits(D4 + [T], offax)
sizes = sorted(len(O) for O in orbs)
out['T_orbits_off_axes'] = {'count': len(orbs), 'size_hist': {s: sizes.count(s) for s in set(sizes)}}
print('T frame: <D4,T>-orbits off the axes:', out['T_orbits_off_axes'])
rows = []
for O in sorted(orbs, key=lambda o: (len(o), S.radius_of(lift(o)), sorted(lift(o)))):
    G = lift(O)
    f, R = S.ldiv(G, S.PI_POLY)
    assert not R and S.lmul(f, S.PI_POLY) == G
    r = S.radius_of(f)
    n, rr = S.rule_number(f)
    st = status(f, with_odd=(r <= 6))
    rows.append(dict(size=len(O), rep=min(O), lift_radius=S.radius_of(G), f_radius=r, f_terms=len(f),
                     rule=(n if r <= 6 else None), **st))
out['T_rows'] = rows
small = [x for x in rows if x['f_radius'] <= 6]
print('orbits with f_O of radius <= 6:', [(x['size'], x['rep'], x['rule'], x['ninth'], x.get('odd_part')) for x in small])
for size in (12, 24):
    sub = [x for x in rows if x['size'] == size]
    print('size %d: %d orbits; f_O = G_O/pi cube-confined %d, ninth-confined %d, 27th %d; radii %s' % (
        size, len(sub), sum(x['cube'] for x in sub), sum(x['ninth'] for x in sub), sum(x['q27'] for x in sub),
        sorted({x['f_radius'] for x in sub})))
out['summary_T'] = {s: dict(n=len([x for x in rows if x['size'] == s]),
                            cube=sum(x['cube'] for x in rows if x['size'] == s),
                            ninth=sum(x['ninth'] for x in rows if x['size'] == s)) for s in (12, 24)}
# unions of the orbits whose lift lies in the box |.| <= 7 (needed for radius <= 6)
box = [O for O in orbs if S.radius_of(lift(O)) <= 7]
print('orbits whose lift lies in the box 7:', [(len(O), min(O)) for O in box])
uni = []
for k in range(1, len(box) + 1):
    for combo in itertools.combinations(range(len(box)), k):
        G = frozenset().union(*[lift(box[i]) for i in combo])
        f, R = S.ldiv(G, S.PI_POLY)
        if R or not f or S.radius_of(f) > 6:
            continue
        n, rr = S.rule_number(f)
        st = status(f)
        uni.append(dict(orbits=[min(box[i]) for i in combo], rule=n, radius=rr, **st))
out['T_unions_in_box'] = uni
for u in uni:
    print('   union', u['orbits'], '-> rule', u['rule'], 'r', u['radius'], 'ninth', u['ninth'], 'cube', u['cube'])
# ---------------- (c): 4850's frame, s * f
orbsM = closure_orbits(D4 + [M0], allnz)
boxM = [O for O in orbsM if S.radius_of(lift(O)) <= 7]
print('M0 frame: <D4,M0>-orbits on nonzero points:', len(orbsM), ' in the box 7:', [(len(O), sorted(lift(O))[:2]) for O in boxM])
uniM = []
# include the origin (s*f may contain the constant term)
boxM_all = boxM + [frozenset({(0, 0)})]
for k in range(1, len(boxM_all) + 1):
    for combo in itertools.combinations(range(len(boxM_all)), k):
        G = frozenset().union(*[lift(boxM_all[i]) for i in combo])
        f, R = S.ldiv(G, S.S_POLY)
        if R or not f or S.radius_of(f) > 6:
            continue
        try:
            n, rr = S.rule_number(f)
        except AssertionError:
            continue
        st = status(f)
        uniM.append(dict(orbits=[sorted(boxM_all[i])[0] for i in combo], sizes=[len(boxM_all[i]) for i in combo], rule=n, radius=rr, **st))
out['M0_unions_in_box'] = uniM
for u in uniM:
    print('   s*f = union', u['orbits'], u['sizes'], '-> rule', u['rule'], 'r', u['radius'], 'ninth', u['ninth'])
# ---------------- (d): recorded confined rules
recs = []
d = json.load(open('/home/user/lattice-lab/examples/llm-pilot-37c/data/ninth37.json'))
for fam in d['families']:
    for r in fam['ninth_power_rules']:
        recs.append((r['id'], fam['radius']))
for line in open('/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl'):
    r = json.loads(line)
    if 'id' in r:
        recs.append((r['id'], 6))
recs = sorted(set(recs))
def single_orbit(G, orbits_list):
    Gm = frozenset((p % m, q % m) for p, q in G)
    return any(Gm == O for O in orbits_list)
hitsT, hitsM = [], []
for n, r in recs:
    f = S.rule(n, r)
    if single_orbit(S.lmul(f, S.PI_POLY), orbs):
        hitsT.append(n)
    if single_orbit(S.lmul(f, S.S_POLY), orbsM):
        hitsM.append(n)
out['recorded_rules_checked'] = len(recs)
out['recorded_with_pi_f_single_T_orbit'] = hitsT
out['recorded_with_s_f_single_M0_orbit'] = hitsM
print('recorded ninth-power rules (radius 4, 5, 6):', len(recs), '; pi*f a single <D4,T>-orbit:', hitsT, '; s*f a single <D4,M0>-orbit:', hitsM)
out['time'] = round(time.time() - t0, 1)
print('time', out['time'])
json.dump(out, open('t1_shape.json', 'w'), indent=1, default=str)
