# The census remainder: 45 cube confinements, sorted

**Status: exploratory, not registered.** The m = 37 pilot's census of all 1,274 shell rules found
69 rules, at odd m from 9 to 161, whose nonzero eigenvalues are all cubes although no known
mechanism accounts for it. The pilot's agent explained 24 of them
([llm-pilot.md](llm-pilot.md#pilot-4-the-cubes-at-m--37)). This note sorts the other 45.

- **Chance: 34 of them**, at m = 13 and 29. Each has only one to four free eigenvalue classes, and
  the number confined matches what chance gives: 33 at m = 13 against 29 ± 5 expected, and 1 at
  m = 29 against 0.7.
- **A known mechanism, mispredicted: 1**, at m = 115. The rule is a product of four rule-90
  passes, and the atlas procedure predicts the period of one factor, which is too large when the
  factors are correlated.
- **Hidden symmetries: 2**, triangle E+VO+T7+T9+self at m = 21 and 69. Modulo 21 and 69 this
  rule has 72 symmetries, not the lattice's 12, and with them its confinement is a 1-in-3 and a
  1-in-81 event.
- **Coinciding eigenvalues: 5**, at m = 21. The four square rules each have seven free classes but
  only two to four distinct values; across all symmetric square rules, m = 21 shows a mild excess
  (12 against 7 ± 2.6).
- **Unexplained structure: 3**, at m = 25. Among all 32,768 symmetric square rules within
  distance 4, **14 are confined at m = 25 against 1.7 ± 1.3 expected**, each with 8 to 10 free
  classes. No symmetry of any kind explains them, and rule 90 is not confined at 25. This is the
  open part.

The tools are `examples/census-remainder`; `findings.py` reproduces every number here in a few
seconds from the census and the files beside it.

## After pilot 5: two of these verdicts were wrong

The fifth pilot's agent took m = 25 ([llm-pilot.md](llm-pilot.md#pilot-5-the-cubes-at-m--25)),
and the judge checked its condition on every entry here:

- **16 of the 33 "chance" entries at m = 13 are structure.** They are cube certificates: f · M^E
  is invariant under the dilation by 4 or 8 mod 13 (2^2 and 2^3; 8² ≡ −1), with M a product of
  rule-90 factors (or of t + 1 along them) and E = 3, 6 or 9, so every eigenvalue is a cube. The
  chance model counted them as free classes that happened to be cubes; it has no term for a
  multiplier that enters as a cube.
- **3 of the 5 "coinciding eigenvalue" entries at m = 21 are cube certificates too**: rule 90
  along both axes, E = 6, and the dilation by 8 = 2^3 (8² ≡ 1 mod 21).
- **At m = 25, 5 of the 17 are explained and proved in Lean** (`Cubes25.lean`): two cube
  certificates, f · (t(x) t(y))³ invariant under ×7, and three twisted pairs
  C(x, y) C(x³, y³), a case of mechanism 4 (3 ≡ 2^7 mod 25) that this note's check for twisted
  powers did not try. None of the three atlas rules is among them.
- **Chance was refuted at held-out sizes.** The orchestrator registered, before the pilot, that
  the square family's census at 14 sizes from 27 to 75 would show nothing beyond chance. It
  showed excess at 6. The twisted pairs explain 35, 53 and 55, and part of 29. **At 37, 16
  square rules are confined that no known mechanism explains** (0.6 expected), three of them also
  at 61.

So of the 45 here, 19 now have a proved mechanism, and the counts below are as first written.

**And after pilot 6** ([llm-pilot.md](llm-pilot.md#pilot-6-the-square-family-at-m--37)): the 16
at 37 were not one thing. Nine are a unit times a cube, f = U · g³ exactly, with U a product of
rule-90 or Ψ₃ factors; the other seven are what chance gives once the model is corrected. Its
rate of one in three per free class is wrong where rule 90 is confined: at 37 the axis and
diagonal classes are cubes 93.5% of the time (29 of the 31 possible one-dimensional values are
products of units), and the expected count of chance confinements in the family there is 5.7,
not 0.62. The verdicts here that rest on the model inherit that error wherever rule 90 is
confined; at 13 it is not.

## The method

**Forced subfields.** A rule's eigenvalue at a character c is λ(c) = f(ζ^c). Frobenius gives
λ(2c) = λ(c)², and a matrix M that maps the rule's translations onto themselves mod m gives
λ(Mᵀc) = λ(c). So if 2^i c = Mᵀc for a symmetry M, then λ(c) lies in F(2^i), whatever the rule.
At m = 13 the eigenvalues lie in F(2^6), and every element of its subfields F(4) and F(8) is a
cube, so an eigenvalue forced into either is a cube by structure. The symmetries searched are
those of the lattice (matrices with entries −1, 0, 1, which give every rule's full lattice
symmetry group of 8 or 12), times powers of 2; and, for the entries here, all of GL2(Z/m).

**The chance model.** The other classes are free. The model takes each free class's value to be
uniform over its forced field, independently of the others, so a class is a cube one time in
three, and a rule is confined by chance with probability 3^(−free classes). Summed over all the
rules no known mechanism confines, it gives the expected number of chance confinements at each m.

**Its checks.** Applied to the census, it marks as forced exactly the 18 rules at m = 13 that
the pilot's pure case explains (invariance under ×8 or ×4), an independent check of both. Its
weak points were then measured:

- **The rate per class** is not quite one in three in small fields: free classes are cubes 37 to
  40% of the time at m = 13, partly because the value 1 is three times as common as uniform. At
  m = 25 the rate is 0.34. So the model, if anything, underpredicts at m = 13.
- **Random rules.** On 1,500 random symmetric square rules (unions of the D4 orbits of the
  translations within distance 4), the model expected 22.6 ± 4.7 confinements at m = 13, and 32
  were found; at m = 21, 25 and 29 it expected 0.32, 0.07 and 0.26, and none were found.
- **The whole family.** All 32,768 such rules, at m = 21 and 25 (`family-21.json`,
  `family-25.json`).

## The 45, by size

| m | entries | expected by chance (the atlas) | verdict |
| --- | --- | --- | --- |
| 13 | 33 | 29.1 ± 5.3 | chance: 1 to 4 free classes each; three of them also have hidden symmetries mod 13 (24, not 8 or 12) |
| 21 | 6 | 1.9 ± 1.4 | one hidden symmetry (the triangle rule); five with coinciding eigenvalues |
| 25 | 3 | 0.24 ± 0.49 | **unexplained structure** |
| 29 | 1 | 0.71 ± 0.84 | chance |
| 69 | 1 | 0.003 | hidden symmetry (the triangle rule again) |
| 115 | 1 | 0 | a mispredicted split |

`findings.py` prints the table rule by rule: the symmetries (the lattice's, and mod m), the free
classes, their distinct values, and the chance.

### m = 115: a split with correlated factors

Square N4+D4+B4+C4 is, up to a monomial, the product of four factors 1 + u along the directions
(1, ±2) and (2, ±1): four rule-90 passes. The atlas procedure calls it "splits into 1+u" and
predicts the period of one 1D factor, which assumes the factors' values vary independently. Along
these four directions they do not, and the product falls short where no factor does: its odd
part is a third of the procedure's prediction at m = 115, and at m = 5 it is 1 where the
procedure predicts 3. The procedure's split step should compute the product's period from its
eigenvalues, as `eigen.py` does.

### The triangle rule at 21 and 69: hidden symmetries

Triangle E+VO+T7+T9+self has the triangular lattice's 12 symmetries. Modulo 21 and modulo 69,
it has 72, for example (x, y) ↦ (y, 8x + 7y) mod 21. Its support has only 12 symmetries mod 3
and 12 mod 7 (or mod 23); the extra ones pair a symmetry of one part of the torus with a
different symmetry of the other, which works for 72 of the 144 pairs. They tie its eigenvalues
together: with them, it has one free
class at m = 21 and four at m = 69, so its confinement there has probability 1/3 and 1/81.
Without them it looked like a one-in-ten-million event.

### m = 21: coinciding eigenvalues

The four square rules each have seven free classes, but only two to four distinct values among
them up to Frobenius, and no symmetry mod 21 explains the coincidences. Counting distinct values,
their confinement is a 1-in-9 to 1-in-81 event. Across the whole square family, m = 21 has 12
confinements against 7.0 ± 2.6 expected: a mild excess, about 2σ.

### m = 25: the open part

Three atlas rules (triangle E+T7+self, hexagon H1+H3+H13 and H3+H4+H5) and 14 of the 32,768
symmetric square rules are confined at m = 25, against 0.24 and 1.7 ± 1.3 expected. The square
ones have 8 to 10 free classes and 6 to 8 distinct values; their full symmetry groups mod 25 are
the lattice's 8, and for the three examined no matrix preserves even their eigenvalues on the
characters of order 25.
Rule 90 is not confined at 25, so the m = 37 mechanism does not apply as it stands.

A lead: 25 has the arithmetic of 37. 2^5 ≡ 7 (mod 25) and 7² ≡ −1, so the dilation by 7 acts on
eigenvalues as the half-Frobenius x ↦ x^(2^5), and 2^5 − 1 = 31 is prime to 3, so F(2^5) lies in
the cubes of F(2^10). A pair of rule-90 factors along w and 7w has eigenvalue t · t^(2^5) = t^33,
always a cube. So rule-90 units in such pairs could stand in for the confinement of rule 90 that
the m = 37 mechanism needs. m = 29 has the same arithmetic (2^7 ≡ 12, 12² ≡ −1); its one entry is
consistent with chance, but the lead applies there too.

## What this does and does not show

It sorts the remainder; it proves nothing new. The chance verdicts rest on a model that is
approximate, and the counts at m = 13 agree with it because the excess there is small against
its error. None of it was registered, and the verdicts were drawn after looking. The next steps
that would make it a result:

- **m = 25** is a question for the loop: a mechanism, as a condition the judge can run on every
  rule, with 17 known examples to explain. It suits a fifth pilot.
- **The procedure** needs its split step computed exactly, and steps for the half-Frobenius and
  for hidden symmetries mod m, then a registered round on new rules (round 4).
- **The chance model** could be registered as it stands: its predicted count of confinements at
  small m, for a fresh sample of rules, before computing them.
