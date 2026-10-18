import LatticeProofs.Pilot

-- The pinned statement. It must elaborate against the pilot's theorem exactly as written in
-- examples/llm-pilot/Pilot.lean, so the theorem cannot have been weakened.
example {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm5 : 5 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    LatticeProofs.hexPeriod n LatticeProofs.hexH1Offsets =
      2 ^ (v + 1) * LatticeProofs.period m LatticeProofs.hexH1Offsets :=
  LatticeProofs.hexPeriod_hexH1_exact hm hm5 hv hn

#print axioms LatticeProofs.hexPeriod_hexH1_exact
