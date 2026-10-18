/-
The triangular torus (docs/proofs.md).

The triangular lattice has two cells per unit cell, an up triangle and a down triangle, and its
translations form Z^2 (the atlas's tau coordinates). The triangular torus of side m is its
quotient by m Z^2: m^2 unit cells and 2 m^2 cells. A rule is four neighbourhoods. They are the
translations an up cell reads among up cells (uu) and among down cells (ud), and those a down cell
reads among up cells (du) and among down cells (dd). The atlas's torus of side n = 2m has this
torus's translation group as its odd quotient. So the odd part of a rule's period there is the
odd part of its period here; that reduction is not formalised.

* `triStep_triStep`: take a rule with no same-orientation part whose two cross eigenvalues
  multiply, at every character, to the eigenvalue of a square-torus rule S. Then two steps of the
  rule are one step of S on each layer.
* `even_of_isEventualPeriod`: if the rule swaps the parities of the two layers' live-cell counts,
  every period is even.
* `triPeriod_eq_two_mul`: together, on a torus of odd side, the rule's period is exactly twice
  S's.
-/
import LatticeProofs.Bridge

namespace LatticeProofs

open Finset

/-- A rule on the triangular lattice: the translations an up cell reads among up cells (uu) and
among down cells (ud), and those a down cell reads among up cells (du) and down cells (dd). -/
structure TriRule where
  uu : Finset (ℤ × ℤ)
  ud : Finset (ℤ × ℤ)
  du : Finset (ℤ × ℤ)
  dd : Finset (ℤ × ℤ)

section Triangle

variable (m : ℕ) [NeZero m]

/-- A configuration of the triangular torus of side m: its up cells and its down cells, one of
each per unit cell. -/
abbrev TriConfig := Config m × Config m

/-- One step: every cell becomes the sum mod 2 of the cells its rule reads. -/
def triStep (R : TriRule) (c : TriConfig m) : TriConfig m :=
  (step m R.uu c.1 + step m R.ud c.2, step m R.du c.1 + step m R.dd c.2)

/-- The period of a triangle rule on the triangular torus of side m: its least positive period. -/
noncomputable def triPeriod (R : TriRule) : ℕ := eventualPeriod (triStep m R)

/-- The number of live cells, mod 2. -/
def total (s : Config m) : ZMod 2 := ∑ v, s v

theorem total_add (s s' : Config m) : total m (s + s') = total m s + total m s' := by
  simp [total, Finset.sum_add_distrib]

/-- One step multiplies the live-cell count, mod 2, by the neighbourhood's size. -/
theorem total_step (D : Finset (ℤ × ℤ)) (s : Config m) :
    total m (step m D s) = D.card * total m s := by
  simp only [total, step]
  rw [Finset.sum_comm]
  calc ∑ d ∈ D, ∑ v, s (v + offset m d) = ∑ d ∈ D, ∑ v, s v :=
        Finset.sum_congr rfl fun d _ => Equiv.sum_comp (Equiv.addRight (offset m d)) s
    _ = D.card * ∑ v, s v := by rw [Finset.sum_const, nsmul_eq_mul]

/-- The live-cell counts of the two layers, mod 2. -/
def totals (c : TriConfig m) : ZMod 2 × ZMod 2 := (total m c.1, total m c.2)

variable {m}

theorem totals_triStep {R : TriRule} (huu : (R.uu.card : ZMod 2) = 0)
    (hud : (R.ud.card : ZMod 2) = 1) (hdu : (R.du.card : ZMod 2) = 1)
    (hdd : (R.dd.card : ZMod 2) = 0) (c : TriConfig m) :
    totals m (triStep m R c) = (totals m c).swap := by
  simp [totals, triStep, total_add, total_step, huu, hud, hdu, hdd]

/-- If a rule swaps the parities of the layers' live-cell counts, every period is even: from a
single live up cell, the up layer's count is odd exactly at even times. -/
theorem even_of_isEventualPeriod {R : TriRule} (huu : (R.uu.card : ZMod 2) = 0)
    (hud : (R.ud.card : ZMod 2) = 1) (hdu : (R.du.card : ZMod 2) = 1)
    (hdd : (R.dd.card : ZMod 2) = 0) {p : ℕ} (h : IsEventualPeriod (triStep m R) p) :
    Even p := by
  obtain ⟨t, ht⟩ := h
  let δ : TriConfig m := (Pi.single 0 1, 0)
  have hτ : ∀ n, totals m ((triStep m R)^[n] δ) = if Even n then (1, 0) else (0, 1) := by
    intro n
    induction n with
    | zero => simp [δ, totals, total, Finset.sum_pi_single']
    | succ n ih =>
      rw [Function.iterate_succ_apply', totals_triStep huu hud hdu hdd, ih]
      by_cases hn : Even n <;> simp [hn, Nat.even_add_one]
  have h := congrArg (fun F => totals m (F δ)) ht
  simp only [hτ] at h
  have key : Even (t + p) ↔ Even t := by
    by_cases h1 : Even t <;> by_cases h2 : Even (t + p) <;> simp [h1, h2] at h ⊢
  rw [Nat.even_add] at key
  tauto

/-- **Two steps of a triangle rule are one step of a square rule on each layer.** For a rule with
no same-orientation part, whose cross eigenvalues multiply to S's at every character. -/
theorem triStep_triStep {K : Type*} [Field K] [CharP K 2] {ζ : K} (hζ : IsPrimitiveRoot ζ m)
    {R : TriRule} {S : Finset (ℤ × ℤ)} (huu : R.uu = ∅) (hdd : R.dd = ∅)
    (h : ∀ j k, lam m ζ R.ud j k * lam m ζ R.du j k = lam m ζ S j k) (c : TriConfig m) :
    triStep m R (triStep m R c) = Prod.map (step m S) (step m S) c := by
  obtain ⟨u, w⟩ := c
  have h1 := hζ.pow_eq_one
  simp only [triStep, huu, hdd, step_empty, zero_add, add_zero, Prod.map]
  refine Prod.ext_iff.2 ⟨eq_of_hat_eq hζ fun j _ k _ => ?_, eq_of_hat_eq hζ fun j _ k _ => ?_⟩
  · simp only [hat_step h1]
    rw [← mul_assoc, h]
  · simp only [hat_step h1]
    rw [← mul_assoc, mul_comm (lam m ζ R.du j k), h]

/-- **The period of a triangle rule is twice its square's.** Suppose two steps of R are one step
of the square-torus rule S on each layer, and R swaps the parities of the layers' live-cell
counts. Then on the triangular torus of odd side m, R's period is exactly twice S's. -/
theorem triPeriod_eq_two_mul (hm : Odd m) {R : TriRule} {S : Finset (ℤ × ℤ)}
    (hR : ∀ c, triStep m R (triStep m R c) = Prod.map (step m S) (step m S) c)
    (huu : (R.uu.card : ZMod 2) = 0) (hud : (R.ud.card : ZMod 2) = 1)
    (hdu : (R.du.card : ZMod 2) = 1) (hdd : (R.dd.card : ZMod 2) = 0) :
    triPeriod m R = 2 * period m S := by
  set f := triStep m R
  have hfS : ∀ n, f^[2 * n] = Prod.map (step m S)^[n] (step m S)^[n] := by
    intro n
    rw [Function.iterate_mul, ← Prod.map_iterate]
    congr 1
    funext c
    exact hR c
  obtain ⟨hP, t₀, ht₀⟩ := eventualPeriod_spec f
  set P := eventualPeriod f
  -- S's period divides R's: every period of R is one of S.
  have h1 : period m S ∣ P := by
    rw [← isPeriod_iff_period_dvd]
    refine ⟨t₀, funext fun s => ?_⟩
    have e : f^[2 * (t₀ + P)] = f^[2 * t₀] := by
      rw [show 2 * (t₀ + P) = t₀ + t₀ + 2 * P by ring, show 2 * t₀ = t₀ + t₀ by ring]
      exact iterate_add_mul_eq ht₀ t₀ 2
    rw [hfS, hfS] at e
    exact congrArg Prod.fst (congrFun e (s, s))
  -- R's period divides twice S's: twice a period of S is one of R.
  have h2 : P ∣ 2 * period m S := by
    rw [← isEventualPeriod_iff_dvd]
    obtain ⟨_, t₁, ht₁⟩ := eventualPeriod_spec (step m S)
    have ht₁' : (step m S)^[t₁ + period m S] = (step m S)^[t₁] := ht₁
    refine ⟨2 * t₁, ?_⟩
    rw [show 2 * t₁ + 2 * period m S = 2 * (t₁ + period m S) by ring, hfS, hfS, ht₁']
  have h3 : Even P := even_of_isEventualPeriod huu hud hdu hdd (eventualPeriod_spec f).2
  have hodd := period_odd hm S
  show P = 2 * period m S
  obtain ⟨c, hc⟩ := h1
  have hc2 : c ∣ 2 := by
    apply Nat.dvd_of_mul_dvd_mul_left hodd.pos
    rw [← hc, mul_comm]
    exact h2
  rcases (Nat.dvd_prime Nat.prime_two).1 hc2 with rfl | rfl
  · rw [hc, mul_one] at h3
    exact absurd h3 (Nat.not_even_iff_odd.2 hodd)
  · rw [hc, mul_comm]

end Triangle

end LatticeProofs
