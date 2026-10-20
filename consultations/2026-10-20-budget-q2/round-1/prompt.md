You are being consulted on a mathematics research project. The project studies linear cellular automata over GF(2) on tori: which rules have every nonzero eigenvalue in a given subgroup (a cube, say) at a given size, why, and what laws their periods follow. Its rule is that nothing counts until a machine has checked it: identities are multiplied out again, claims about eigenvalues are recomputed, proofs go into Lean, and predictions are registered before they are tested. Other models are being asked the same question independently.

So that your answer can be checked: state each claim precisely, with the quantifiers and the sizes it covers; say for each whether you proved it, checked it by computation (and how far), or conjecture it; give proofs or arguments where you have them; and where you can, make predictions at cases the documents below do not settle, which can then be registered and tested. If you can run code, use it to check every identity and computation before you state it. Say plainly where you think the project is wrong or missing something.

<question>
Work over GF(2). For (a, b) in Z², let O(a, b) be the set of all points (±a, ±b) and
(±b, ±a). A rule is a union of such orbits, read as the Laurent polynomial
f(x, y) = Σ x^a y^b over its points. The **square family** is every nonempty union of the 15
orbits O(a, b) with 0 ≤ b ≤ a ≤ 4: 32,767 symmetric linear cellular automata on the square
lattice.

**Eigenvalues and periods.** On the torus (Z/m)², m odd, a rule acts diagonally in the
characters: its eigenvalues are f(ζ^j, ζ^k), ζ a primitive m-th root of unity in F(2^d),
d = ord_m(2). The odd part of the rule's period is the lcm of the multiplicative orders of its
nonzero eigenvalues. The rules are symmetric, so the eigenvalues lie in F(2^s), s the least j
with 2^j = ±1 (mod m), and the odd part divides 2^s - 1.

**Mechanisms already known to confine eigenvalues to a proper subgroup**, each proved:

1. splitting: f is a product of one-dimensional rules along lattice directions. Rule 90,
   t(x) = x + 1/x, is the basic one, with eigenvalues ζ^j + ζ^-j.
2. powers: f = g^k, so the eigenvalues are k-th powers.
3. dilations: f = h(x^p, y^p) with p dividing m.
4. twisted powers: f = g(x, y) g(x^d, y^d) with d = ±2^k (mod m), so the eigenvalues are
   λ^(1 + 2^k).
5. half-Frobenius confinement, at m = 37: if n = 2^g (mod m) and B is invariant under the
   dilation (x, y) -> (x^n, y^n) on the m-torus, B's eigenvalues lie in F(2^g). At 37,
   2^9 = -6 and 6^2 = -1. Some rules become such a B after multiplying by rule-90 factors,
   whose eigenvalues are cubes at 37 because rule 90 itself is confined to the cubes there.
6. cube certificates and twisted pairs, at m = 25: f M^E = B with B invariant under x2^g and q
   dividing E (the multiplier M enters as a q-th power); and f = C(x^a, y^a) C(x^b, y^b) with
   b = ±2^k a.

A chance model takes each class of characters not forced into a subfield as uniform over its
field and independent, so a rule with k free classes is confined to the cubes by chance about
one time in 3^k.

**The question.** At m = 37, d = 36 and s = 18 (2^18 = -1). The full bound is
2^18 - 1 = 262,143 = 3^3 · 7 · 19 · 73, and the cubes are its subgroup of order 87,381. Every
proper subfield of F(2^18) lies inside the cubes, and so do rule 90's eigenvalues.

- In the square family, 34 rules are confined to the cubes at 37 beyond mechanisms 1 to 4 and
  forced subfields. Mechanism 5 explains 18 of them; mechanism 6 adds none. The other 16 are
  unexplained, against 0.62 ± 0.79 expected by chance. Each has 9 or 10 free classes: chance
  confines each about once in 20,000 to 60,000.
- Three of the 16 (rules 3461, 18246 and 26883) are also confined to the cubes at m = 61, where
  nothing else in the family is. At 61, d = 60, s = 30, and the full bound is
  2^30 - 1 = 3^2 · 7 · 11 · 31 · 151 · 331. Rule 90 is not confined at 61 (its odd part is the
  full bound), and F(2^6) is not inside the cubes there, though F(2^2), F(2^3), F(2^5),
  F(2^10) and F(2^15) are.

The sixteen (orbits as (a, b) pairs):

| rule | orbits | confined at |
| --- | --- | --- |
| 1112 | (2,0) (2,1) (3,0) (4,0) | 37 |
| 2436 | (1,1) (3,1) (3,2) (4,1) | 37 |
| 3461 | (0,0) (1,1) (3,1) (3,2) (4,0) (4,1) | 37, 61 |
| 4850 | (1,0) (2,1) (2,2) (3,0) (3,1) (3,3) (4,2) | 37 |
| 5972 | (1,1) (2,1) (3,0) (3,2) (3,3) (4,0) (4,2) | 37 |
| 10498 | (1,0) (3,2) (4,1) (4,3) | 37 |
| 13584 | (2,1) (3,2) (4,0) (4,2) (4,3) | 37 |
| 13822 | (1,0) (1,1) (2,0) (2,1) (2,2) (3,0) (3,1) (3,2) (4,0) (4,2) (4,3) | 37 |
| 17056 | (2,2) (3,1) (3,3) (4,4) | 37 |
| 18246 | (1,0) (1,1) (3,0) (3,2) (3,3) (4,0) (4,4) | 37, 61 |
| 22064 | (2,1) (2,2) (3,3) (4,0) (4,2) (4,4) | 37 |
| 25183 | (0,0) (1,0) (1,1) (2,0) (2,1) (3,0) (3,3) (4,3) (4,4) | 37 |
| 26883 | (0,0) (1,0) (3,2) (4,1) (4,3) (4,4) | 37, 61 |
| 27390 | (1,0) (1,1) (2,0) (2,1) (2,2) (3,0) (3,1) (3,3) (4,1) (4,3) (4,4) | 37 |
| 28586 | (1,0) (2,0) (2,2) (3,1) (3,2) (3,3) (4,0) (4,1) (4,3) (4,4) | 37 |
| 28944 | (2,1) (3,2) (4,2) (4,3) (4,4) | 37 |

**What has been checked.** No hidden symmetry: for all 16, the stabiliser of the support mod 37
in GL2(Z/37) is the lattice's 8, and the same holds mod 61 for the three. Mechanisms 5 and 6,
searched with much wider bounds, explain none of the 16, nor any of their images under 2,112
invertible exponent maps. What is not known: whether the 16 share factors. Two-variable
factorisation over GF(2) is not in sympy, and nobody has looked.

**Find the mechanism**: a condition on a rule f and an odd m that forces every nonzero
eigenvalue of f at m to be a cube (or a q-th power), that holds for the targets, and that you
can prove. Say which of the 16 it explains, why the three are also confined at 61, and where
else it predicts confinement. If part of it is chance after all, say which part and why.

## Machine-checkable claims

End your answer with one JSON block (```json ... ```) of the form

    {"definitions": {"name": "expression", ...},
     "factorisations": [{"rule": 1112, "factors": [["expression", exponent], ...]}, ...],
     "congruences": [{"lhs": "expression", "rhs": "expression"}, ...]}

A factorisation means that the rule equals the product of its factors, each raised to its
exponent, over GF(2) modulo (x^37 - 1, y^37 - 1); a congruence means lhs = rhs there. List a
factorisation for every rule you explain by one, and any other identity your argument uses as a
congruence. An expression is a Laurent polynomial in x and y, written with +, * and ^ (negative
exponents only on monomials). You may use O(a, b) as above, t(z) for z + 1/z, R(n) for the
family rule with id n from the table, and the names you define in "definitions", each an
expression in x, y and earlier names. Every claim will be checked by machine, and one that fails
counts against the answer, so list only what you have checked.
</question>
