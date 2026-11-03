import sys; sys.path.insert(0, '.')
from base import *
from scipy.optimize import least_squares, linprog, brentq

S, L = np.sqrt, np.log
M = {
 'c*sqrt(n)':            (lambda n,p: p[0]*S(n),                 [1.4]),
 'c*sqrt(n)*ln n':       (lambda n,p: p[0]*S(n)*L(n),            [0.27]),
 'a+b*n':                (lambda n,p: p[0]+p[1]*n,               [5., .07]),
 'c*sqrt(n)(1-e^-n/n0)': (lambda n,p: p[0]*S(n)*(1-np.exp(-n/abs(p[1]))), [1.45, 30.]),
 # controls (not part of the claim)
 'A*sqrt(n)+B':          (lambda n,p: p[0]*S(n)+p[1],            [1.65, -3.]),
 'c*sqrt(n ln n)':       (lambda n,p: p[0]*S(n*L(n)),            [0.6]),
 'a*n^b':                (lambda n,p: p[0]*n**p[1],              [0.8, .6]),
}
LIN = {'c*sqrt(n)': lambda n: [S(n)], 'c*sqrt(n)*ln n': lambda n: [S(n)*L(n)], 'a+b*n': lambda n: [np.ones_like(n), n],
       'A*sqrt(n)+B': lambda n: [S(n), np.ones_like(n)], 'c*sqrt(n ln n)': lambda n: [S(n*L(n))]}

def fev(name, n, p): return M[name][0](np.asarray(n, float), np.asarray(p, float))

def fit_thr(name, nmin, cut):
    T = [(d, a, b) for d, a, b in thr if nmin <= b <= cut]
    x = np.array([(a+b)/2 for d, a, b in T], float); y = np.array([d for d, a, b in T], float)
    best = None
    starts = [M[name][1]]
    if 'n0' in name: starts = [[1.45, s] for s in (5, 15, 30, 60, 120, 300)]
    if name == 'a*n^b': starts = [[0.8, .6], [1.5, .5], [0.3, .7]]
    for s in starts:
        r = least_squares(lambda p: fev(name, x, p) - y, s, max_nfev=20000)
        if best is None or r.cost < best.cost: best = r
    return best.x, len(T)

def fit_up(name, nmin, cut):
    n = np.array([k for k in ns if nmin <= k <= cut and k in E], float)
    y = np.array([E[int(k)] for k in n], float)
    if name in LIN:
        X = np.array(LIN[name](n)).T
        res = linprog(X.sum(0), A_ub=-X, b_ub=-y, bounds=[(None, None)]*X.shape[1], method='highs')
        return res.x, len(n)
    best = None
    if 'n0' in name:
        for n0 in np.geomspace(0.5, 3000, 3000):
            g = S(n)*(1-np.exp(-n/n0)); c = np.max(y/g)
            obj = np.sum(c*g - y)
            if best is None or obj < best[0]: best = (obj, [c, n0])
        return np.array(best[1]), len(n)
    if name == 'a*n^b':
        for b in np.linspace(0.3, 0.9, 6001):
            c = np.max(y/n**b); obj = np.sum(c*n**b - y)
            if best is None or obj < best[0]: best = (obj, [c, b])
        return np.array(best[1]), len(n)

def fe(v): return 2*np.floor(v/2 + 1e-12)

test_thr = [(d, a, b) for d, a, b in thr if b > 300]
stair = [n for n in ns if n > 300 and E[n] == R[n]]

def evaluate(name, p):
    res = [float(fev(name, (a+b)/2, p) - d) for d, a, b in test_thr]
    hits = sum(int(fe(fev(name, n, p)) == E[n]) for n in stair)
    errs = [int(fe(fev(name, n, p)) - E[n]) for n in stair]
    # predicted first-crossing n for each test d
    cross = []
    for d, a, b in test_thr:
        g = lambda t: fev(name, t, p) - d
        try: cross.append(round(brentq(g, 20, 5000), 1))
        except Exception: cross.append(None)
    return res, hits, errs, cross

if __name__ == '__main__':
    cut = 300
    print('test thresholds', test_thr, ' staircase test pts', len(stair), stair)
    for method in ('THR', 'UP'):
        for nmin in (30, 60, 100, 150, 200):
            print(f'\n=== {method}  train n in [{nmin},{cut}] ===')
            for name in M:
                p, cnt = (fit_thr if method == 'THR' else fit_up)(name, nmin, cut)
                if p is None: print(name, 'fail'); continue
                res, hits, errs, cross = evaluate(name, p)
                print(f'{name:22s} npts={cnt:2d} p={np.round(p,4)}  resid@d26,28={np.round(res,2)}  exact={hits}/{len(stair)}  '
                      f'err-mix={sorted(set(errs))} cross26,28={cross} (obs (300,306],(350,354])')
