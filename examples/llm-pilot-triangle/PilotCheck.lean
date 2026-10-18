import LatticeProofs.Pilot

-- The pinned statements. They must elaborate against the pilot's theorems exactly as written in
-- examples/llm-pilot-triangle/Pilot.lean, so the theorems cannot have been weakened.
example {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    LatticeProofs.atlasTriPeriod n LatticeProofs.triE =
      2 ^ (v + 1) * LatticeProofs.period m LatticeProofs.triSEOffsets :=
  LatticeProofs.atlasTriPeriod_triE_exact hm hm3 hv hn

example {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    LatticeProofs.atlasTriPeriod n LatticeProofs.triEVOVS =
      2 ^ (v + 1) * LatticeProofs.period m LatticeProofs.triSEVOVSOffsets :=
  LatticeProofs.atlasTriPeriod_triEVOVS_exact hm hm3 hv hn

#print axioms LatticeProofs.atlasTriPeriod_triE_exact
#print axioms LatticeProofs.atlasTriPeriod_triEVOVS_exact
