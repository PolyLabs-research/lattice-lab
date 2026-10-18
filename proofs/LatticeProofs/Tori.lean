/-
Every torus size: the reduction from even sizes to odd parts (docs/proofs.md).

Frobenius moves the steps (`gstep_iterate_two_pow`): 2^k steps of a rule are one step of the
rule with every translation multiplied by 2^k. On a torus whose 2-part has exponent 2^k, those
translations stay inside the cosets of the odd part, where the rule acts as it does on the odd
torus (`isEventualPeriod_restrict_iff`). So if f is a rule on the torus and f_odd the same rule
on its odd quotient, f^[2^k] has the periods of f_odd. Then P / gcd(P, 2^k) = P_odd: the odd part
of the period is the odd torus's period, and the 2-part divides 2^k.

* The square torus of side n = 2^k m': `period_dvd_two_pow_mul_iff`, `period_div_gcd_two_pow`,
  `period_eq_two_pow_mul`, and `period_eq_two_pow_mul_of_double`. The last says the 2-part at
  every size follows from the size 2m.
* The atlas's triangular torus of side n = 2^v m is Z/n x Z/(n/2) with
  (x, y) -> (x - y mod n, y mod n/2). Its 2-part has exponent 2^v (`triPeriod_div_gcd`).
* The atlas's hexagonal torus of side n = 2^v m is Z/2n x Z/(n/2) with
  (q, r) -> (q + 2r mod 2n, r mod n/2). Its 2-part has exponent 2^(v+1) (`hexPeriod_div_gcd`).

Both coordinate maps are those of docs/parity-lattices.md, and `tests/test_proofs.py` checks
that these tori have the atlas's periods.
-/
import LatticeProofs.Triangle

namespace LatticeProofs

open Finset

/-- Multiplication by N, from (Z/m')^2 into (Z/n)^2, when n divides N m'. -/
def cellMul (m' n N : ℕ) (h : n ∣ N * m') : Cell m' →+ Cell n :=
  (zmodMul m' n N h).prodMap (zmodMul m' n N h)

theorem cellMul_offset {m' n N : ℕ} (h : n ∣ N * m') (d : ℤ × ℤ) :
    cellMul m' n N h (offsetHom m' d) = offsetHom n (N • d) := by
  obtain ⟨a, b⟩ := d
  rw [Prod.smul_mk]
  simp only [cellMul, AddMonoidHom.coe_prodMap, Prod.map_apply, offsetHom_apply, offset,
    zmodMul_intCast]
  ext <;> simp

/-- If P / gcd(P, 2^k) = Q, then P = 2^a Q for some a ≤ k. -/
theorem eq_two_pow_mul_of_div_gcd {P Q k : ℕ} (h : P / Nat.gcd P (2 ^ k) = Q) :
    ∃ a ≤ k, P = 2 ^ a * Q := by
  obtain ⟨a, ha, hg⟩ := (Nat.dvd_prime_pow Nat.prime_two).1 (Nat.gcd_dvd_right P (2 ^ k))
  refine ⟨a, ha, ?_⟩
  rw [← h, hg, Nat.mul_div_cancel' (hg ▸ Nat.gcd_dvd_left P (2 ^ k))]

/-- n divides N (n / gcd(n, N)). -/
theorem dvd_mul_div_gcd (n N : ℕ) : n ∣ N * (n / Nat.gcd n N) := by
  obtain ⟨c, hc⟩ := Nat.gcd_dvd_right n N
  refine ⟨c, ?_⟩
  calc N * (n / Nat.gcd n N) = Nat.gcd n N * c * (n / Nat.gcd n N) := by rw [← hc]
    _ = c * (Nat.gcd n N * (n / Nat.gcd n N)) := by ring
    _ = n * c := by rw [Nat.mul_div_cancel' (Nat.gcd_dvd_left n N), mul_comm]

/-- If n divides N a, then n / gcd(n, N) divides a. -/
theorem div_gcd_dvd_of_dvd_mul {n N a : ℕ} (hn : 0 < n) (h : n ∣ N * a) :
    n / Nat.gcd n N ∣ a := by
  have hg : 0 < Nat.gcd n N := Nat.gcd_pos_of_pos_left N hn
  have h' : n / Nat.gcd n N * Nat.gcd n N ∣ N / Nat.gcd n N * a * Nat.gcd n N := by
    rw [Nat.div_mul_cancel (Nat.gcd_dvd_left n N), mul_right_comm,
      Nat.div_mul_cancel (Nat.gcd_dvd_right n N)]
    exact h
  exact (Nat.coprime_div_gcd_div_gcd hg).dvd_of_dvd_mul_left (Nat.dvd_of_mul_dvd_mul_right hg h')

/-! ### The square torus -/

section Square

/-- Multiplication by N is injective from (Z/m')^2 into (Z/n)^2 when m' = n / gcd(n, N). -/
theorem cellMul_injective_gcd {n N m' : ℕ} [NeZero n] [NeZero m'] (hm' : m' = n / Nat.gcd n N)
    (h : n ∣ N * m') : Function.Injective (cellMul m' n N h) := by
  have hz := zmodMul_injective (m' := m') (n := n) (N := N) h fun a ha => by
    rw [hm']
    exact div_gcd_dvd_of_dvd_mul (Nat.pos_of_ne_zero (NeZero.ne n)) ha
  exact hz.prodMap hz

/-- **Dilations.** On the square torus of side n, the rule N D has the period of D on the torus
of side n / gcd(n, N). -/
theorem period_image_smul {n N m' : ℕ} [NeZero n] [NeZero m'] (hN : 0 < N)
    (hm' : m' = n / Nat.gcd n N) (D : Finset (ℤ × ℤ)) :
    period n (D.image (N • ·)) = period m' D := by
  have h : n ∣ N * m' := by rw [hm']; exact dvd_mul_div_gcd n N
  rw [period_eq_gperiod, period_eq_gperiod]
  exact eventualPeriod_restrict hN (cellMul_offset h) (cellMul_injective_gcd hm' h) D

theorem cellMul_injective {m' n k : ℕ} [NeZero m'] (hn : n = 2 ^ k * m') (h : n ∣ 2 ^ k * m') :
    Function.Injective (cellMul m' n (2 ^ k) h) := by
  have hz := zmodMul_injective (m' := m') (n := n) (N := 2 ^ k) h fun a ha => by
    rw [hn] at ha
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) ha
  exact hz.prodMap hz

/-- **The even-size reduction.** On the square torus of side n = 2^k m', P(n) divides 2^k p
exactly when P(m') divides p. -/
theorem period_dvd_two_pow_mul_iff {n k m' : ℕ} [NeZero n] [NeZero m'] (hn : n = 2 ^ k * m')
    (D : Finset (ℤ × ℤ)) (p : ℕ) : period n D ∣ 2 ^ k * p ↔ period m' D ∣ p := by
  rw [period_eq_gperiod, period_eq_gperiod, gperiod, gperiod, ← isEventualPeriod_iff_dvd,
    ← isEventualPeriod_iff_dvd, ← isEventualPeriod_iterate_iff (k := 2 ^ k) (by positivity),
    gstep_iterate_two_pow]
  have h : n ∣ 2 ^ k * m' := by rw [hn]
  exact isEventualPeriod_restrict_iff (by positivity) (cellMul_offset h) (cellMul_injective hn h) D p

/-- So P(n) / gcd(P(n), 2^k) = P(m'). -/
theorem period_div_gcd_two_pow {n k m' : ℕ} [NeZero n] [NeZero m'] (hn : n = 2 ^ k * m')
    (D : Finset (ℤ × ℤ)) : period n D / Nat.gcd (period n D) (2 ^ k) = period m' D :=
  (eq_div_gcd_of_dvd_iff (by positivity) fun p => (period_dvd_two_pow_mul_iff hn D p).symm).symm

/-- **The odd part.** On the square torus of side n = 2^v m, the period is 2^a P(m) for some
a ≤ v. For odd m, P(m) is odd (`period_odd`), so it is the odd part of P(n). -/
theorem period_eq_two_pow_mul {n v m : ℕ} [NeZero n] [NeZero m] (hn : n = 2 ^ v * m)
    (D : Finset (ℤ × ℤ)) : ∃ a ≤ v, period n D = 2 ^ a * period m D :=
  eq_two_pow_mul_of_div_gcd (period_div_gcd_two_pow hn D)

/-- **The 2-part from the size 2m.** If P(2m) = 2 P(m), then P(2^v m) = 2^v P(m) for every
v ≥ 1. -/
theorem period_eq_two_pow_mul_of_double {n v m : ℕ} [NeZero n] [NeZero m] [NeZero (2 * m)]
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (D : Finset (ℤ × ℤ))
    (h2 : period (2 * m) D = 2 * period m D) : period n D = 2 ^ v * period m D := by
  obtain ⟨a, ha, hP⟩ := period_eq_two_pow_mul hn D
  have hn' : n = 2 ^ (v - 1) * (2 * m) := by
    rw [hn, ← mul_assoc, ← pow_succ, Nat.sub_add_cancel hv]
  have key := period_dvd_two_pow_mul_iff hn' D (period m D)
  have hpos : 0 < period m D := (eventualPeriod_spec (step m D)).1
  have hnot : ¬ period (2 * m) D ∣ period m D := by
    rw [h2]
    intro hd
    have := Nat.le_of_dvd hpos hd
    omega
  have hav : ¬ a ≤ v - 1 := fun hle =>
    hnot (key.1 (by rw [hP]; exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 hle) _))
  rw [hP, show a = v by omega]

end Square

/-! ### The atlas's triangular torus -/

section TriangularTorus

/-- The atlas's triangular torus of side n: its translation group, Z/n x Z/(n/2). -/
abbrev TriCell (n : ℕ) := ZMod n × ZMod (n / 2)

/-- The lattice's translations on the atlas's triangular torus of side n:
(x, y) -> (x - y mod n, y mod n/2). -/
def triHom (n : ℕ) : ℤ × ℤ →+ TriCell n :=
  ((Int.castAddHom (ZMod n)).comp (AddMonoidHom.fst ℤ ℤ - AddMonoidHom.snd ℤ ℤ)).prod
    ((Int.castAddHom (ZMod (n / 2))).comp (AddMonoidHom.snd ℤ ℤ))

/-- The period of a triangle rule on the atlas's triangular torus of side n. -/
noncomputable def atlasTriPeriod (n : ℕ) (R : TriRule) : ℕ := gtriPeriod (triHom n) R

/-- Multiplication by N from (Z/m)^2 into the triangular torus: (a, b) -> (N (a - b), N b). -/
def triMul (m n N : ℕ) (h1 : n ∣ N * m) (h2 : n / 2 ∣ N * m) : Cell m →+ TriCell n :=
  ((zmodMul m n N h1).comp (AddMonoidHom.fst _ _ - AddMonoidHom.snd _ _)).prod
    ((zmodMul m (n / 2) N h2).comp (AddMonoidHom.snd _ _))

theorem triMul_offset {m n N : ℕ} (h1 : n ∣ N * m) (h2 : n / 2 ∣ N * m) (d : ℤ × ℤ) :
    triMul m n N h1 h2 (offsetHom m d) = triHom n (N • d) := by
  obtain ⟨a, b⟩ := d
  rw [Prod.smul_mk]
  simp only [triMul, triHom, AddMonoidHom.prod_apply, AddMonoidHom.comp_apply,
    AddMonoidHom.sub_apply, AddMonoidHom.coe_fst, AddMonoidHom.coe_snd, offsetHom_apply, offset,
    ← Int.cast_sub, zmodMul_intCast, Int.coe_castAddHom]
  ext <;> simp; ring

/-- The half side: n / 2 = 2^(v-1) m when n = 2^v m and v ≥ 1. -/
theorem half_eq {n v m : ℕ} (hv : 1 ≤ v) (hn : n = 2 ^ v * m) : n / 2 = 2 ^ (v - 1) * m := by
  rw [hn, show 2 ^ v * m = 2 * (2 ^ (v - 1) * m) by
    rw [← mul_assoc, ← pow_succ', Nat.sub_add_cancel hv]]
  exact Nat.mul_div_cancel_left _ (by norm_num)

theorem triMul_injective {m n v : ℕ} [NeZero m] (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m)
    (h1 : n ∣ 2 ^ v * m) (h2 : n / 2 ∣ 2 ^ v * m) :
    Function.Injective (triMul m n (2 ^ v) h1 h2) := by
  have i1 := zmodMul_injective h1 fun a ha => by
    rw [hn] at ha
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) ha
  have i2 := zmodMul_injective h2 fun b hb => by
    rw [half_eq hv hn, show 2 ^ v * b = 2 ^ (v - 1) * (b * 2) by
      rw [mul_comm b, ← mul_assoc, ← pow_succ, Nat.sub_add_cancel hv]] at hb
    exact (Nat.coprime_two_right.2 hm).dvd_of_dvd_mul_right
      (Nat.dvd_of_mul_dvd_mul_left (by positivity) hb)
  refine (injective_iff_map_eq_zero _).2 fun ⟨a, b⟩ h => ?_
  simp only [triMul, AddMonoidHom.prod_apply, AddMonoidHom.comp_apply, AddMonoidHom.sub_apply,
    AddMonoidHom.coe_fst, AddMonoidHom.coe_snd, Prod.mk_eq_zero] at h
  have hb : b = 0 := i2 (h.2.trans (map_zero _).symm)
  have hab : a - b = 0 := i1 (h.1.trans (map_zero _).symm)
  rw [hb, sub_zero] at hab
  rw [hab, hb]
  rfl

/-- **The reduction on the atlas's triangular torus.** For n = 2^v m with m odd and v ≥ 1, a plane
rule's period P there satisfies P / gcd(P, 2^v) = P(m), its period on the square torus of side m.
So P = 2^a P(m) for some a ≤ v. -/
theorem triPeriod_div_gcd {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (D : Finset (ℤ × ℤ)) :
    gperiod (triHom n) D / Nat.gcd (gperiod (triHom n) D) (2 ^ v) = period m D := by
  have h1 : n ∣ 2 ^ v * m := hn ▸ dvd_rfl
  have h2 : n / 2 ∣ 2 ^ v * m := by
    rw [half_eq hv hn]
    exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 (Nat.sub_le v 1)) m
  refine (eq_div_gcd_of_dvd_iff (by positivity) fun p => ?_).symm
  rw [period_eq_gperiod, gperiod, gperiod, ← isEventualPeriod_iff_dvd, ← isEventualPeriod_iff_dvd,
    ← isEventualPeriod_iterate_iff (k := 2 ^ v) (by positivity), gstep_iterate_two_pow]
  exact (isEventualPeriod_restrict_iff (by positivity) (triMul_offset h1 h2)
    (triMul_injective hm hv hn h1 h2) D p).symm

end TriangularTorus

/-! ### The atlas's hexagonal torus -/

section HexagonalTorus

/-- The atlas's hexagonal torus of side n: its translation group, Z/2n x Z/(n/2). -/
abbrev HexCell (n : ℕ) := ZMod (2 * n) × ZMod (n / 2)

/-- The lattice's translations, in axial coordinates, on the atlas's hexagonal torus of side n:
(q, r) -> (q + 2r mod 2n, r mod n/2). -/
def hexHom (n : ℕ) : ℤ × ℤ →+ HexCell n :=
  ((Int.castAddHom (ZMod (2 * n))).comp (AddMonoidHom.fst ℤ ℤ + 2 • AddMonoidHom.snd ℤ ℤ)).prod
    ((Int.castAddHom (ZMod (n / 2))).comp (AddMonoidHom.snd ℤ ℤ))

/-- The period of a hexagon rule on the atlas's hexagonal torus of side n. -/
noncomputable def hexPeriod (n : ℕ) (D : Finset (ℤ × ℤ)) : ℕ := gperiod (hexHom n) D

/-- Multiplication by N from (Z/m)^2 into the hexagonal torus: (a, b) -> (N (a + 2b), N b). -/
def hexMul (m n N : ℕ) (h1 : 2 * n ∣ N * m) (h2 : n / 2 ∣ N * m) : Cell m →+ HexCell n :=
  ((zmodMul m (2 * n) N h1).comp (AddMonoidHom.fst _ _ + 2 • AddMonoidHom.snd _ _)).prod
    ((zmodMul m (n / 2) N h2).comp (AddMonoidHom.snd _ _))

theorem hexMul_offset {m n N : ℕ} (h1 : 2 * n ∣ N * m) (h2 : n / 2 ∣ N * m) (d : ℤ × ℤ) :
    hexMul m n N h1 h2 (offsetHom m d) = hexHom n (N • d) := by
  obtain ⟨a, b⟩ := d
  have e : ((a : ZMod m) + 2 • (b : ZMod m)) = ((a + 2 * b : ℤ) : ZMod m) := by
    push_cast; rw [two_nsmul, two_mul]
  rw [Prod.smul_mk]
  simp only [hexMul, hexHom, AddMonoidHom.prod_apply, AddMonoidHom.comp_apply,
    AddMonoidHom.add_apply, AddMonoidHom.coe_fst, AddMonoidHom.coe_snd, AddMonoidHom.nsmul_apply,
    offsetHom_apply, offset, Int.coe_castAddHom]
  rw [e, zmodMul_intCast, zmodMul_intCast]
  ext <;> simp; ring

theorem hexMul_injective {m n v : ℕ} [NeZero m] (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m)
    (h1 : 2 * n ∣ 2 ^ (v + 1) * m) (h2 : n / 2 ∣ 2 ^ (v + 1) * m) :
    Function.Injective (hexMul m n (2 ^ (v + 1)) h1 h2) := by
  have hc : Nat.Coprime m 4 := by
    simpa using (Nat.coprime_two_right.2 hm).pow_right 2
  have i1 := zmodMul_injective h1 fun a ha => by
    rw [hn, ← mul_assoc, ← pow_succ'] at ha
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) ha
  have i2 := zmodMul_injective h2 fun b hb => by
    rw [half_eq hv hn, show 2 ^ (v + 1) * b = 2 ^ (v - 1) * (b * 4) by
      rw [show (4 : ℕ) = 2 ^ 2 by norm_num, mul_comm b, ← mul_assoc, ← pow_add]
      congr 2; omega] at hb
    exact hc.dvd_of_dvd_mul_right (Nat.dvd_of_mul_dvd_mul_left (by positivity) hb)
  refine (injective_iff_map_eq_zero _).2 fun ⟨a, b⟩ h => ?_
  simp only [hexMul, AddMonoidHom.prod_apply, AddMonoidHom.comp_apply, AddMonoidHom.add_apply,
    AddMonoidHom.smul_apply, AddMonoidHom.coe_fst, AddMonoidHom.coe_snd, Prod.mk_eq_zero] at h
  have hb : b = 0 := i2 (h.2.trans (map_zero _).symm)
  have ha : a + 2 • b = 0 := i1 (h.1.trans (map_zero _).symm)
  rw [hb, smul_zero, add_zero] at ha
  rw [ha, hb]
  rfl

/-- **The reduction on the atlas's hexagonal torus.** For n = 2^v m with m odd and v ≥ 1, a
hexagon rule's period P there satisfies P / gcd(P, 2^(v+1)) = P(m), its period on the square
torus of side m (in axial coordinates). So P = 2^a P(m) for some a ≤ v + 1. -/
theorem hexPeriod_div_gcd {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (D : Finset (ℤ × ℤ)) :
    hexPeriod n D / Nat.gcd (hexPeriod n D) (2 ^ (v + 1)) = period m D := by
  have h1 : 2 * n ∣ 2 ^ (v + 1) * m := by rw [hn, ← mul_assoc, ← pow_succ']
  have h2 : n / 2 ∣ 2 ^ (v + 1) * m := by
    rw [half_eq hv hn]
    exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 (by omega)) m
  refine (eq_div_gcd_of_dvd_iff (by positivity) fun p => ?_).symm
  rw [hexPeriod, period_eq_gperiod, gperiod, gperiod, ← isEventualPeriod_iff_dvd,
    ← isEventualPeriod_iff_dvd, ← isEventualPeriod_iterate_iff (k := 2 ^ (v + 1)) (by positivity),
    gstep_iterate_two_pow]
  exact (isEventualPeriod_restrict_iff (by positivity) (hexMul_offset h1 h2)
    (hexMul_injective hm hv hn h1 h2) D p).symm

end HexagonalTorus

end LatticeProofs
