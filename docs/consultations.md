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

**What came of it.** Fable's criterion and pyramid recipe make predictions at primes nobody has
looked at; they are registered and tested in `examples/fable-units`. Two models finding the same
argument for rule 90 independently is good evidence that it is the right explanation, and it is
better than the computed cube root in the library's `Cubes37.lean`.
