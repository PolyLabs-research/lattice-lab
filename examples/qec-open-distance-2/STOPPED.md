# The run stopped before its registered end (disclosed deviation)

- **What happened.** The registered run (ledger: registration, then run_started) did parts A1, A2
  and B, and part C's passes 2 to 29 on [[756,16]], with 25,143 s of its 108,000 s budget
  used. The pass at 29 finished without a find, so d >= 29, and d >= 30 because d is even for
  this code (A and B have odd weight). The pass at 30 then began, and the session's worker
  process was restarted, which ended the run. Its records stop after the pass at 29: no C_end
  record, no observations entry, no verdict in the ledger.
- **Why it was not resumed.** The pass at 30 cannot change the result: it can find only logicals
  lighter than 30, and the pass at 29 has shown there are none, d being even. The pass that
  could (31, which would give d >= 32, or d = 30 exactly with a witness) is estimated at about
  33 hours from the passes' growth (about 2.8 times per bound), more than the 23 hours left. The
  user chose not to resume it.
- **The decision rules, applied anyway.** `judged-after-stop.json` is study.py's `decide`
  applied to every record of records.jsonl after the stop: verdict "hold", with A1, A2, B,
  C1, C2 and H each "pass" and no problems. It is not a ledger entry: the ledger, as registered
  and as `lattice-lab verify` checks it, ends at run_started, and its own verdict is missing.
  `resume` would add one, after running the pass at 30 from its start.
