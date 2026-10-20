# Consultations: other models on our questions

**Status: a record, kept as we go.** Besides the pilots, where one agent works a card in an
isolated container, we put questions we have already answered to other models, to gauge how hard
they are and to collect other routes and ideas. Every claim a consultant makes is checked by
machine before it counts, and anything it predicts is registered and tested like our own
predictions (`examples/fable-units`).

## The protocol

- **The same prompt to every model**, first without hints. A follow-up, if any, is recorded with
  the exact text, and it is the same for every model that gets it.
- **Independent answers.** No model sees another's answer before giving its own.
- **Checked by machine.** Every identity a consultant states is multiplied out again with the
  orchestrator's arithmetic, and every claim about eigenvalues is checked against `eigen.py`.
- **Graded against a rubric** written before the answers were read.
- **Predictions are registered** before they are tested.

## 1. The cubes at m = 37 (pilot 4's question), 2026-10-19 and 20

**The prompt** gave the five square rules of pilot 4 as unions of D4 orbits, the observation that
every nonzero eigenvalue of each is a cube in F(2^18) at m = 37, that a random rule does this about
once in 20,000 tries, that none does anything similar at any other odd m from 9 to 161, and that
the same holds for t(x) = x + 1/x; it asked why, for a general condition, and for a proof. **The
rubric**: the arithmetic 2^9 = -6 and 6^2 = -1 (mod 37), so the dilation by 6 acts as a Frobenius;
F(2^9) lies in the cubes; an identity that makes the rules invariant under it; rule 90's
confinement; the shared factor; a proof for all five.

**ChatGPT, unaided** (about 20 minutes, with code). It found the shared factor (f2, f3 and f5 are
f1 times uv, u + v and (1 + u)(1 + v), with u = x + 1/x, v = y + 1/y) and proved the claim with a
certificate: every nonzero value is a cube exactly when f^87381 is idempotent in the group algebra,
and it checked that identity for f1, f4 and rule 90 by computer. Correct (its script and our
eigenvalues agree: f1 has no zero eigenvalue, f4's zeros are exactly the lines k = +-6j), but the
criterion is equivalent to computing every eigenvalue, so it does not explain; it said so itself.

**ChatGPT, after a hint** (the same follow-up for any model: that its criterion confirms without
explaining, and pointing at its own observation that f4 vanishes on lines of slope +-6, with
6^2 = -1). In 35 minutes it gave a structural proof: the ratio R = D3/D2 of square sums is inverted
by the dilation by 6, which acts on traces as the 2^9-th power, and symmetry then puts a related
quantity in F(2^9), inside the cubes. It also proved rule 90's confinement at 37 by number theory:
the product of 1 - xi^a over the quadratic residues is a unit times sqrt 37 in Q(sqrt 37), equal to
37 - 6 sqrt 37, which is 1 mod 2. Every identity checked.

**Claude Fable** (one answer; whether it saw a hint is to be confirmed). The mechanism (each rule,
up to binomial factors, is invariant under the dilation by 31 = 2^9, with exact congruences such
as f4 · O(19,19) = O(15,15) + O(16,16) mod (x^37 - 1, y^37 - 1)); the same unit argument as ChatGPT,
reached independently; a general theorem with two conditions, one on the binomial "units" and one
on the structure; a criterion for the first, that eps^h lies in Z[sqrt p] for the fundamental unit
eps and class number h of Q(sqrt p); and predictions: the pyramid rules at 101 and 197. Every
identity checked, the pyramid at 101 is family rule 31801, which the sixth pilot's registered
census had already recorded as confined there, and the pyramid at 197 is confined, its neighbour
not. One slip: its list of primes where the criterion fails names 109 and 157, where 2 is not a
primitive root, and omits 173 and 181, which are eligible and do fail.

| | the mechanism | rule 90 at 37 | a general condition | predictions |
| --- | --- | --- | --- | --- |
| Pilot 4's agent (with its card, data and tools) | yes | computed | yes, run at 94 sizes | none |
| ChatGPT, unaided | no (a certificate) | computed | equivalent to computing | none |
| ChatGPT, after the hint | yes | by the unit of Q(sqrt 37) | abstract | none |
| Claude Fable | yes | by the unit, with a criterion | yes | yes, all correct where checked |

**What came of it.** Fable's criterion and pyramid recipe made predictions at primes nobody had
looked at, so they were registered and tested (below). Two models finding the same argument for
rule 90 independently is good evidence that it is the right explanation, and it is better than the
computed cube root in the library's `Cubes37.lean`.

## The registered test of Fable's criterion (`examples/fable-units`), 2026-10-20

**The claims.** For a prime p = 5 (mod 8) at which 2 is a primitive root, (U) rule 90 is confined
to the cubes at p (equivalently, 1 + zeta is a cube in F(2^(p-1))) exactly when eps^h lies in
Z[sqrt p], for the fundamental unit eps and class number h of Q(sqrt p); and at p = i^2 + 1 where
(U) holds, the pyramid rule (the centre and the square rings at radii 2, 4, ..., i/2 - 1) is
confined to the cubes, while the pyramid without its largest ring is not.

**The design.** The predictions come from number theory alone (`units.predicted`: eps from the
continued fraction of (1 + sqrt p)/2, h by counting cycles of reduced quadratic forms), with no
cyclotomic arithmetic. The truth comes from direct computation in GF(2)[x]/Phi_p
(`units.confined`: the norm of 1 + zeta to F(4); `units.pyramid_confined`: the norm of every
eigenvalue of the pyramid, one per orbit of doubling and the lattice's symmetries). The grid was
every eligible prime from 302 to 20,000 (405 of them) and the pyramid primes among them below
10,000 (677, 4357, 5477 and 8837). Every eligible prime up to 301 counts as seen. The predictions
were pushed at 08:32:54 UTC (`981793f`), and the run started at 08:33:03.

**The result: both claims held everywhere.**

- **(U), at 405 primes, none wrong.** 144 are confined: at 114 eps itself lies in Z[sqrt p] (a
  and b even in eps = (a + b sqrt p)/2), and at 30 eps does not but 3 divides h. At the other
  261, eps is not in Z[sqrt p], 3 does not divide h, and rule 90 is not confined. The class
  numbers reach 19 and the units 46 digits.
- **The pyramids, 4 of 4.** Each predicted pyramid is confined and each neighbour is not. The
  largest, at 8837 (i = 94, 23 rings), took 88 seconds; the whole run took 2.5 minutes.
- `lattice-lab verify --lab examples/fable-units`: the ledger's 417 entries chain, no problems.

**What the test does and does not show.** Both claims come with Fable's arguments, and filled in
they are proofs, so the test is a check of the argument and of the arithmetic at scale, not the
settling of a conjecture. Fable's step from (U) to eps^h is one line ("i.e."). It is Dirichlet's
class number formula: with eta and eta' the products of 1 - zeta^s over the quadratic residues and
non-residues, eta eta' = p and eta'/eta = eps^(2h), so eta = sqrt p eps^(-h). Since
sqrt p = 2 theta - 1 = 1 (mod 2), eta = 1 (mod 2) exactly when eps^h does, which is when eps^h
lies in Z + 2 O_K = Z[sqrt p]. For the pyramids, Fable's identity
sum_{r <= N} Q_r t(X) t(Y) = t(X/Y) t((XY)^(2N+2)) + t(XY) t((X/Y)^(2N+2)) (with 2N + 2 = i)
puts their values off the axes, up to rule-90 factors, in the field fixed by the dilation by i,
and since 2^((p-1)/4) = +-i with (p - 1)/4 odd, that field lies in the cubes. That the
neighbours fail is not part of any proof; it is an observation, and it held at all four. The one
error in Fable's answer stands: its list of primes where (U) fails names 109 and 157, where 2 is
not a primitive root, and omits 173 and 181.
