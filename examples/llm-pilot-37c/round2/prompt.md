This is the second round of the seventh pilot (ninth powers at m = 37). Your first-round work is this checkout, at your commit b5014b6: CARD.md, mechanism.py, proposal.md, proposal.py, report.md, proofs/LatticeProofs/Pilot.lean and scratch/.

**What the judge reports back from round 1** (the results it may share; it does not report the held-out ones):

- Library unchanged: yes.
- Targets: your condition explains 4 of the 5 (699738, 985232, 1431278, 1968276, each with q divisible by 9 at m = 37); not 4850.
- Soundness at the training sizes: it ran on every set without an error, and made 1,182 claims, none false.
- proposal.py: 42 checks, all passing.
- Lean: **Pilot.lean does not build** against the library, so no theorem is accepted. The build took 346 s; its errors:

```
error: LatticeProofs/Pilot.lean:94:12: Tactic `rewrite` failed: Did not find an occurrence of the pattern
  ⋯ + ⋯ + ⋯ * y ^ 4 + x⁻¹ ^ 5 * y ^ 5 + x⁻¹ ^ 4 * y⁻¹ ^ 5 + x⁻¹ ^ 4 * y⁻¹ + x⁻¹ ^ 4 * y + x⁻¹ ^ 4 * y ^ 5 +
    x⁻¹ ^ 3 * y⁻¹ ^ 5 +
    x⁻¹ ^ 3 * y⁻¹ +
    x⁻¹ ^ 3 * y +
    x⁻¹ ^ 3 * y ^ 5 +
    x⁻¹ ^ 2 * y⁻¹ ^ 5 +
    x⁻¹ ^ 2 * y⁻¹ +
    x⁻¹ ^ 2 * y +
    x⁻¹ ^ 2 * y ^ 5 +
    x⁻¹ * y⁻¹ ^ 4 +
    x⁻¹ * y⁻¹ ^ 3 +
    x⁻¹ * y⁻¹ ^ 2 +
    x⁻¹ * y⁻¹ +
    x⁻¹ * y +
    x⁻¹ * y ^ 2 +
    x⁻¹ * y ^ 3 +
    x⁻¹ * y ^ 4 +
    x * y⁻¹ ^ 4 +
    x * y⁻¹ ^ 3 +
    x * y⁻¹ ^ 2 +
    x * y⁻¹ +
    x * y +
    x * y ^ 2 +
    x * y ^ 3 +
    x * y ^ 4 +
    x ^ 2 * y⁻¹ ^ 5 +
    x ^ 2 * y⁻¹ +
    x ^ 2 * y +
    x ^ 2 * y ^ 5 +
    x ^ 3 * y⁻¹ ^ 5 +
    x ^ 3 * y⁻¹ +
    x ^ 3 * y +
    x ^ 3 * y ^ 5 +
    x ^ 4 * y⁻¹ ^ 5 +
    x ^ 4 * y⁻¹ +
    x ^ 4 * y +
    x ^ 4 * y ^ 5 +
    x ^ 5 * y⁻¹ ^ 5 +
    x ^ 5 * y⁻¹ ^ 4 +
    x ^ 5 * y⁻¹ ^ 3 +
    x ^ 5 * y⁻¹ ^ 2 +
    x ^ 5 * y ^ 2 +
    x ^ 5 * y ^ 3 +
    x ^ 5 * y ^ 4 +
    x ^ 5 * y ^ 5
in the target expression
  ev r1968276Offsets x y = ((x + x⁻¹) * (y + y⁻¹)) ^ 2 * vPoly x x⁻¹ y y⁻¹

K : Type u_1
inst✝¹ : Field K
inst✝ : CharP K 2
x y : K
hx : x ≠ 0
hy : y ≠ 0
⊢ ev r1968276Offsets x y = ((x + x⁻¹) * (y + y⁻¹)) ^ 2 * vPoly x x⁻¹ y y⁻¹
error: LatticeProofs/Pilot.lean:101:12: Tactic `rewrite` failed: Did not find an occurrence of the pattern
  ⋯ + ⋯ + ⋯ * y ^ 3 + x⁻¹ ^ 5 * y ^ 4 + x⁻¹ ^ 4 * y⁻¹ ^ 5 + x⁻¹ ^ 4 * y⁻¹ + x⁻¹ ^ 4 * y + x⁻¹ ^ 4 * y ^ 5 +
    x⁻¹ ^ 3 * y⁻¹ ^ 5 +
    x⁻¹ ^ 3 * y⁻¹ +
    x⁻¹ ^ 3 * y +
    x⁻¹ ^ 3 * y ^ 5 +
    x⁻¹ ^ 2 * y⁻¹ ^ 5 +
    x⁻¹ ^ 2 * y⁻¹ +
    x⁻¹ ^ 2 * y +
    x⁻¹ ^ 2 * y ^ 5 +
    x⁻¹ * y⁻¹ ^ 5 +
    x⁻¹ * y⁻¹ ^ 4 +
    x⁻¹ * y⁻¹ ^ 3 +
    x⁻¹ * y⁻¹ ^ 2 +
    x⁻¹ * y ^ 2 +
    x⁻¹ * y ^ 3 +
    x⁻¹ * y ^ 4 +
    x⁻¹ * y ^ 5 +
    x * y⁻¹ ^ 5 +
    x * y⁻¹ ^ 4 +
    x * y⁻¹ ^ 3 +
    x * y⁻¹ ^ 2 +
    x * y ^ 2 +
    x * y ^ 3 +
    x * y ^ 4 +
    x * y ^ 5 +
    x ^ 2 * y⁻¹ ^ 5 +
    x ^ 2 * y⁻¹ +
    x ^ 2 * y +
    x ^ 2 * y ^ 5 +
    x ^ 3 * y⁻¹ ^ 5 +
    x ^ 3 * y⁻¹ +
    x ^ 3 * y +
    x ^ 3 * y ^ 5 +
    x ^ 4 * y⁻¹ ^ 5 +
    x ^ 4 * y⁻¹ +
    x ^ 4 * y +
    x ^ 4 * y ^ 5 +
    x ^ 5 * y⁻¹ ^ 4 +
    x ^ 5 * y⁻¹ ^ 3 +
    x ^ 5 * y⁻¹ ^ 2 +
    x ^ 5 * y⁻¹ +
    x ^ 5 * y +
    x ^ 5 * y ^ 2 +
    x ^ 5 * y ^ 3 +
    x ^ 5 * y ^ 4
in the target expression
  ev r985232Offsets x y = ((x + x⁻¹) * (y + y⁻¹)) ^ 2 * (x + x⁻¹ + y + y⁻¹) * wPoly x x⁻¹ y y⁻¹

K : Type u_1
inst✝¹ : Field K
inst✝ : CharP K 2
x y : K
hx : x ≠ 0
hy : y ≠ 0
⊢ ev r985232Offsets x y = ((x + x⁻¹) * (y + y⁻¹)) ^ 2 * (x + x⁻¹ + y + y⁻¹) * wPoly x x⁻¹ y y⁻¹
error: LatticeProofs/Pilot.lean:109:12: Tactic `rewrite` failed: Did not find an occurrence of the pattern
  ⋯ + ⋯ + ⋯ * y ^ 2 + x⁻¹ ^ 2 * y ^ 4 + x⁻¹ * y⁻¹ ^ 5 + x⁻¹ * y⁻¹ ^ 3 + x⁻¹ * y⁻¹ + x⁻¹ + x⁻¹ * y + x⁻¹ * y ^ 3 +
    x⁻¹ * y ^ 5 +
    y⁻¹ ^ 5 +
    y⁻¹ ^ 4 +
    y⁻¹ ^ 3 +
    y⁻¹ ^ 2 +
    y⁻¹ +
    y +
    y ^ 2 +
    y ^ 3 +
    y ^ 4 +
    y ^ 5 +
    x * y⁻¹ ^ 5 +
    x * y⁻¹ ^ 3 +
    x * y⁻¹ +
    x +
    x * y +
    x * y ^ 3 +
    x * y ^ 5 +
    x ^ 2 * y⁻¹ ^ 4 +
    x ^ 2 * y⁻¹ ^ 2 +
    x ^ 2 +
    x ^ 2 * y ^ 2 +
    x ^ 2 * y ^ 4 +
    x ^ 3 * y⁻¹ ^ 5 +
    x ^ 3 * y⁻¹ ^ 3 +
    x ^ 3 * y⁻¹ +
    x ^ 3 +
    x ^ 3 * y +
    x ^ 3 * y ^ 3 +
    x ^ 3 * y ^ 5 +
    x ^ 4 * y⁻¹ ^ 4 +
    x ^ 4 * y⁻¹ ^ 2 +
    x ^ 4 +
    x ^ 4 * y ^ 2 +
    x ^ 4 * y ^ 4 +
    x ^ 5 * y⁻¹ ^ 5 +
    x ^ 5 * y⁻¹ ^ 3 +
    x ^ 5 * y⁻¹ +
    x ^ 5 +
    x ^ 5 * y +
    x ^ 5 * y ^ 3 +
    x ^ 5 * y ^ 5
in the target expression
  ev r1431278Offsets x y = ((x + x⁻¹) ^ 2 + (x + x⁻¹) + 1) * ((y + y⁻¹) ^ 2 + (y + y⁻¹) + 1) * vPoly x x⁻¹ y y⁻¹

K : Type u_1
inst✝¹ : Field K
inst✝ : CharP K 2
x y : K
hx : x ≠ 0
hy : y ≠ 0
⊢ ev r1431278Offsets x y = ((x + x⁻¹) ^ 2 + (x + x⁻¹) + 1) * ((y + y⁻¹) ^ 2 + (y + y⁻¹) + 1) * vPoly x x⁻¹ y y⁻¹
error: LatticeProofs/Pilot.lean:118:12: Tactic `rewrite` failed: Did not find an occurrence of the pattern
  ⋯ + ⋯ + ⋯ * ⋯ + x⁻¹ ^ 2 * y⁻¹ + x⁻¹ ^ 2 + x⁻¹ ^ 2 * y + x⁻¹ ^ 2 * y ^ 3 + x⁻¹ ^ 2 * y ^ 5 + x⁻¹ * y⁻¹ ^ 4 +
    x⁻¹ * y⁻¹ ^ 2 +
    x⁻¹ +
    x⁻¹ * y ^ 2 +
    x⁻¹ * y ^ 4 +
    y⁻¹ ^ 5 +
    y⁻¹ ^ 4 +
    y⁻¹ ^ 3 +
    y⁻¹ ^ 2 +
    y⁻¹ +
    y +
    y ^ 2 +
    y ^ 3 +
    y ^ 4 +
    y ^ 5 +
    x * y⁻¹ ^ 4 +
    x * y⁻¹ ^ 2 +
    x +
    x * y ^ 2 +
    x * y ^ 4 +
    x ^ 2 * y⁻¹ ^ 5 +
    x ^ 2 * y⁻¹ ^ 3 +
    x ^ 2 * y⁻¹ +
    x ^ 2 +
    x ^ 2 * y +
    x ^ 2 * y ^ 3 +
    x ^ 2 * y ^ 5 +
    x ^ 3 * y⁻¹ ^ 4 +
    x ^ 3 * y⁻¹ ^ 2 +
    x ^ 3 +
    x ^ 3 * y ^ 2 +
    x ^ 3 * y ^ 4 +
    x ^ 4 * y⁻¹ ^ 5 +
    x ^ 4 * y⁻¹ ^ 3 +
    x ^ 4 * y⁻¹ +
    x ^ 4 +
    x ^ 4 * y +
    x ^ 4 * y ^ 3 +
    x ^ 4 * y ^ 5 +
    x ^ 5 * y⁻¹ ^ 4 +
    x ^ 5 * y⁻¹ ^ 2 +
    x ^ 5 +
    x ^ 5 * y ^ 2 +
    x ^ 5 * y ^ 4
in the target expression
  ev r699738Offsets x y =
    ((x + x⁻¹) ^ 2 + (x + x⁻¹) + 1) * ((y + y⁻¹) ^ 2 + (y + y⁻¹) + 1) * (x + x⁻¹ + y + y⁻¹) * wPoly x x⁻¹ y y⁻¹

K : Type u_1
inst✝¹ : Field K
inst✝ : CharP K 2
x y : K
hx : x ≠ 0
hy : y ≠ 0
⊢ ev r699738Offsets x y =
    ((x + x⁻¹) ^ 2 + (x + x⁻¹) + 1) * ((y + y⁻¹) ^ 2 + (y + y⁻¹) + 1) * (x + x⁻¹ + y + y⁻¹) * wPoly x x⁻¹ y y⁻¹
error: LatticeProofs/Pilot.lean:287:4: (deterministic) timeout at `«Mathlib.Tactic.Ring.Common.evalAdd»`, maximum number of heartbeats (200000) has been reached

Note: Use `set_option maxHeartbeats <num>` to set the limit.

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
error: LatticeProofs/Pilot.lean:266:0: (deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached

Note: Use `set_option maxHeartbeats <num>` to set the limit.

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
error: LatticeProofs/Pilot.lean:342:14: Tactic `rewrite` failed: Did not find an occurrence of the pattern
  Y⁻¹ + Y
in the target expression
  (0 ^ 2 + 0 + 1) ^ 2 * (0 ^ 2 + 0 + 1) ^ 2 * ((Y + 1 * Y⁻¹) * (1 * Y⁻¹ + Y)) * (0 ^ 2 + 1) ^ 2 = 0

case pos
K : Type u_1
inst✝¹ : Field K
inst✝ : CharP K 2
Y : K
hY : Y ^ 37 = 1
h2 : 2 = 0
hY0 : Y ≠ 0
hX : 1 ^ 37 = 1
hX0 : 1 ≠ 0
hid :
  wPoly (1 ^ 2) (1 ^ 2)⁻¹ (Y ^ 2) (Y ^ 2)⁻¹ * ((1 + 1⁻¹) * (Y + Y⁻¹) * (1 * Y + 1⁻¹ * Y⁻¹) * (1 * Y⁻¹ + 1⁻¹ * Y)) =
    shNat 1 Y
n1 : 1 + 1⁻¹ = 0
n2 : Y + Y⁻¹ = 0
n2' : Y⁻¹ + Y = 0
⊢ (0 ^ 2 + 0 + 1) ^ 2 * (0 ^ 2 + 0 + 1) ^ 2 * ((Y + 1 * Y⁻¹) * (1 * Y⁻¹ + Y)) * (0 ^ 2 + 1) ^ 2 = 0
error: LatticeProofs/Pilot.lean:346:4: (deterministic) timeout at `«Mathlib.Tactic.Ring.Common.evalMulProd»`, maximum number of heartbeats (200000) has been reached

Note: Use `set_option maxHeartbeats <num>` to set the limit.

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
error: LatticeProofs/Pilot.lean:322:0: (deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached

Note: Use `set_option maxHeartbeats <num>` to set the limit.

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
error: LatticeProofs/Pilot.lean:395:8: (kernel) unknown constant 'LatticeProofs.Pilot37c.r1431278_val_sq'
error: LatticeProofs/Pilot.lean:399:8: (kernel) unknown constant 'LatticeProofs.Pilot37c.r699738_val_sq'
Some required targets logged failures:
- LatticeProofs.Pilot
error: build failed
(11 warnings not shown)
```

**This round's task: make the Lean proof build.** The four theorems period_r1968276_dvd, period_r985232_dvd, period_r1431278_dvd and period_r699738_dvd should keep their statements (`period 37 rXOffsets ∣ 29127`); everything else in Pilot.lean is yours to change, and you may split it into files under proofs/LatticeProofs/Pilot/. The judge accepts a theorem when the file builds against the real library, the sources contain no `axiom` declaration and no `native_decide`, and `#print axioms` shows only propext, Classical.choice and Quot.sound (so no `sorry`). The mechanism and the proposal are not part of this round: leave mechanism.py, proposal.md and proposal.py as they are.

**Tools.** lean_build builds Pilot.lean as the judge does and, when it builds, lists each theorem's axioms. lean_file checks a single scratch .lean file and is much faster for trying a lemma or a tactic; it may import LatticeProofs modules (LatticeProofs, LatticeProofs.Cubes37, ...) and the Mathlib modules the library's build compiled (about 2,500 of them; `import Mathlib` as a whole is not built here, and neither was it in round 1). mathlib's sources can be read and searched under mathlib/, and the library's under proofs/LatticeProofs/. scratch/gen_pilot.py and scratch/pilot_certs.json are your generator and certificates from round 1; run_python runs scratch scripts.

The round has a fixed API budget, so work economically: test pieces with lean_file before a full build, and prefer edit_file to rewriting whole files. When the four theorems build, or if you conclude you cannot get further, call finish with a short report: what you changed, the final build result and axioms, and anything still unproved.