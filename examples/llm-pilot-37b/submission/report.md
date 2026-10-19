# Report: the sixteen cube-confined rules at m = 37

## What I found

**Nine of the sixteen targets, including all three that are also confined at 61, are a unit times
a cube, exactly over GF(2).** With a = x + 1/x and b = y + 1/y:

| | (a + b + 1)³ | (ab + 1)³ | (ab + a + b)³ |
| --- | --- | --- | --- |
| a + b | 1112 | 10498 | 13584 |
| ab | 2436 | 17056 | 28944 |
| (a + 1)(b + 1) | 3461 | 26883 | 18246 |

These are all nine products of a bidegree-(1,1) unit with the cube of a bidegree-(1,1) non-unit;
the family's degree bound allows no others. The units' values are q-th powers on the whole torus:

* a + b = t_{(j+k)/2} t_{(j−k)/2} and ab = t_j t_k are products of rule-90 values, which are cubes
  at 37;
* (a + 1)(b + 1) = Ψ₃(t_j) Ψ₃(t_k) with Ψ₃(t)² = t_{3j}/t_j. That is a cube at 37 (rule 90) and,
  without rule 90, at 61, where 3 = 2⁶ makes it t^63. **This is why exactly the bottom row is
  confined at 61**, where rule 90 is not.

The cube factor needs no reason. So λ_f = λ_U λ_g³ is a cube.

**The mechanism** (proposal.md §3, proved in full): if f = x^v ∏ Φ_e(X_w)^{k_{w,e}} · h^q exactly
over GF(2), where X_w is a lattice monomial, h is any Laurent polynomial, and each unit Φ_e(X_w)
with q ∤ k takes q-th-power values at m (Lemma 1: by rule 90's confinement, or by
e' ≡ ±2^{a} (mod m) with q | A_e), then every nonzero eigenvalue of f is a q-th power in F(2^s)*.
It contains splitting (no h) and powers (no units) as special cases. The new case is the mixture.

**The other seven (4850, 5972, 13822, 22064, 25183, 27390, 28586) are not explained, and I think
they are chance.** The census's chance model is wrong at 37 by a factor of about 9. It gives every
free class a cube probability of 1/3. But the axis and diagonal classes are cubes for 93.5% of the
family. A rule's axis value is H(t_j) with deg H ≤ 4, and of the 31 such H only the two quartic
halves of Ψ₁₇ are not products of whole Ψ_e's (units at 37); the diagonal is the same with H².
With the measured per-class rates, classes still independent, the expected number of chance
confinements at 37 is 5.71, against 0.63 in the census model (which my code reproduces), and 7
remain. The independent model with these rates also fits the counts of rules with 1, 2 and 3
non-cube classes (82, 560, 2,022 observed against 80, 534, 2,044 predicted). Only the all-cube
count is in excess, 42 against 5.2. Of those 42, 35 are explained by mechanisms 1–6 and this one,
and the 7 left are within chance.

## Deliverables

* `mechanism.py`: `condition(f, m)`. It factors f over GF(2): line factors are found as Newton-edge
  contents in unimodular coordinates, and the two-dimensional core is tested as a q-th power by
  Kronecker substitution, a square-free decomposition and an exact check. Units are grouped by
  (direction, e). Each needed unit is tested with Lemma 1; the only field computation is rule
  90's own confinement (`halffrob._rule90_powers`). It returns the lcm with the previous pilots'
  `certificate.condition` (which includes `halffrob`). No eigenvalue of f is computed.
  Timing: 30–40 s for the atlas at one m (37, 299); 25–40 s for 2,000 family rules at m ≤ 125.
* `proposal.md`: the theorem and proof, the targets, the chance analysis, what was ruled out,
  reach and predictions.
* `proposal.py`: 32 checks, all held (`scratch/proposal_out.txt`).
* `proofs/LatticeProofs/Pilot.lean`: `period_rN_dvd_37 : period 37 rNOffsets ∣ 87381` for the
  nine rules, and `period_rN_dvd_61 : period 61 rNOffsets ∣ 357913941` for 3461, 26883 and 18246.
  So every eigenvalue is a cube of F(2^18), respectively F(2^30). The build succeeds with
  `lake build LatticeProofs.Pilot`, and every one of the twelve depends only on propext,
  Classical.choice and Quot.sound (`scratch/PilotAxioms.out`). No sorry, no new axiom, no
  native_decide. At 37 they use the fourth pilot's certificate `Cubes37.r90_val`; the 61 proofs
  are self-contained (t⁶⁴ = t(z³), (t + 1)² = t⁶³).

## How I checked it

* Every claim of the mechanism on all 1,274 atlas rules, at every odd m from 3 to 301: 1,081
  claims, none false (`scratch/sweep_atlas.log`, eigenvalues computed directly with
  `tools/eigen.py`).
* Every claim on all 32,767 family rules at 39 odd sizes from 13 to 125
  (`scratch/famsweep.log`), and again at 31 composite sizes up to 143 after the last change, which
  allowed prime e with gcd(e, m) > 1 (`scratch/famsweep_v2.log`): none false. Family claims at
  13, 37, 61, 95, 101, 111, 141, 143, 169 and 181 were also checked against the eigenvalues
  (`scratch/newclaims.log`).
* The nine identities were checked symbolically (`proposal.py`) and in Lean.
* Predictions verified directly up to 151 (`scratch/predict.py`). All nine are confined wherever
  rule 90 is confined to the cubes (≤ 301: 37, 95, 101, 111, 141, 197, 203, 269). The bottom row is
  also confined at 13, 61, 143, 169, 181, 193, 247, 253, 259 and 299. Of these, 13, 95, 101, 111,
  141 and 143 are below 151 and outside the census.

## Reach

* The 19 targets: 12 (the nine at 37, the three at 61).
* Census remainder: those 12 rows; nothing at 21, 25 or 29.
* Mixed-kind claims in the family at all checked sizes are exactly these nine rules
  (`scratch/classify_family.log`). The atlas contains no rule of the mixed kind; its claims are
  all splitting or powers.

## What I tried that failed (for the seven)

* Laurent factorisation over GF(2): five are irreducible; 13822 and 27390 split into two
  multiplicity-one non-unit factors.
* Images under integer matrices with entries in [−3, 3] (|det| ≤ 9, prime to m), put to the same
  condition: nothing, for the seven or for any census remainder at 21, 25 and 29.
* f · M = C · C(x^n, y^n), C ⊂ [−1, 1]², n = 3…13: nothing.
* λ_f λ_U λ_g³ ∈ F(2⁹) or F(2⁶) at all classes, with g any family rule and U ∈ {1, a + b, ab,
  (a + 1)(b + 1), (a + b)²}: nothing. This generalises the previous certificates to arbitrary cube
  multipliers.
* f(x³, y³) divisible by f²: no.
* Line by line, each class proven separately by a Ψ-factorisation of the line restriction, over
  all 36 representative direction vectors: it works on the axis, the diagonal and a few other
  classes, and fails on at least five of the eleven classes of every one of the seven.

## What I am unsure of

* That the seven are chance. The refined model assumes independent classes and takes its rates
  from the same population. It explains the excess (7 against 5.7) but does not exclude a
  mechanism I did not think of.
* At 29 the remainder, 13 against 7.85 refined, is borderline (Poisson p ≈ 0.05), and I found no
  structure there.
* The condition is sufficient, not necessary. It sees only exact factorisations over GF(2), not
  identities that hold only on the m-torus.
