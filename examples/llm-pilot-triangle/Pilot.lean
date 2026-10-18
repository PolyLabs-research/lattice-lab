/-
The LLM-central pilot's target (CARD.md). Replace each `sorry` with a proof.
-/
import LatticeProofs
import LatticeProofs.HexTwoPart

namespace LatticeProofs

/-- **The edge rule's 2-part.** On the atlas's triangular torus of side n = 2^v m, with m odd,
m ≥ 3 and v ≥ 1, the triangle parity rule B13/S13 (`triE`) has period exactly 2^(v+1) P(m),
where P(m) is the period of its square's plane rule on the square torus of side m. -/
theorem atlasTriPeriod_triE_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triE = 2 ^ (v + 1) * period m triSEOffsets := by
  sorry

/-- **The edge+vertex rule's 2-part.** The same for B1,3,...,11/S1,3,...,11 (`triEVOVS`). -/
theorem atlasTriPeriod_triEVOVS_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triEVOVS = 2 ^ (v + 1) * period m triSEVOVSOffsets := by
  sorry

end LatticeProofs
