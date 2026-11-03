# Draft reply to guluchen/DistQLDPC#150

Draft only, for posting by hand. The data file to attach to the comment is
`docs/outreach/BB_756_16_passes.csv` (GitHub accepts .csv attachments). Don't link lattice-lab:
the repository is private.

---

Thank you, and thanks for checking it against your side so quickly.

**Credit:** [YOUR CHOICE: e.g. "tripptytrip", a name, or "PolyLabs Research"]

**Per-pass records for BB_756_16** are attached as `BB_756_16_passes.csv`, one row per (pass, part):

- `bound`: the pass tests "is there a Z-logical of weight ≤ bound?" (bounds 2 to 29, in order);
- `found`: whether that pass found one (false for every pass);
- `part`: which of the 16 parts of that pass (the search tree is split by a hash of the node's
  partial support at depth 6; each node is searched by exactly one part);
- `nodes`, `seconds`: nodes visited and wall time for that part.

Settings: kind Z, 16 parts, split depth 6, anchors (0, lm) (the translation argument: some
translate of a least-weight logical contains qubit 0 or qubit lm), with the packing cut on.
Totals: about 2.23 × 10^11 nodes over the 28 passes and about 7.0 hours of wall time on 4 cores.
The last pass (bound 29) alone was 1.41 × 10^11 nodes and 4.5 hours. No pass found a logical, so
there is none of weight ≤ 29, and with even weight that gives d ≥ 30.

Per pass, the total node count grows by a factor of about 2.6 to 2.75 per unit of bound from bound
17 on, which may be useful if you want to compare search-tree sizes with your engines.
