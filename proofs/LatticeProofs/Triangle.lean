/-
The triangular torus (docs/proofs.md).

The triangular lattice has two cells per unit cell, an up triangle and a down triangle, and its
translations form Z^2 (the atlas's tau coordinates). A triangular torus is a torus (G, omega) of
those translations with two layers of cells over it. On the atlas's torus of side n,
G = Z/n x Z/(n/2) (`Tori.lean`). On the rhombic torus of side m, G = (Z/m)^2. A rule is four
neighbourhoods. They are the translations an up cell reads among up cells (uu) and among down
cells (ud), and those a down cell reads among up cells (du) and among down cells (dd).

* `gtriStep_twice`: if the rule's matrix [[uu, ud], [du, dd]] squares to s I as Laurent
  polynomials, two steps of the rule are one step of the plane rule S on each layer.
* `gtriPeriod_div_two`: so the period P satisfies P / gcd(P, 2) = P(S), on every torus.
* `even_of_isEventualPeriod`: if the rule swaps the parities of the two layers' live-cell counts,
  every period is even.
* `gtriPeriod_eq_two_mul`: then the period is exactly 2 P(S).
-/
import LatticeProofs.GroupRing

namespace LatticeProofs

open Finset

/-- A rule on the triangular lattice: the translations an up cell reads among up cells (uu) and
among down cells (ud), and those a down cell reads among up cells (du) and down cells (dd). -/
structure TriRule where
  uu : Finset (ℤ × ℤ)
  ud : Finset (ℤ × ℤ)
  du : Finset (ℤ × ℤ)
  dd : Finset (ℤ × ℤ)

section General

variable {G : Type*} [AddCommGroup G] (ω : ℤ × ℤ →+ G)

/-- One step of a triangle rule on the triangular torus over (G, omega): its up cells and its down
cells. -/
def gtriStep (R : TriRule) (c : (G → ZMod 2) × (G → ZMod 2)) : (G → ZMod 2) × (G → ZMod 2) :=
  (gstep ω R.uu c.1 + gstep ω R.ud c.2, gstep ω R.du c.1 + gstep ω R.dd c.2)

/-- The period of a triangle rule on the triangular torus over (G, omega). -/
noncomputable def gtriPeriod (R : TriRule) : ℕ := eventualPeriod (gtriStep ω R)

/-- **Two steps are one step of the square, on each layer.** If the rule's matrix squares to S I
as Laurent polynomials, two steps of the rule are one step of S on each layer, on every torus. -/
theorem gtriStep_twice {R : TriRule} {S : Finset (ℤ × ℤ)}
    (h1 : grp R.uu * grp R.uu + grp R.ud * grp R.du = grp S)
    (h2 : grp R.uu * grp R.ud + grp R.ud * grp R.dd = 0)
    (h3 : grp R.du * grp R.uu + grp R.dd * grp R.du = 0)
    (h4 : grp R.du * grp R.ud + grp R.dd * grp R.dd = grp S)
    (c : (G → ZMod 2) × (G → ZMod 2)) :
    gtriStep ω R (gtriStep ω R c) = Prod.map (gstep ω S) (gstep ω S) c := by
  obtain ⟨u, w⟩ := c
  set A := act ω (grp R.uu)
  set B := act ω (grp R.ud)
  set C := act ω (grp R.du)
  set D := act ω (grp R.dd)
  have e1 : ∀ v, A (A v) + B (C v) = act ω (grp S) v := fun v => by
    rw [← h1, map_add, map_mul, map_mul]; rfl
  have e2 : ∀ v, A (B v) + B (D v) = 0 := fun v => by
    have := congrArg (fun F => F v) (congrArg (act ω) h2)
    simpa [map_add, map_mul] using this
  have e3 : ∀ v, C (A v) + D (C v) = 0 := fun v => by
    have := congrArg (fun F => F v) (congrArg (act ω) h3)
    simpa [map_add, map_mul] using this
  have e4 : ∀ v, C (B v) + D (D v) = act ω (grp S) v := fun v => by
    rw [← h4, map_add, map_mul, map_mul]; rfl
  simp only [gtriStep, Prod.map, ← act_grp ω]
  refine Prod.ext_iff.2 ⟨?_, ?_⟩
  · show A (A u + B w) + B (C u + D w) = act ω (grp S) u
    rw [map_add, map_add, ← e1 u]
    have := e2 w
    calc A (A u) + A (B w) + (B (C u) + B (D w))
        = A (A u) + B (C u) + (A (B w) + B (D w)) := by abel
      _ = A (A u) + B (C u) := by rw [this, add_zero]
  · show C (A u + B w) + D (C u + D w) = act ω (grp S) w
    rw [map_add, map_add, ← e4 w]
    have := e3 u
    calc C (A u) + C (B w) + (D (C u) + D (D w))
        = C (B w) + D (D w) + (C (A u) + D (C u)) := by abel
      _ = C (B w) + D (D w) := by rw [this, add_zero]

/-- For a rule with no same-orientation part, the matrix squares to (ud du) I. -/
theorem gtriStep_twice_of_cross {R : TriRule} {S : Finset (ℤ × ℤ)} (huu : R.uu = ∅)
    (hdd : R.dd = ∅) (h : grp R.ud * grp R.du = grp S) (c : (G → ZMod 2) × (G → ZMod 2)) :
    gtriStep ω R (gtriStep ω R c) = Prod.map (gstep ω S) (gstep ω S) c :=
  gtriStep_twice ω (by simp [huu, grp_empty, h]) (by simp [huu, hdd, grp_empty])
    (by simp [huu, hdd, grp_empty]) (by simp [hdd, grp_empty, mul_comm, h]) c

/-- Then the period P satisfies P / gcd(P, 2) = P(S). -/
theorem gtriPeriod_div_two [Finite G] {R : TriRule} {S : Finset (ℤ × ℤ)}
    (hR : ∀ c, gtriStep ω R (gtriStep ω R c) = Prod.map (gstep ω S) (gstep ω S) c) :
    gtriPeriod ω R / Nat.gcd (gtriPeriod ω R) 2 = gperiod ω S := by
  have hf : (gtriStep ω R)^[2] = Prod.map (gstep ω S) (gstep ω S) := funext fun c => hR c
  rw [gtriPeriod, ← eventualPeriod_iterate (by norm_num : 0 < 2), hf, eventualPeriod_prodMap]
  rfl

variable [Fintype G] [DecidableEq G]

/-- The number of live cells, mod 2. -/
def total (s : G → ZMod 2) : ZMod 2 := ∑ v, s v

omit [AddCommGroup G] [DecidableEq G] in
theorem total_add (s s' : G → ZMod 2) : total (s + s') = total s + total s' := by
  simp [total, Finset.sum_add_distrib]

omit [DecidableEq G] in
/-- One step multiplies the live-cell count, mod 2, by the neighbourhood's size. -/
theorem total_gstep (D : Finset (ℤ × ℤ)) (s : G → ZMod 2) :
    total (gstep ω D s) = D.card * total s := by
  simp only [total, gstep]
  rw [Finset.sum_comm]
  calc ∑ d ∈ D, ∑ v, s (v + ω d) = ∑ d ∈ D, ∑ v, s v :=
        Finset.sum_congr rfl fun d _ => Equiv.sum_comp (Equiv.addRight (ω d)) s
    _ = D.card * ∑ v, s v := by rw [Finset.sum_const, nsmul_eq_mul]

/-- The live-cell counts of the two layers, mod 2. -/
def totals (c : (G → ZMod 2) × (G → ZMod 2)) : ZMod 2 × ZMod 2 := (total c.1, total c.2)

variable {ω}

omit [DecidableEq G] in
theorem totals_gtriStep {R : TriRule} (huu : (R.uu.card : ZMod 2) = 0)
    (hud : (R.ud.card : ZMod 2) = 1) (hdu : (R.du.card : ZMod 2) = 1)
    (hdd : (R.dd.card : ZMod 2) = 0) (c : (G → ZMod 2) × (G → ZMod 2)) :
    totals (gtriStep ω R c) = (totals c).swap := by
  simp [totals, gtriStep, total_add, total_gstep, huu, hud, hdu, hdd]

/-- If a rule swaps the parities of the layers' live-cell counts, every period is even: from a
single live up cell, the up layer's count is odd exactly at even times. -/
theorem even_of_isEventualPeriod {R : TriRule} (huu : (R.uu.card : ZMod 2) = 0)
    (hud : (R.ud.card : ZMod 2) = 1) (hdu : (R.du.card : ZMod 2) = 1)
    (hdd : (R.dd.card : ZMod 2) = 0) {p : ℕ} (h : IsEventualPeriod (gtriStep ω R) p) :
    Even p := by
  obtain ⟨t, ht⟩ := h
  let δ : (G → ZMod 2) × (G → ZMod 2) := (Pi.single 0 1, 0)
  have hτ : ∀ n, totals ((gtriStep ω R)^[n] δ) = if Even n then (1, 0) else (0, 1) := by
    intro n
    induction n with
    | zero => simp [δ, totals, total, Finset.sum_pi_single']
    | succ n ih =>
      rw [Function.iterate_succ_apply', totals_gtriStep huu hud hdu hdd, ih]
      by_cases hn : Even n <;> simp [hn, Nat.even_add_one]
  have h := congrArg (fun F => totals (F δ)) ht
  simp only [hτ] at h
  have key : Even (t + p) ↔ Even t := by
    by_cases h1 : Even t <;> by_cases h2 : Even (t + p) <;> simp [h1, h2] at h ⊢
  rw [Nat.even_add] at key
  tauto

variable (ω) in
/-- **The period of a triangle rule is twice its square's.** If two steps are one step of S on
each layer, and the rule swaps the parities of the layers' live-cell counts, its period is
exactly 2 P(S), on every torus. -/
theorem gtriPeriod_eq_two_mul {R : TriRule} {S : Finset (ℤ × ℤ)}
    (hR : ∀ c, gtriStep ω R (gtriStep ω R c) = Prod.map (gstep ω S) (gstep ω S) c)
    (huu : (R.uu.card : ZMod 2) = 0) (hud : (R.ud.card : ZMod 2) = 1)
    (hdu : (R.du.card : ZMod 2) = 1) (hdd : (R.dd.card : ZMod 2) = 0) :
    gtriPeriod ω R = 2 * gperiod ω S := by
  have h := gtriPeriod_div_two ω hR
  have h2 : 2 ∣ gtriPeriod ω R :=
    even_iff_two_dvd.1 (even_of_isEventualPeriod huu hud hdu hdd (eventualPeriod_spec _).2)
  rw [Nat.gcd_eq_right h2] at h
  rw [← h, Nat.mul_div_cancel' h2]

end General

/-! ### The rhombic torus of side m -/

section Rhombic

variable (m : ℕ) [NeZero m]

/-- One step on the rhombic triangular torus of side m: (Z/m)^2 unit cells. -/
def triStep (R : TriRule) : Config m × Config m → Config m × Config m :=
  gtriStep (offsetHom m) R

/-- The period of a triangle rule on the rhombic triangular torus of side m. -/
noncomputable def triPeriod (R : TriRule) : ℕ := gtriPeriod (offsetHom m) R

end Rhombic

end LatticeProofs
