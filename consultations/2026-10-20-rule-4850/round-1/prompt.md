You are being consulted on a mathematics research project. The project studies linear cellular automata over GF(2) on tori: which rules have every nonzero eigenvalue in a given subgroup (a cube, say) at a given size, why, and what laws their periods follow. Its rule is that nothing counts until a machine has checked it: identities are multiplied out again, claims about eigenvalues are recomputed, proofs go into Lean, and predictions are registered before they are tested. Other models are being asked the same question independently.

So that your answer can be checked: state each claim precisely, with the quantifiers and the sizes it covers; say for each whether you proved it, checked it by computation (and how far), or conjecture it; give proofs or arguments where you have them; and where you can, make predictions at cases the documents below do not settle, which can then be registered and tested. If you can run code, use it to check every identity and computation before you state it. Say plainly where you think the project is wrong or missing something.

<question>
Work over GF(2). For (a, b) in Z², let O(a, b) be the set of all points (±a, ±b) and
(±b, ±a). A rule is a union of such orbits, read as the Laurent polynomial
f(x, y) = Σ x^a y^b over its points. The **square family** is every nonempty union of the 15
orbits O(a, b) with 0 ≤ b ≤ a ≤ 4: 32,767 symmetric linear cellular automata on the square
lattice. Rule n is the union of the orbits its bits select, in the order (0,0), (1,0), (1,1),
(2,0), (2,1), (2,2), (3,0), ..., (4,4).

**Eigenvalues and periods.** On the torus (Z/m)², m odd, a rule acts diagonally in the
characters: its eigenvalues are f(ζ^j, ζ^k), ζ a primitive m-th root of unity in F(2^d),
d = ord_m(2). The odd part of the rule's period is the lcm of the multiplicative orders of its
nonzero eigenvalues. The rules are symmetric, so the eigenvalues lie in F(2^s), s the least j
with 2^j = ±1 (mod m), and the odd part divides the full bound 2^s - 1.

**Coordinates.** Write a = x + 1/x and b = y + 1/y. Every rule of the family is a symmetric
polynomial F(a, b) of degree at most 4 in each variable: O(i, j) = D_i(a) D_j(b) + D_j(a) D_i(b),
O(i, i) = D_i(a) D_i(b), O(i, 0) = D_i(a) + D_i(b) and O(0, 0) = 1, with D_1(a) = a,
D_2(a) = a^2, D_3(a) = a^3 + a and D_4(a) = a^4. At a character, a and b take the values of
rule 90, t_j = ζ^j + ζ^-j and t_k.

**Mechanisms known to confine eigenvalues to a proper subgroup**, each proved:

1. splitting: f is a product of one-dimensional rules along lattice directions. Rule 90,
   t(x) = x + 1/x, and rule 150, 1 + t(x), are the basic ones.
2. powers: f = g^k, so the eigenvalues are k-th powers.
3. dilations: f = h(x^p, y^p) with p dividing m.
4. twisted powers: f = g(x, y) g(x^d, y^d) with d = ±2^k (mod m), so the eigenvalues are
   λ^(1 + 2^k).
5. half-Frobenius confinement, at m = 37: if n = 2^g (mod m) and B is invariant under the
   dilation (x, y) -> (x^n, y^n) on the m-torus, B's eigenvalues lie in F(2^g). At 37,
   2^9 = -6 and 6^2 = -1. Some rules become such a B after multiplying by rule-90 factors.
6. cube certificates and twisted pairs, at m = 25: f M^E = B with B invariant under x2^g and q
   dividing E; and f = C(x^a, y^a) C(x^b, y^b) with b = ±2^k a.
7. a unit times a power: f = U g^q exactly, every nonzero eigenvalue of U a q-th power at m.
   At 37, nine family rules are U g^3 with U one of a + b, ab, (a + 1)(b + 1). Rule 90's values
   are cubes at 37 because the fundamental unit of Q(sqrt 37), 6 + sqrt 37, lies in Z[sqrt 37];
   rule 150's values are cubes wherever 3 is a power of 4 mod m.

**The question.** Rule 4850 is O(1,0) ∪ O(2,1) ∪ O(2,2) ∪ O(3,0) ∪ O(3,1) ∪ O(3,3) ∪ O(4,2), or

    F(a, b) = a^4 b^2 + a^3 b^3 + a^3 + a^2 b^4 + a^2 b^2 + a^2 b + a b^2 + a b + b^3,

which with s = a + b and p = ab is F = s^3 + p + p^2 + p^3 + p^2 s^2.

At m = 37 (d = 36, s = 18, full bound 2^18 - 1 = 3^3 · 7 · 19 · 73), **every nonzero eigenvalue
of rule 4850 is a ninth power** in F(2^18)*: the odd part of its period is
(2^18 - 1)/9 = 29,127. They are not all 27th powers. (Checked by computer, two independent ways.)

What has been checked:

- At no other odd m from 9 to 201 is 4850 confined at all: its odd part is the full bound.
- In the family at 37, 110 rules are confined to the cubes, 21 to the ninth powers and 4 to the
  27th powers. Of the 21, all but 4850 are accounted for by mechanisms 1 to 4: they split along
  lattice directions into rule-90 and rule-150 factors (rule 150's values at 37 are ninth
  powers), or are powers or dilations of such rules. For instance rule 7 is (1 + a)(1 + b) and
  rule 13 = O(0,0) ∪ O(1,1) ∪ O(2,0) is (1 + t(xy))(1 + t(x/y)), rule 150 along both diagonals.
- None of mechanisms 5 to 7 explains 4850. As a polynomial in a and b it is irreducible over
  GF(2) (it has total degree 6 and no factor of total degree at most 3), and it is irreducible
  as a Laurent polynomial in x and y too (Kronecker substitution and recombination). An earlier
  consultant reported, not rechecked, that its smallest cube root in the group ring
  F2[x, y]/(x^37 - 1, y^37 - 1) has about 440 terms, as for a random confined rule.
- The stabiliser of its support mod 37 in GL2(Z/37) is the lattice's 8 symmetries, and no
  invertible exponent map with entries in [-6, 6] sends it to another family rule.
- It has 10 free classes of characters (classes not forced into a subfield). The sixth pilot's
  census counted it among seven confined rules it attributed to chance, before anyone noticed
  the ninth powers.
- Ninth-power confinement is equivalent to the group-ring identity f^29127 = idempotent, or to
  the norm from F(2^18) to F(2^6) of each eigenvalue lying in F(2^3). Both are restatements, not
  explanations.

**Find the mechanism**: why every nonzero eigenvalue of rule 4850 at m = 37 is a ninth power,
stated as a condition on a rule f and an odd m that you can prove and that holds for 4850 at 37.
Say whether it explains anything else: other rules of the family at 37 (cube- or
ninth-power-confined), other sizes, or rules outside the family. Make predictions that can be
registered and tested. If you conclude there is no mechanism, say exactly what you excluded.

## Machine-checkable claims

End your answer with one JSON block (```json ... ```) of the form

    {"definitions": {"name": "expression", ...},
     "factorisations": [{"rule": 4850, "factors": [["expression", exponent], ...]}, ...],
     "congruences": [{"lhs": "expression", "rhs": "expression"}, ...]}

A factorisation means that the rule equals the product of its factors, each raised to its
exponent, over GF(2) modulo (x^37 - 1, y^37 - 1); a congruence means lhs = rhs there. List every
identity your argument uses. An expression is a Laurent polynomial in x and y, written with +, *
and ^ (negative exponents only on monomials). You may use O(a, b) as above, t(z) for z + 1/z,
R(n) for family rule n, and the names you define in "definitions", each an expression in x, y
and earlier names. Every claim will be checked by machine, and one that fails counts against the
answer, so list only what you have checked.
</question>
