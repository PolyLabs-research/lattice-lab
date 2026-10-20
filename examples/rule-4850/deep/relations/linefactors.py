"""
Logs (mod 513 and mod 27) at t_1 = zeta + 1/zeta of the irreducible factors over GF(2) of
Psi_e(t) for small e (the one-variable line factors that occur on the axes and lines of 4850 and
its relatives): which are ninth powers in F(2^18)*?
    python linefactors.py
"""
import sys
import sympy
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import tables  # noqa: E402

F = tables.C.F
f18 = tables.f18
t = sympy.symbols("t")
z = sympy.symbols("z")


def psi(e):
    phi = sympy.cyclotomic_poly(e, z)
    deg = sympy.degree(phi, z) // 2
    cs = sympy.symbols(f"c0:{deg + 1}")
    cand = sum(cs[i] * (z + 1 / z) ** i for i in range(deg + 1))
    eqs = sympy.Poly(sympy.expand((cand - phi / z**deg) * z**deg), z).all_coeffs()
    sol = sympy.solve(eqs, cs, dict=True)[0]
    return sympy.Poly(sum(int(sol[cs[i]]) % 2 * t**i for i in range(deg + 1)), t, modulus=2)


def ev(P, x):
    v = 0
    for (k,), c in P.terms():
        if int(c) % 2:
            v ^= F.pow(x, k)
    return v


t1 = f18.t(1)
for e in (3, 5, 7, 9, 13, 31, 127, 73, 11, 23):
    P = psi(e)
    _, facs = sympy.factor_list(P.as_expr(), modulus=2)
    rows = []
    for q, mult in facs:
        Q = sympy.Poly(q, t, modulus=2)
        lg = f18.log(ev(Q, t1))
        rows.append((str(q), lg % 513 if lg is not None else None, lg % 27 if lg is not None else None))
    print(f"Psi_{e} (deg {P.degree()}):", rows)
