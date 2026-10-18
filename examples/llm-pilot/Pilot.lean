/-
The LLM-central pilot's target (examples/llm-pilot/card.md). Replace `sorry` with a proof.
-/
import LatticeProofs

namespace LatticeProofs

/-- **The hexagon law's 2-part.** On the atlas's hexagonal torus of side n = 2^v m, with m odd,
m ≥ 5 and v ≥ 1, the parity rule H1 (B135/S135) has period exactly 2^(v+1) P(m), where P(m) is
its period on the square torus of side m in axial coordinates. -/
theorem hexPeriod_hexH1_exact {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm5 : 5 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    hexPeriod n hexH1Offsets = 2 ^ (v + 1) * period m hexH1Offsets := by
  sorry

end LatticeProofs
