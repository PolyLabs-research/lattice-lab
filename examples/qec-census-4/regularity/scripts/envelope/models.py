"""Candidate envelope functions f(n) and three fitting methods (see fit_all.py docstring)."""
import numpy as np
from scipy.optimize import least_squares, minimize, linprog

L = np.log
S = np.sqrt

# name: (f(n, p), p0, short formula, linear-design or None)
MODELS = {
    'c*sqrt(n)':            (lambda n, p: p[0] * S(n),                      [1.4],        lambda n: [S(n)]),
    'c*sqrt(n ln n)':       (lambda n, p: p[0] * S(n * L(n)),               [0.6],        lambda n: [S(n * L(n))]),
    'c*sqrt(n)*ln n':       (lambda n, p: p[0] * S(n) * L(n),               [0.25],       lambda n: [S(n) * L(n)]),
    'a*n^b':                (lambda n, p: p[0] * n ** p[1],                 [0.7, 0.6],   None),
    'c*sqrt(n)*(ln n)^p':   (lambda n, p: p[0] * S(n) * L(n) ** p[1],       [0.6, 0.5],   None),
    'c*sqrt(n)*(1-e^-n/n0)':(lambda n, p: p[0] * S(n) * (1 - np.exp(-n / abs(p[1]))), [1.5, 80.], None),
    'A*sqrt(n)+B':          (lambda n, p: p[0] * S(n) + p[1],               [1.7, -4.],   lambda n: [S(n), np.ones_like(n)]),
    'sqrt(n)*(a+b*sqrt(ln n))': (lambda n, p: S(n) * (p[0] + p[1] * S(L(n))), [0.0, 0.6], lambda n: [S(n), S(n) * S(L(n))]),
    'a+b*n':                (lambda n, p: p[0] + p[1] * n,                  [4., 0.07],   lambda n: [np.ones_like(n), n]),
    'a*n^b+c':              (lambda n, p: p[0] * n ** p[1] + p[2],          [1.5, 0.52, -3.], None),
}
NPAR = {k: len(v[1]) for k, v in MODELS.items()}


def f(name, n, p):
    return MODELS[name][0](np.asarray(n, float), np.asarray(p, float))


def fit_ls(name, n, y, w=None):
    """Least squares of f(n) to y (optionally weighted). Multi-start for robustness."""
    fn, p0, _ = MODELS[name][0], MODELS[name][1], None
    n = np.asarray(n, float); y = np.asarray(y, float)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    best = None
    starts = [p0]
    if name == 'c*sqrt(n)*(1-e^-n/n0)':
        starts = [[1.5, x] for x in (10, 30, 60, 100, 200, 400)]
    if name == 'a*n^b+c':
        starts = [[a, b, c] for a in (0.5, 1.5, 3.) for b in (0.4, 0.5, 0.6, 0.7) for c in (-8, -3, 0, 3)]
    if name == 'c*sqrt(n)*(ln n)^p':
        starts = [[0.6, 0.5], [1.0, 0.1], [0.3, 1.0]]
    if name == 'a*n^b':
        starts = [[0.7, 0.6], [1.5, 0.5], [0.3, 0.7]]
    for s in starts:
        try:
            r = least_squares(lambda p: w * (fn(n, p) - y), s, max_nfev=20000)
        except Exception:
            continue
        if best is None or r.cost < best.cost:
            best = r
    return best.x, best


def fit_upper(name, n_all, y_all, n_obj, y_obj, p_init):
    """Tightest upper envelope: minimise sum_{obj}(f - y) subject to f >= y on all points.
    Exact LP for models linear in their parameters; SLSQP multi-start otherwise."""
    n_all = np.asarray(n_all, float); y_all = np.asarray(y_all, float)
    n_obj = np.asarray(n_obj, float); y_obj = np.asarray(y_obj, float)
    lin = MODELS[name][2]
    if lin is not None:
        Xa = np.array(lin(n_all)).T; Xo = np.array(lin(n_obj)).T
        c = Xo.sum(0)
        res = linprog(c, A_ub=-Xa, b_ub=-y_all, bounds=[(None, None)] * Xa.shape[1], method='highs')
        if res.status == 0:
            return res.x
    fn = MODELS[name][0]
    best = None
    for scale in (1.0, 1.05, 1.1, 1.2):
        p = np.array(p_init, float).copy()
        # push the start above all points
        if name in ('a*n^b+c', 'A*sqrt(n)+B'):
            p[-1] += 3 * scale
        else:
            p[0] *= scale * max(1.0, np.max(y_all / np.maximum(fn(n_all, p), 1e-9)))
        cons = {'type': 'ineq', 'fun': lambda q: fn(n_all, q) - y_all}
        for meth in ('SLSQP', 'trust-constr'):
            opts = {'maxiter': 5000, 'ftol': 1e-12} if meth == 'SLSQP' else {'maxiter': 5000}
            try:
                r = minimize(lambda q: np.sum(fn(n_obj, q) - y_obj), p, constraints=[cons], method=meth,
                             options=opts)
            except Exception:
                continue
            # feasibility tolerance 1e-3 in d units (d is even-quantised; irrelevant at this size)
            if np.all(fn(n_all, r.x) - y_all >= -1e-3) and (best is None or r.fun < best.fun):
                best = r
    return best.x if best is not None else None


def crossing(name, p, d, lo=5, hi=1e7):
    """Smallest n where f(n) >= d (bisection on a monotone-ish f; scan first)."""
    grid = np.geomspace(lo, hi, 20000)
    v = f(name, grid, p)
    idx = np.where(v >= d)[0]
    if len(idx) == 0:
        return np.inf
    i = idx[0]
    if i == 0:
        return grid[0]
    a, b = grid[i - 1], grid[i]
    for _ in range(60):
        m = 0.5 * (a + b)
        if f(name, m, p) >= d:
            b = m
        else:
            a = m
    return b
