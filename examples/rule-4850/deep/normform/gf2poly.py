"""Bivariate polynomials over GF(2): factoring by Kronecker substitution, with every candidate factor
verified by exact bivariate division (sympy.div over GF(2))."""
import itertools
import sympy as sp

def _kron_factors(poly, u, v, D):
    z = sp.Symbol('z')
    expr = 0
    for (i, j), c in poly.terms():
        if int(c) % 2:
            expr += z ** (i + D * j)
    up = sp.Poly(expr, z, modulus=2)
    _, facs = up.factor_list()
    flat = []
    for f, mult in facs:
        flat += [f] * mult
    return flat, z

def _lift(fz, z, u, v, D):
    expr = 0
    for (e,), c in fz.terms():
        if int(c) % 2:
            expr += u ** (e % D) * v ** (e // D)
    return sp.Poly(expr, u, v, modulus=2)

def factor2(poly, u, v):
    """irreducible factors (sympy Polys over GF(2)) of a bivariate Poly, product verified."""
    out = []
    todo = [poly]
    while todo:
        p = todo.pop()
        if p.total_degree() <= 1:
            out.append(p); continue
        D = p.degree(u) + 1
        flat, z = _kron_factors(p, u, v, D)
        split = None
        for size in range(1, len(flat)):
            for sub in itertools.combinations(range(len(flat)), size):
                prod = sp.Poly(1, z, modulus=2)
                for i in sub:
                    prod = prod * flat[i]
                cand = _lift(prod, z, u, v, D)
                if cand.total_degree() == 0:
                    continue
                q, r = sp.div(p, cand)
                if r.is_zero and q.total_degree() > 0:
                    split = (cand, q); break
            if split:
                break
        if split:
            todo += list(split)
        else:
            out.append(p)
    prod = sp.Poly(1, u, v, modulus=2)
    for f in out:
        prod = prod * f
    assert prod == poly, 'factorization check failed'
    return [f.as_expr() for f in out]
