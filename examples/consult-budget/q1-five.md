Work over GF(2). For (a, b) in Z², let O(a, b) be the set of all points (±a, ±b) and
(±b, ±a), and for a set S of such points let f_S(x, y) = Σ_{(a,b) ∈ S} x^a y^b,
a Laurent polynomial over GF(2). Consider these five:

  f1: O(0,0) ∪ O(2,0) ∪ O(2,1) ∪ O(2,2)
  f2: O(2,1) ∪ O(3,2) ∪ O(3,3)
  f3: O(3,0) ∪ O(3,1) ∪ O(3,2)
  f4: O(3,0) ∪ O(3,1) ∪ O(3,2) ∪ O(3,3)
  f5: O(0,0) ∪ O(2,0) ∪ O(2,2) ∪ O(3,0) ∪ O(3,1) ∪ O(3,3)

Let ζ be a primitive 37th root of unity in F_{2^36} (2 has order 36 mod 37). Each f
is symmetric under (x, y) -> (1/x, 1/y), so its values f(ζ^j, ζ^k) lie in F_{2^18}.

Observation (checked by computer): for each of the five, every nonzero value
f(ζ^j, ζ^k), j, k in Z/37, is a cube in F_{2^18}*, i.e. lies in the subgroup of order
(2^18 - 1)/3 = 87381. A random polynomial of this kind would do that roughly once in
20,000 tries or less often, and at every other odd modulus from 9 to 161 none of the
five does anything like it. The same holds at 37 for t(x) = x + 1/x.

(Context: these are linear cellular automata on the 37 x 37 torus. The period is the
lcm of the multiplicative orders of the nonzero values, so this says the period divides
87381 instead of 2^18 - 1.)

Why? Find the reason, state it as a general condition on a polynomial f and an odd
modulus m that forces every nonzero value to be a cube (or a q-th power), and prove
that it holds for these five at m = 37.

## Machine-checkable claims

End your answer with one JSON block (```json ... ```) of the form

    {"definitions": {"name": "expression", ...},
     "congruences": [{"lhs": "expression", "rhs": "expression"}, ...]}

listing the identities your argument uses, each meaning lhs = rhs over GF(2) modulo
(x^37 - 1, y^37 - 1). An expression is a Laurent polynomial in x and y, written with +, *
and ^ (negative exponents only on monomials). You may use O(a, b) as above, t(z) for
z + 1/z, f1(X, Y) to f5(X, Y) for the five polynomials evaluated at any expressions X and Y
(so f1(x^6, y^6) is f1 dilated by 6), and the names you define in "definitions", each an
expression in x, y and earlier names. Every congruence will be checked by machine, and one
that fails counts against the answer, so list only what you have checked.
