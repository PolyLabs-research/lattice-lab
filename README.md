# lattice-lab

A law-discovery loop over two existing projects. It asks "how does quantity y depend on setting
x" for a cellular-automaton rule, and answers with a named law, its constants with error bars,
and a verdict from experiments the fit never saw. Each prediction is recorded before the run
that tests it, in an append-only, hash-chained ledger.

- [LatticeLife](https://github.com/PolyLabs-research/gameoflife_advanced) runs the experiments
  and says what their numbers mean, including when a number is only a bound.
- [Kepler](https://github.com/PolyLabs-research/kepler) fits, ranks and predicts closed-form laws
  with error bars.
- lattice-lab owns what belongs to neither: the questions, the candidate laws, choosing the next
  experiment, pre-registered predictions, verdicts, and the record of every result.

Neither library imports lattice-lab or the other. See [docs/design.md](docs/design.md) for the
architecture, the loop step by step, and the milestones.

The loop began with settling times. Most of the work since is on linear rules, whose periods can
be computed exactly and proved: period laws for the parity rules, an atlas of rules built from
neighbour shells, the mechanisms behind it proved in Lean, and seven pilots in which a fresh LLM
agent, given a problem card, proves a law or finds and proves a mechanism, with Lean as the
judge of the proof. Its latest results explain why every nonzero eigenvalue of rule 4850 at
m = 37 is a ninth power, with a proof that three independent checkers found stands with repairs,
and classify the hexagon family it belongs to, confirmed by a registered test.

The ring all of this lives in is also the ring of bivariate bicycle quantum codes
([docs/next-direction.md](docs/next-direction.md)), and that is where the work is now: exact
distances for published codes ([docs/code-distances.md](docs/code-distances.md)), and a census of
every weight-6 code of that family up to 400 qubits ([docs/code-census.md](docs/code-census.md)).
The census's registered predictions failed where it mattered most: [[294,10,20]] scores
k d²/n = 13.6, above the published [[288,12,18]]'s 13.5, and [[384,12,24]] scores 18.0.

The public website, [polylabs-research.net](https://polylabs-research.net), is built from
`site/`; [site/README.md](site/README.md) says how to rebuild and deploy it. It covers every
PolyLabs Research programme, with lattice-lab's own section at
[/lattice](https://polylabs-research.net/lattice). Its
[census page](https://polylabs-research.net/census) summarises the census.

## Findings so far

**Picking this up?** [docs/STATUS.md](docs/STATUS.md) says where things stand: the three
repositories, how to resume, what is established, and what is open.

Every finding below was tested by predictions written to a ledger, committed and pushed before the
runs that test them. `uv run lattice-lab verify --lab examples/<study>` checks the order. Where
reasoning after the fact went beyond the tools, the write-up says so.

| Finding | Status | Write-up | Studies |
| --- | --- | --- | --- |
| Square parity rule B1357/S1357: period 2^v(n) (2^sord(m) - 1) | confirmed in advance at every n up to 200; the 2-part proved in Lean at every size (odd part > 1); the odd part settled by machine up to 999 except ten | [xor-periods.md](docs/xor-periods.md), [proof](docs/xor-periods-proof.md), [proofs.md](docs/proofs.md) | `xor-periods*` |
| Hexagon parity rule B135/S135: period 2 * 2^v(n) R(m), R = rule 90's period | the first law was refuted at 3 of 70 sizes; the corrected law was confirmed at 100 and **proved for every even n**; its 2-part also proved in Lean, by an LLM agent | [parity-lattices.md](docs/parity-lattices.md), [llm-pilot.md](docs/llm-pilot.md) | `parity-lattices*`, `llm-pilot` |
| Triangle parity rules: period 2 * 2^v(n) (2^sord(m) - 1) | confirmed at 154 sizes; the factor 2 * 2^v(n) is proved, and also in Lean, by an LLM agent; the odd part is checked by machine for odd parts up to 999 except ten | [parity-lattices.md](docs/parity-lattices.md), [llm-pilot.md](docs/llm-pilot.md) | `parity-lattices*`, `llm-pilot-triangle` |
| Kepler, given rule periods in its vocabulary, finds the hexagon law itself | confirmed in a registered replay (8 of 8 expectations) | [parity-lattices.md](docs/parity-lattices.md#kepler-with-a-wider-vocabulary) | `kepler-rediscovery` |
| Periods of 42 linear rules built from neighbour shells, 38 never studied | blind: all 34 rules that got a law kept a registered one at 1,930 new pairs, and again at 624 harder pairs up to n = 400 | [linear-atlas.md](docs/linear-atlas.md) | `linear-atlas`, `linear-atlas-2` |
| A rule that factors into 1D passes has a 1D period; any other reaches the full bound | registered on 116 new rules and **refuted** (7 of 113 predictions failed). Three failed rules were cubes or a dilation, mechanisms then predicted exactly; of the other four failures, two are explained (eigenvalues in F(8) at n = 13), and the one at n = 37 was explained later by the fourth pilot | [linear-atlas.md](docs/linear-atlas.md#round-2-the-pattern-registered) | `linear-atlas-2` |
| The refined statement: the full bound unless splitting, an odd power or a dilation confines the eigenvalues | registered on 344 new rules and **refuted**: 43 of 11,358 predictions failed (0.4%). Every dilation and power held; a third mechanism, a twisted power, showed up and its expectation, written first, matched all 34 sizes; the rest are small-field coincidences, and one case at m = 37, since explained by the fourth pilot | [linear-atlas.md](docs/linear-atlas.md#round-3-the-refined-statement-registered) | `linear-atlas-3` |
| B2/S34 settling time on the hexagon grows like log L | found by the loop; replicated on tori up to 1024, where the power law is rejected | [settling-time.md](docs/settling-time.md) | `lab-b2s34`, `settling-time-replication` |
| Settling-time fluctuations are universal, with extreme-value (Gumbel) shape and ratio | eight random rules on four lattice types; a first apparent miss for B2/S34 was a low draw | [settling-time.md](docs/settling-time.md) | `settling-universality`, `settling-time-local` |
| Cumulative births under B1357/S1357 are always even | found in the data, then proved | [capabilities.md](docs/capabilities.md) | `capabilities` |
| Six rules have every eigenvalue a cube at m = 37 because a dilation by 6 acts there as half a Frobenius, combined with rule 90's own confinement | **answered by an LLM agent**, on a question the orchestrator could not answer, and **proved in Lean** for all six, unconditionally; the agent's general condition held at 633 claims, 180 of them at held-out sizes registered before it started, none false | [llm-pilot.md](docs/llm-pilot.md#pilot-4-the-cubes-at-m--37) | `llm-pilot-37` |
| Five of seventeen rules have every eigenvalue a cube at m = 25: two by cube certificates (f (t(x) t(y))^3 is invariant under x7, and 2^5 = 7 mod 25), three as twisted pairs C(x, y) C(x^3, y^3) | **found and proved in Lean by an LLM agent**; its condition held at 1,381 claims, 414 at held-out sizes, none false. Twelve remain unexplained, and the registered held-out census found 16 new confinements at m = 37 that no mechanism then known explained, the sixth pilot's question (next row) | [llm-pilot.md](docs/llm-pilot.md#pilot-5-the-cubes-at-m--25) | `llm-pilot-25` |
| Nine square-family rules are a unit times a cube, f = U g^3 with U a product of rule-90 or Psi_3 factors, so every eigenvalue is a cube at m = 37 (and three of them at 61) | **found and proved in Lean by an LLM agent**, which also showed the census's chance model undercounts at 37; the registered census at 17 new sizes found these nine at exactly the three sizes predicted, and nothing else unexplained | [llm-pilot.md](docs/llm-pilot.md#pilot-6-the-square-family-at-m--37) | `llm-pilot-37b` |
| For a prime p = 5 (mod 8) with 2 a primitive root, rule 90 is confined to the cubes at p exactly when eps^h lies in Z[sqrt p] (eps, h: the fundamental unit and class number of Q(sqrt p)); at p = i^2 + 1 the pyramid rule with rings at radii 2, 4, ..., i/2 - 1 is then confined too | **proposed by Claude Fable in a consultation**, with an argument that, filled in with Dirichlet's class number formula, is a proof; registered and confirmed at all 405 such primes from 302 to 20,000 and at the 4 pyramid primes below 10,000, none wrong | [consultations.md](docs/consultations.md) | `fable-units` |
| At m = 37, five symmetric rules have every nonzero eigenvalue a ninth power that none of the seven mechanisms then known explains: 4850 (radius 4) and 699738, 985232, 1431278, 1968276 (radius 5) | chance **refuted** by a registered census of 2,064,384 radius-5 rules (4 independent such rules against 0.0066 expected), from a test Claude Fable proposed in a consultation; each is confined at 37 and at no other odd m from 11 to 101. All five are explained since (next two rows) | [consultations.md](docs/consultations.md) | `rule-4850` |
| Four of them (699738, 985232, 1431278, 1968276) are line units times pilot 4's half-Frobenius cores, and the units' exact exponents add the third factor of 3 | **found by an LLM agent (Claude Fable)** in the seventh pilot, its condition sound at all 1,715 claims (533 at held-out sizes) and covering 35 of the 37 unexplained ninth-power rules of the registered radius-6 census, which the agent had computed itself; its Lean failed to build in round 1 and was fixed in a second round over the API (`Ninth37.lean`); 4850 itself was explained afterwards by the deep dive (next row) | [llm-pilot.md](docs/llm-pilot.md#pilot-7-the-ninth-powers-at-m--37) | `llm-pilot-37c` |
| Rule 4850 itself: (x + 1/x + y + 1/y)·4850 is two hexagons sharing a 120° rotation mod 37 (5² + 3·2² = 37), its eigenvalues off the diagonals are W⁴/(t t) with W a Kloosterman-type sum over μ6, and a Gauss-period norm formula puts every norm to F64 in F8* | **explained, with a proof**: three independent checkers found it stands with repairs, which they supplied, and the orchestrator rechecked the chain; not yet written as one document, and not in Lean. The hexagon family's classification at 37 (p a non-residue gives ninth powers, a residue cubes) passed a registered held-out test: 35 of 35 tested predictions correct; the six at the largest sizes were not tested | [deep dive report](examples/rule-4850/deep/REPORT.md) | `rule-4850/deep`, `hexagon-family` |
| A bivariate bicycle quantum code's logical qubits k are read off the torus's characters (common zeros of A and B, with 2-part multiplicities at even sizes) | **confirmed by a registered test**: agrees with linear algebra on 3,000 of 3,000 random codes and reproduces all 12 published k, IBM's gross code included | [next-direction.md](docs/next-direction.md) | `qec-bb` |
| The 12 published codes' distances, d = 18 for [[288,12,18]] included | **reproduced by a registered test**, blind to the published values, by an exhaustive search built here (the gross code in 0.2 s, [[288,12,18]] in 3 minutes); an integer program agrees on 11. Its registered method check **failed** once, through a SCIP fault; the fault was traced and fixed, and a second registered test on fresh codes found both instruments hold, while SCIP's unfixed defaults failed on 3 of its codes | [code-distances.md](docs/code-distances.md) | `qec-distance`, `qec-distance-2` |
| Every code of the published form on 116 tori with n ≤ 200 | **a census, stage 1 (exploratory)**: 3,330 classes with k > 0 on 35 tori, each with an exact distance; the gross code has the highest k d²/n; an exact criterion for which tori have codes (proved by hand, matches all 116); a registered stage 2 on 122 held-out tori confirmed the criterion, the k formulas, the d = 2 rule and a linear distance law (19 of 19 instances exact, up to [[300,8,20]]), and refuted the mod-3 base pattern on 6 x 18 | [code-census.md](docs/code-census.md) | `qec-census`, `qec-census-2`, `qec-census-2b` |
| The open distances of the published [[360,12,≤24]] and [[756,16,≤34]] | **registered**: [[360,12]] has d = 24 exactly, by a checked weight-24 logical and a split exhaustive search, an independent recomputation of a value Crocker and DistQLDPC had found. [[756,16]] has 30 ≤ d ≤ 34, with a packing cut that a Fable consultation proposed and a registered test checked on fresh codes first; that matches DistQLDPC's public lower bound with a second implementation of the same kind of search. The second run stopped before its registered end, disclosed in its `STOPPED.md` | [code-distances.md](docs/code-distances.md#the-open-distances-examplesqec-open-distance) | `qec-open-distance`, `qec-open-distance-2` |
| Every weight-6 code of the family up to 300 qubits: the 116 stage-1 tori, then the 122 held out | stage 3a, **exploratory**: 36,496 classes, every d exact, matching Lin and Pryadko's catalog at 43 of 44 comparable (n, k) pairs and never higher. Stage 3b/3c, **registered and refuted**: [[294,10,20]] has k d²/n = 13.61, above the published [[288,12,18]]'s 13.5, and the best d reaches 1.42 √n. A spot-check of 20 frontier codes with other tools (SAT with DRAT proofs, DistQLDPC's two engines, SCIP) agreed everywhere, and the registered stage 3d settled the 154 classes left open: all have d = 24, as the parity of d predicted | [code-census.md](docs/code-census.md#stage-3b3c-every-weight-6-code-on-the-held-out-tori-registered) | `qec-census-3`, `qec-census-3b`, `qec-census-3c`, `qec-census-3d` |
| Every weight-6 code from 302 to 400 qubits (110 tori), against laws refitted on stage 3 | **registered and refuted**: 633,390 classes, with exact distances from DistQLDPC's cluster engine, each with a checked witness. The fitted envelope fails on 3 x 51 ([[306,4,26]]), and the ceiling on k d²/n fails: [[384,12,24]] scores 18.0, above 17.0. Growth past stage 3's d/√n record and a new record score both held, on 10 and 29 tori. Stage 4d, still running, reruns the 53 classes that stage 4 left at its 4-hour limit; every one settled so far has d = 30, and [[396,4,30]] has the census's highest d/√n, 1.508 | [code-census.md](docs/code-census.md#stage-4-the-laws-refitted-and-tested-up-to-400-qubits-registered) | `qec-census-4`, `qec-census-4d` |
| An LLM agent, given only a problem card and the Lean library, finds a mechanism and proves it | three pilots, each on the first attempt: the hexagon and triangle laws' 2-parts, and VO + T13's law, which the agent had to find from data. **Accepted by Lean**, not by the agent's account, with pinned statements and standard axioms; the registered predictions held at 15 of 15, 40 of 40 and 20 of 20, and the third agent's own law at 20 of 20 sizes it never saw. The last two ran in their own containers, with their transcripts audited. The laws were within reach of known techniques and, for the third, of one division per data row. Pilots 4 to 7, on open questions, are in the rows above | [llm-pilot.md](docs/llm-pilot.md) | `llm-pilot*` |
| The atlas's mechanisms, formally | **proved in Lean** (mathlib, standard axioms only): the 18 identities behind them; the bridge, that a rule's period on an odd torus is the lcm of its nonzero eigenvalues' orders; the reduction from even sizes to odd parts on the square and the atlas's own triangular and hexagonal tori; round 2's cube and dilation at every size; round 3's twisted power on the atlas's own triangular torus; the XOR law's 2-part at every size; the hexagon and triangle laws' 2-parts and VO + T13's law (proved by LLM agents, the last also found by one); the confinements that pilots 4 to 7 found and proved, to the cubes at m = 25, 37 and 61 and to the ninth powers at 37; and the full bound, that the period divides 2^sord(m) - 1 | [proofs.md](docs/proofs.md) | `proofs/` |
| Zooming out a parity rule by 2^k, with the clock slowed by 2^k, gives the rule itself: a closure test (run then zoom out, against zoom out then run) counts no difference where the scales match, and a fair coin per supercell where they do not | **confirmed by a registered calibration** of the scale-up instrument: 296 of 296 cases held. No supercell differed in 10.1 million comparisons, at blocks from 2 to 128 on grids up to 768 x 768, on LatticeLife's own engine. The 36 controls at mismatched scales (a block of 3, a clock one generation out or at half speed, the wrong coarse rule) each fell inside their exact binomial interval: 820,478 mismatches in 1,640,448 trials. The exact cases are theorems of the Lean library (Frobenius and the restriction lemma); the controls' law is worked out by machine from the group ring and is not formalised | [scale-up-plan.md](docs/scale-up-plan.md) | `scale-up-linear` |
| What a world of several species does on small grids is what it does on grids up to sixteen times as wide: its means do not depend on the side, the spread between starts falls as one over the side, and a rare species survives exactly when the start has room for one of its blocks | **confirmed by a registered test**, all 124 predictions: 62 at sides 512 and 1024 and the same 62 at sides 2048 and 4096 (16.8 million cells), registered together before either part was run. Laws fitted at sides 32 to 256, for Conway's Life against HighLife and for a five-species soup under two tie-breaks, gave each side's mean live fraction, species balance and mixing (none further than 1.4 standard errors), their spreads over the starts (none further than 2.5), and the constants of the live fraction's law against time. The soup's rare species is left as 2 x 2 blocks that nothing can break, 44 blocks per million cells under the random draw on the small grids: that density gave its share of the large ones (166 ± 2 cells per million at side 4096 against 174 ± 14) and the scatter of independent blocks, and every species survived all 288 runs. Not registered: the large sides agree with each other on eight of nine means; for the ninth, one sample of sixteen starts ran high and sixteen fresh starts did not, which left a difference of 0.4% for the next row to settle | [scale-up-plan.md](docs/scale-up-plan.md) | `scale-up-sizes`, `scale-up-sizes-large` |
| Zoomed out by blocks, with the clock slowed by the block, a world of several species is a map of where things still move. Movement cannot start where nothing around it moved, and in Life against HighLife it spreads from moving neighbours and dies without them by a rule that is nearly the same at every time | **43 of 45 registered predictions held** on a torus twice as wide as the first look's, from fresh starts. Exact: no block moved out of stillness in 902 million still neighbourhoods (with the clock four blocks long, 8,700 did). Measured: knowing how many neighbours moved removes 38% of the surprise about a block of 4 and 10% about a block of 32, but under half a percent of the errors; a rule with neighbour counts learned in the first 256 generations has under 1% more surprise afterwards than one learned afterwards, where a rule that knows the block alone has 47% to 64% more; the rule learned on side 1024 serves on side 2048 to 0.02%; a still block with exactly one moving neighbour starts moving with a chance of 0.008 at every block from 4 to 64; and run on by itself the rule keeps the fine world's amount of movement for about eight coarse generations, then loses it. Failed: a band guessed for a block of 64 (0.084 against at most 0.08) and a claim that had nothing to test it on. The rule is not the same at every scale, so there is no rung-to-rung fixed point here | [scale-up-plan.md](docs/scale-up-plan.md) | `scale-up-closure` |
| A rule alone seldom organises itself over a growing distance, and most that seem to are one kind of ground taking the whole grid. But one rule in six sorts into growing territories when it meets a copy of itself, and which rules do goes with how few of its own kind a cell needs to be born | **a search (exploratory)**, nothing registered. Read by the correlation area (how much more a block's count scatters than independent cells would), a screen of 2,407 worlds on a 256 x 256 grid called 42 growing, about one rule set in fifty. Run again on a 1,024 grid from fresh starts, most of the strong one-species growers are takeovers, and three rules keep growing with their two kinds of ground level (Anneal, Day and Night, B012457/S14). Then every one of 1,196 random rules was set against a copy of itself, as two species with the one rule: 202 hold territories, 112 of them under both tie-breaks and 78 from either start under either, and 191 of the 202 are plain patches when alone, while Anneal dies against its copy. Territories turn up in 5%, 15%, 57%, 50% and 1% of the rules whose births need 0, 1, 2, 3 and 4 or more neighbours of their own kind, a cut read off the first 458 rules that held on the other 738; among those that need two or three, 44 of the 47 whose cells cannot last on one or two, and that live at all, hold them (read off all the rules, untested). In the worlds that keep growing, a zoom-out by two goes with waiting four to eight times as long, not twice as in the row above. The soups as drawn hold no such world: nineteen in twenty are patches, and those that grow are mostly one species left | [scale-up-plan.md](docs/scale-up-plan.md#step-4b-the-search-for-a-world-that-organises-itself-exploratory-2026-11-24) | `scale-up-search` |
| Which rules hold territories against a copy of themselves goes with how few of its own kind a cell needs: to be born, and to last | **confirmed by a registered test**, all 10 predictions, on 600 rules of a random draw that no run had used, from a start no run had used: each rule as two species with the one rule, from a full start and a half-full one, under the random draw and the standoff. 17.7% of the rules hold territories. By the fewest of its own kind a cell needs to be born: 4.8% of the rules that need none (14 of 292), 13.5% of those that need one, 61.5% of those that need two or three (72 of 117), and none of the 43 that need four or more. Among 359 rules that need two or three, 82% hold territories where a cell cannot survive on one or two of its own kind, against 53% where it can; and of the 85 such rules that do not die out, 84 hold them. Rules that hold under one tie-break only do so under the standoff 35 times in 41, and of the 21 rules that organise alone one holds territories. The bounds were set between what the exploratory screen gave and what would mean nothing; every number came out within 0.08 of the screen's. The counts are tested; the reasons for them are a reading | [scale-up-plan.md](docs/scale-up-plan.md#step-4c-which-rules-hold-territories-registered-and-run-2026-11-24-all-ten-held) | `scale-up-territories` |
| Zoomed out by blocks, a world of territories has a coarse description that works: who leads each block, with a table of what blocks with as many rival neighbours did next, runs the world on without its cells and says where most of its territories will be | **a first look (exploratory)**, nothing registered. Two rules against copies of themselves, B245678/S3678 (two still grounds, only the walls move) and B23467/S4568 (two busy grounds), on a 1,024 x 1,024 grid for 4,096 generations from eight starts each, read through blocks of 4 to 32 with the clock at the block and at its square. A block changes hands by being surrounded: with a chance under 0.003 with two of its eight neighbours under the rival, 0.15 to 0.17 with four and 0.44 to 0.47 with six, at blocks of 4. Run on by itself from generation 1,024, drawing from that table with no cells under it, the rule's world 3,072 generations later has the real world's leader in all but 7% to 12% of the blocks at blocks of 4 to 16, where a fifth of the blocks have changed leader, and within about 5% of its walls at blocks of 16 and 32. The rule learned in one world serves in the other to within half a percent of its surprise from blocks of 8, though the two rules share nothing cell by cell. It is the same early and late to 0.24% at blocks of 4 and 3% at 16. It is not the same from rung to rung: the rule from blocks half the size is out by 7% to 16% with the clock at the block and by 2% to 9% with the clock at its square, less at each rung, so the ladder has no fixed point yet and a clock to look for one on | [scale-up-plan.md](docs/scale-up-plan.md#step-4d-a-world-of-territories-zoomed-out-first-look-exploratory-2026-11-25) | `scale-up-closure-territories` |
| A coarse rule stands in for a world of territories, and for worlds whose grounds fill it is one rule with a pace | **73 of 89 registered predictions held** (8 failed, 8 not tested), on six worlds from starts no run had used: the first look's two, three that had never been zoomed out, and a control. All 58 claims about the first look's two worlds held, at its figures: the first look's tables, tried unchanged on fresh starts, are within 0.03% of tables learned from them; run on by itself for 3,072 generations a world's own table keeps its walls (0.97 and 0.99 of them at blocks of 16) and is amiss in 0.36 to 0.54 of the blocks that change leader; each world's table serves in the other to 0.5% from blocks of 8, and the still world's runs the busy world on nearly as well as its own; from one block size to the next the table changes on both clocks, less on the square clock, and at blocks of 16 the table from blocks of 8 is still 4% short. Of the three worlds never zoomed out: B24678/S34678 follows the still world's table as it is (0.5% to 0.6% more surprise, and that table runs it on); B3568/S124678 follows it at half the pace (0.5% at half the tick, 1.8% to 2.5% as it is, which failed), and its walls read with no coarse rule say the same half (exploratory); B2/S0, sparse and busy, does not follow it at any pace (54% to 60% more), has no clean territories at any block, and coarsens as the 0.27th power of time where the others have about a half. In the control, B2578/S135678, whose territories set, the table is three times as surprised as the world's own and wrecks it when run on. One failure is a bound missed by a hair (0.70003 against 0.70). The ledger verifies, and six run-ons and five fine runs recomputed on another machine match byte for byte | [scale-up-plan.md](docs/scale-up-plan.md#step-4e-the-zoom-out-of-territories-registered-registered-and-run-2026-11-26-73-of-89-held) | `scale-up-closure-territories` |
| The class of worlds that one coarse rule runs is the full ones, not the ones that share its clock | **54 of 128 registered predictions held** (55 failed, 19 not tested): the claim the test was built for is refuted. 38 worlds never zoomed out, chosen by rule from an earlier registered run (every rule that grew territories against its copy and filled the grid, and a share of those that grew them without filling it), each on a 1,024 grid to generation 4,096 from four fresh starts. Nearly all coarsen alike: 29 thin their walls as the 0.40th to 0.54th power of time, 5 have set and 4 are slower. But the table read off one still world serves only 10 of the 29 within 1% and 4 more within 2%, and they are the worlds with more than half their grid live; the other 15 it misses by 4% to 38%. The registered claim that a world's clock says whether the table serves it failed for 20 worlds, and so did the claim that the pace at which the table serves is the pace the walls give (it is loosely so in the worlds served and means nothing outside them). Weighted by how many rules each kind stands for, the class is 23% of the rules of a random draw that grow territories. One thing went the other way: run on by itself at the pace a world's walls give, the still world's table keeps 19 of the 29 worlds, including 6 it does not serve, and beats the world's own table in 23 | [scale-up-plan.md](docs/scale-up-plan.md#step-4f-how-wide-is-the-class-registered-and-run-2026-11-26-54-of-128-held) | `scale-up-class` |
| One rung further up, the coarse rule changes less again, and the rule of each rung runs the rung above; it has not stopped changing | **confirmed by a registered test**, all 22 predictions. Two worlds of territories on a 2,048 grid to generation 16,384 from eight fresh starts each, read through blocks of 4, 8, 16 and 32, each at the age that matches it (a block twice the size is read four times later). The fourth rung looks like the three below it: as many walls when its age starts, within 7% and 3%. The table learned at one rung has 8.6%, 2.8% and 1.4% more surprise at the next than the table learned there in the still world, and 5.6%, 3.0% and 1.6% in the busy one. Used unchanged as the table of the rung above and run on by itself, with no cells, it ends amiss in 6% to 15% more blocks than that rung's own table, which at blocks of 32 is amiss in 0.51 and 0.39 of the blocks that changed leader over 12,288 generations. What the same records show beside the claims (exploratory): the table moves the same way at every rung, so the gaps compound (from two rungs down 8% and 9%, twice the sum of the steps between), and a gap that halves is a step that shortens by three tenths; what still moves is how often a block on a wall, with three or four of its eight neighbours under the rival, changes hands. By that pattern a table that has stopped changing is three or more rungs further up, and each rung costs sixteen times the last | [scale-up-plan.md](docs/scale-up-plan.md#step-4g-one-more-rung-registered-and-run-2026-11-26-all-22-held) | `scale-up-rung` |
| Zoomed out, a world with no memory has one: how long a block has had its leader says what it does next, and a coarse rule that keeps that in view runs the world on better and is nearly the same rule from one rung to the next | **a first look, exploratory**: nothing is registered, and no world was run. The block leaders of the sixteen runs above read again, with more of a block in view: who led it one tick before, and for how many ticks running it has had its leader. A block of 16 with four of its neighbours under the rival has another leader one tick on with a chance of 0.31 if it changed hands a tick ago, and 0.04 if it has held sixteen ticks; the table as it was gives every such block 0.076. What the symbol hides is where the wall inside the block is, and the block's past says. Three things follow. Where a block is all but surrounded its chance is the same at every rung once its past is in view: what looked like the table changing there was the mix of blocks that had just changed hands and blocks that had not. Run on by itself, with no cells, the table that remembers ends with the wrong leader in a tenth to a quarter fewer blocks at blocks of 8 and 16, no longer loses walls as the plain table does, and wavers as the world does; and the table of one rung then runs the rung above within 3% of that rung's own at blocks of 16 and 32, where the plain one is 10% to 15% worse. One tick ahead the table still changes along the walls, by about half for each doubling of the block, whatever a block's past | [scale-up-plan.md](docs/scale-up-plan.md#step-4h-a-rule-that-remembers-first-look-exploratory-2026-11-27) | `scale-up-memory` |
| A coarse rule that remembers how long a block has had its leader runs a world of territories on better, and is nearly the same rule from one rung to the next | **confirmed by a registered test**, all 74 predictions, on sixteen fresh starts of each of two worlds (a 1,024 grid to generation 4,096, blocks of 4, 8 and 16, each at the age that matches it), with the first look's own tables written down beforehand and tried unchanged. A block with four rival neighbours that changed hands a tick ago changes again eight times as often as one that has held sixteen ticks. Where a block is all but surrounded its chance is the same at blocks of 8 and 16 once its past is in view (0.95 and 1.00 times), while the plain table's falls to 0.85 and 0.88, and that fall is the mix of young and old leads; along the walls the chance still falls, to a third at three rival neighbours. Run on by itself, the table that remembers ends with the wrong leader in 0.73 to 0.88 of the plain table's blocks and keeps the walls the plain one loses a tenth of. Learned at blocks of 8 and used unchanged at blocks of 16, it ends within 5% of the table learned there (the plain one: 14% to 15% worse). Blocks of 32 are beyond this grid, so what the first look saw there is still a look | [scale-up-plan.md](docs/scale-up-plan.md#step-4i-the-rule-that-remembers-registered-registered-and-run-2026-11-27-all-74-held) | `scale-up-memory` |
| The large grids agree with each other: nothing in Life against HighLife creeps with the size of the grid between sides 1024 and 4096 | **confirmed by a registered test**, all 9 predictions, on 512 fresh starts: each pair of sides agrees within 0.0002 for the live fraction (the 0.4% gap the row above left), 0.0028 for the species balance and 0.00053 for the mixing, by the 99% interval of the difference. The three live fractions are 0.048302 ± 0.000028, 0.048330 ± 0.000026 and 0.048267 ± 0.000023, and the largest difference is 0.00006 ± 0.00003. Not registered: a line through the three sides changes by 0.04% ± 0.04% for each doubling of the side; the one registered sample that ran high stays unexplained, 4.2 standard errors above 112 fresh starts at its own side | [scale-up-plan.md](docs/scale-up-plan.md) | `scale-up-gap` |
| The birth tie-break (who is born in a cell two species could both be born into) changes a world of several species only where contests are common | **confirmed by a registered test**, all 15 predictions: under a standoff (the contested cell stays empty) in place of the random draw, Conway's Life against itself and against HighLife show no difference beyond a tenth in live fraction at three times, nor in species balance or mixing (128 starts each; contests are 0.4% of births); two identical species end level under both; of 24 five-species soups with rules drawn at random, the five where contests are under 1% of births are level to within 0.007 of the grid, and in all nine where they are a fifth or more the standoff lowers the live fraction, by 0.04 to 0.46. Not registered: over the 24 soups the drop follows the contested share (rank correlation -0.82) | [scale-up-plan.md](docs/scale-up-plan.md) | `scale-up-tie-break`, `scale-up-compete` |

## Install

```bash
uv sync                      # LatticeLife and Kepler at the commits pinned in pyproject.toml
uv run pytest
```

The code-distance and census studies use SCIP, from the optional `qec` group:
`uv sync --group qec` installs it, and without it their SCIP tests fail.

Python 3.12 or 3.13 (LatticeLife's bound). To work against local checkouts of the libraries,
run `uv pip install -e ../gameoflife_advanced -e ../kepler` after `uv sync`, then use
`uv run --no-sync`; the ledger records their commits and whether they had uncommitted changes.

## Use

```bash
uv run lattice-lab ask questions/settling-time-hexagon-B2S34.toml --lab lab --workers 8
uv run lattice-lab verify --lab lab --rerun 5     # chain, order, and records rerun byte for byte
uv run lattice-lab report --lab lab               # rebuild the latest report from the ledger
uv run lattice-lab selfcheck --out docs/selfcheck.md
uv run lattice-lab laws
```

To put a question to other models (Claude Fable and ChatGPT) and record their answers verbatim,
see [docs/consultations.md](docs/consultations.md#running-a-consultation):

```bash
uv sync --group consult            # the two API clients
uv run lattice-lab consult ask 2026-10-21-next-steps --preset direction --dry-run
uv run lattice-lab consult ask 2026-10-21-next-steps --preset direction
uv run lattice-lab consult review 2026-10-21-next-steps
```

`ask` prints a JSON summary and writes `lab/reports/<id>-<n>.md`. The verdict is one of:

| Verdict | Meaning |
| --- | --- |
| found | One law passed its held-out test, no rival as simple is within 6 BIC points on all the data, and the verdict survives dropping the smallest sizes and each size in turn |
| fragile | A law passed, but the verdict changes when some fitted size is left out |
| inconclusive | Laws that passed are too close to call, or nothing could be tested (seeds unsettled at every cap, no budget, no sizes left) |
| none fits | Every candidate's held-out predictions were rejected, or none fits the data at all |

### A question

```toml
id = "settling-time-hexagon-B2S34"
rule = "B2/S34"
shape = "hexagon"            # square, hexagon, triangle (+ triangle_mode)
density = 0.5
seeds = 20
fit_sizes = [8, 10, 12, 16, 20, 24, 32]
heldout_pool = [40, 48, 64, 96, 128]   # "24x26" for a rectangular torus
```

Defaults (all overridable): `heldout_per_round = 3`, `max_rounds = 2`, `cap = 2000` and
`max_cap = 64000` generations, `laws` = constant, logarithmic, linear, power, exponential,
exponential in the area, `space = "auto"` (log when every value is positive), `alpha = 0.01`,
`decisive_bic = 6`, `budget_cell_steps = 2e11`. Version 1 asks one quantity, `settling_time`:
the median generation at which a soup's final cycle begins, against the torus size (for a
rectangle, the square root of its cells).

### The lab directory

```
lab/
  ledger.jsonl          every question, run, observation, plan, prediction and verdict
  records/<id>-<n>.jsonl  LatticeLife's raw records for that question
  reports/<id>-<n>.md   the report, rebuilt from the ledger by `report`
```

Keep a lab directory as data, apart from this code. Reports state how many questions the
ledger holds, since scanning many rules turns up chance fits.

## Example: B2/S34 on the hexagon lattice

`examples/lab-b2s34/` is a complete lab from `uv run lattice-lab ask
questions/settling-time-hexagon-B2S34.toml` on the pinned commits: the ledger, LatticeLife's 200
records and [the report](examples/lab-b2s34/reports/settling-time-hexagon-B2S34-0.md).
`uv run lattice-lab verify --lab examples/lab-b2s34` checks it.

Its answer is not the prototype's. Fitted on L = 8 to 32 and tested at 64, 96 and 128, the
verdict is **found: logarithmic**, T(L) = 37.6 log L − 36.3 (± 2.7 and ± 8.3, all sizes). A
power law also passed its held-out test (p = 0.09), but on all ten sizes it is 8.4 BIC points
worse. The verdict holds with the smallest sizes dropped and with each size left out. The
prototype reported T ≈ 27·L^0.35. Before the run, the plan said these sizes and seeds could
not be expected to separate the two (an expected BIC difference of 3.9 against a margin of 6;
about 1.5× the seeds would), so the margin seen is more than the design promised: treat this
as one answer to replicate with more seeds or larger tori, not a settled fact. It has since been
replicated, in a registered study on tori up to 1024 with 100 seeds each, where the power law was
rejected ([docs/settling-time.md](docs/settling-time.md)).

## Beyond settling time: what else Kepler finds in LatticeLife data

[docs/capabilities.md](docs/capabilities.md) runs each of Kepler's newer tools on real
LatticeLife simulations (`uv run python examples/capabilities/run.py`):

- survival windows and how their edges move with torus size (a binomial likelihood, one fit over
  density and size);
- times that are only bounds (a censored likelihood);
- whether a law depends on the starting density (shared constants);
- relaxation and damage over time, with seed-to-seed error bars;
- distributions of object sizes;
- exact formulas for periods (the studies below);
- conserved quantities (a parity of births, found from data and then proved);
- whether a fitted constant is a known number.

The loop itself still asks only about settling time; these studies are ready to become question
types.

## Periods of the parity rules

The parity rule sets each cell to the parity of its live neighbours. It is linear over GF(2), so
its period on an n x n torus can be both measured and proved. Write n = 2^v(n) m with m odd, and
sord(m) for the least j with 2^j = +-1 modulo m. In each study Kepler found the law from
simulations, the law's predictions were registered in a ledger before the sizes were computed,
and the proofs came afterwards.

| Rule | Law | Tested in advance | Proved |
| --- | --- | --- | --- |
| B1357/S1357, square ([write-up](docs/xor-periods.md)) | 2^v(n) (2^sord(m) - 1) | confirmed at 45 sizes by simulation and at all 198 from 3 to 200 exactly; the rival (rule 90's period) refuted at all ten sizes where it differs | reduced to odd sizes; settled by machine for every odd part up to 999 except ten ([proof](docs/xor-periods-proof.md)) |
| B135/S135, hexagon ([write-up](docs/parity-lattices.md)) | first 2 * 2^v(n) (2^sord(m) - 1); corrected to 2 * 2^v(n) R(m), R(m) = rule 90's period on m cells | first law refuted at 3 of 70 sizes (74, 148, 190, by a factor of 3); corrected law confirmed at all 100 sizes from 202 to 400 | **the whole law, for every even n**; the key step is that two hexagon generations are three passes of rule 90. The 2-part is also in Lean, proved by an LLM agent ([pilot](docs/llm-pilot.md)) |
| B13/S13 and B1,3,...,11/S1,3,...,11, triangle ([write-up](docs/parity-lattices.md)) | 2 * 2^v(n) (2^sord(m) - 1) | confirmed at all 154 sizes registered | the factor 2 * 2^v(n) for every even n, also in Lean, proved by an LLM agent ([pilot](docs/llm-pilot.md)); the odd part checked by machine for every odd part up to 999 except ten |

What is new, as far as a web search went:

- **Known before.** The square rule's odd sizes up to 23 were published by McLaughlin, and the
  structure of these laws is Martin, Odlyzko and Wolfram's for rule 90 (1984). Vadali and Turner
  (2025) proved the four-neighbour square rule has rule 90's cycle lengths.
- **Not found in the literature:** the square eight-neighbour rule escapes rule 90's shortfalls,
  the hexagonal rule shares them exactly, and the triangular rules escape them. The identity
  behind the hexagon result is elementary, and a specialist may know it.
- **Who did what.** Kepler found each law from data. The registered tests showed where the
  hexagon's was wrong, and the corrected law and the proofs were reasoning added afterwards.
  Since then Kepler's vocabulary includes the periods of the 1D linear rules. A registered replay
  (`examples/kepler-rediscovery`) shows it now lists the corrected law on the discovery data,
  names n = 74 as the size that decides, and on data up to 200 keeps the right law on every
  lattice, predicting all 98 hexagon periods at 202 to 400. That shows capability in hindsight;
  it is not a fresh discovery.

**A blind atlas** ([write-up](docs/linear-atlas.md), `examples/linear-atlas`). Kepler then
proposed laws for all 42 rules built from symmetric neighbour shells on the three lattices, 38
of them unstudied. The laws came from tori up to 60. Every law, tied rivals included, was
registered at each new size before any was computed. On exact checks at 1,930 (rule, size) pairs
up to n = 160:
- **all 34 rules that got a law kept one at every size**;
- no rule had every law refuted;
- Kepler's first choice held for 19 rules, and a registered rival for the other 15;
- 8 rules got no law, and each is a quadratic in its lattice's nearest-neighbour rule.

Afterwards, not registered: the laws split into two families, and the rules' polynomials sort
them into those families without exception among the 32.
- **Rules that factor into passes of 1D rules along lattice directions** have that rule's period
  and inherit its shortfalls.
- **Rules that do not factor** reach the full bound.

This includes rule-150 analogues of Vadali and Turner's theorem and of the hexagon theorem.

**Round 2 registered the pattern** (`examples/linear-atlas-2`) and made 5,048 exact checks.
- **The atlas laws:** all 34 held at all 624 new sizes, which were chosen where the two families
  part, up to n = 400.
- **New rules:** for 112 square rules nobody had computed, plus the four without a law, the
  pattern predicted each period at odd n from the factorisation alone. **106 of the 113
  predictions held, and 7 failed, so the pattern as registered is refuted.**
- **Three of the failed rules** are confined without splitting: two are perfect cubes and one is a
  rule in x^3, y^3. After the first failure of each kind, the sizes and periods where they must
  fail were committed before those sizes were computed. All 55 came out as written.
- **The other four** fail at one small size each (n = 13 or 37). Two are explained since: at
  n = 13 they are sums of one 1D polynomial along each axis, and it sends every rule-90 value
  into the subfield F(8) (`examples/linear-atlas-2/subfield.py`). The n = 37 one, with every
  eigenvalue a cube, was explained later by the fourth LLM pilot (below).

**Round 3** (`examples/linear-atlas-3`, registered in `223e56f`) wrote the refined statement as a
fixed procedure, `atlas3.predict`: dilation, odd prime power, a complete 1D split, and otherwise
the full bound. It predicts the odd part of each period from the polynomial alone. It was
registered for 344 new rules on all three lattices, with nine new shells, at odd parts from 9 to
141, small sizes included: 11,358 predictions. Before registration it reproduced 7,746 of the
7,750 earlier data points. The run was stopped at a two-hour limit and finished by the harness's
new `resume` step; an independent eigenvalue computation agrees with all 11,662 records.
- **43 predictions failed (0.4%)**, so both registered hypotheses are refuted: strict, and
  "failures only at m <= 61, at most 1%".
- **Every dilation (1,017) and perfect-power (272) prediction held**, and 164 of 165 splits.
- **Seven failures are one rule, triangle VO+T13.** Its polynomial is the edge rule's times its
  own dilation by 3, which is a disguised power wherever 3 = +-2^k modulo m. An expectation built
  on that was written during the run, before 29 of its 34 sizes, and matched all 34.
- **The other 36 are at m = 13, 15, 21, 25 and 37.** There the rules have only 3 to 9 distinct
  eigenvalues, all inside a subfield or the cube subgroup; that is chance in small fields. The
  m = 37 case is not chance, and neither is round 2's one at 37. A census found six such rules
  at 37, and the fourth LLM pilot's agent explained and proved all six
  ([llm-pilot.md](docs/llm-pilot.md#pilot-4-the-cubes-at-m--37)).

Each study is a directory under `examples/`. The ones with ledgers check with
`uv run lattice-lab verify --lab <dir>`.

| Directory | What it holds |
| --- | --- |
| `xor-periods` | square rule, round 1: simulations of 45 registered sizes |
| `xor-periods-algebra` | square rule, round 2: exact periods for n = 3..200 |
| `xor-periods-proof` | square rule: the odd-size machine check up to 999 |
| `parity-lattices` | hexagon and triangles: discovery, the exact engine, round 1 (210 predictions) |
| `parity-lattices-hexagon` | round 2: the corrected hexagon law at 100 sizes, the triangles at 7 |
| `parity-lattices-proof` | triangles: the odd-part machine check up to 999, with the hexagon as control |
| `settling-time-replication` | B2/S34 settling times on hexagon tori up to 1024 (registered) |
| `settling-universality` | eight random rules on four lattice types: settling-time laws and their fluctuations (registered) |
| `settling-time-local` | B2/S34's local settling times on 256 and 1024 tori: round 2 (registered) |
| `kepler-rediscovery` | Kepler's search, with 1D linear-rule periods, replayed on the period data (registered) |
| `linear-atlas` | 42 shell-built linear rules: exact engine, discovery, Kepler's laws judged at 1,930 new pairs (registered), factorisation analysis |
| `linear-atlas-2` | the factorisation pattern registered: the 34 laws at 624 decisive pairs, and 116 square rules predicted from their factorisation (registered); the cubes and dilation found afterwards |
| `linear-atlas-3` | the refined statement registered: 11,358 predictions of odd parts for 344 new rules on all three lattices (registered; resumed once); the eigenvalue cross-check and the failure analysis |
| `llm-pilot` | the LLM-central pilot: problem card, tools, sandbox, judge, the agent's submission, and the hexagon law at 15 new sizes (registered) |
| `llm-pilot-triangle` | the second pilot, on the triangle laws' 2-part, run in a separate container: card, setup, judge, transcript audit, the agent's submission and transcript, and both triangle laws at 20 new sizes (registered) |
| `llm-pilot-vot13` | the third pilot: the agent finds VO + T13's law from data and proves it; card, data, judge (with the law evaluated at unseen sizes), audit, the agent's submission and transcript, and the law at 20 new sizes (registered) |
| `llm-pilot-37` | the fourth pilot, on an open question: why six rules have only cube eigenvalues at m = 37. The census of all 1,274 rules, card, data, judge (the agent's condition run on every rule at 94 sizes and checked by eigenvalues), the held-out census (registered), audit, the agent's submission and transcript |
| `llm-pilot-25` | the fifth pilot, on the cubes at m = 25: the square family, card, data, tools, judge (the agent's condition on the atlas at 94 sizes and on the family at 16), the family's census at 14 held-out sizes (registered; chance refuted at 6), audit, the agent's submission and transcript |
| `llm-pilot-37b` | the sixth pilot, on the 16 square-family rules confined at m = 37 that pilot 5's census found: the pre-check, card, data, both earlier conditions as tools, judge, the family's census at 17 held-out sizes (registered), audit, the agent's submission and transcript |
| `llm-pilot-37c` | the seventh pilot, on Claude Fable, on the five ninth-power rules at m = 37: card, data, all three earlier conditions and a fast census as tools, judge, the registered radius-6 census, audit, the agent's submission and transcript, and the second round over the API that fixed its Lean (`round2.py`) |
| `hexagon-family` | the registered held-out test of the hexagon-family classification from the rule-4850 deep dive: 41 predicted period odd parts at 37, 13 and other sizes (the classification holds: 35 of 35 tested, 6 untested) |
| `qec-bb` | the first step toward quantum codes ([next-direction.md](docs/next-direction.md)): a bivariate bicycle code's logical qubits from the torus's characters, against linear algebra and twelve published codes (registered; both predictions held) |
| `qec-distance` | the published codes' distances by two exact instruments, an integer program (SCIP) and an exhaustive search in C, with method checks on random, toric and trinomial codes (registered; all 12 reproduced, one method check failed; [write-up](docs/code-distances.md)); `check-independent/`, the independent checker's development records |
| `qec-census` | stage 1 of a census of codes of the published form on every torus with n ≤ 200 outside a committed hold-out: fast k, equivalence classes, exact distances, cross-checks ([write-up](docs/code-census.md); exploratory; stage 2 tested it, in `qec-census-2`) |
| `qec-distance-2` | the re-test of both instruments as fixed (SCIP's XOR presolving and rapid learning off; the search with iterative deepening), on fresh codes, the known fault cases, the published codes and a power test with SCIP's defaults as control (registered; the instruments hold) |
| `qec-census-2` | census stage 2: stage 1's findings registered and tested on the 122 held-out tori (registered; all but the mod-3 base pattern hold, and the verdict stays "incomplete" after a capacity fault in `census.c`) |
| `qec-census-2b` | stage 2's registered continuation: the jobs its run could not do, with stage 2's predictions copied verbatim |
| `qec-open-distance` | the open distances of the published [[360,12,≤24]] and [[756,16,≤34]]: a window search for checked logicals and an exhaustive search split across cores (registered; d = 24 for [[360,12]], 24 ≤ d ≤ 34 for [[756,16]]) |
| `qec-open-distance-2` | a packing cut for the search, tested on fresh codes and known distances, then [[756,16]] to d ≥ 30 (registered; stopped before its registered end, disclosed in `STOPPED.md`) |
| `qec-census-3` | census stage 3a: every weight-6 code on the 116 stage-1 tori, 36,496 classes with exact distances (exploratory) |
| `qec-census-3b` | stage 3b: stage 3a's patterns registered on the 122 held-out tori (refuted by [[294,10,20]]); `spotcheck/`, the independent check of 20 frontier codes with other tools |
| `qec-census-3c` | stage 3b's registered continuation on the tori its run could not reach, with its predictions verbatim; the last 25 tori ran on a RunPod CPU pod (`runpod/`) |
| `qec-census-3d` | the 154 classes stage 3b/3c left unfinished, settled with DistQLDPC's cluster engine (registered; all d = 24) |
| `qec-census-4` | census stage 4: the laws refitted and tested on 110 tori from 302 to 400 qubits (registered; the envelope and the ceiling fail); `dashboards/` and `explorer/`, the review dashboards' data layer and the census explorer; `check-310/`, the second method on [[310,10,22]] |
| `qec-census-4b` | probabilistic distances by information-set decoding: the instrument and its calibration (prepared; not registered or run) |
| `qec-census-4d` | the 53 classes stage 4 left at its 4-hour limit, rerun with a 14-day limit (registered; running) |
| `qec-noise` | the plan for circuit-noise simulation of the census's best codes (scoping, not registered) |
| `census-remainder` | the 45 census entries pilot 4 left, sorted: forced subfields, a chance model and its calibration (all 32,768 symmetric square rules within distance 4 at m = 21 and 25), hidden symmetries mod m; pilot 5 later explained 19 of them, and pilot 7's condition covers 27, among them 10 that no earlier condition covered ([write-up](docs/census-remainder.md)) |
| `fable-units` | a registered test of Claude Fable's unit criterion and pyramid rules from a consultation: predictions from the fundamental unit and class number alone, decided by direct computation in GF(2)[x]/Phi_p ([write-up](docs/consultations.md)) |
| `consult-budget` | what a consultation's effort is worth: two answered questions put to Fable at three settings, every claim checked by machine, rubrics graded blind; cost per verified answer, and two findings ([write-up](docs/consultations.md)) |
| `rule-4850` | rule 4850's ninth powers at m = 37: the pre-check, the consultation's question, a fast census by discrete logs, and the registered radius-5 census that refuted chance ([write-up](docs/consultations.md)); `deep/`, the multi-agent deep dive that explained it, with its investigators', verifiers' and checkers' scripts and [the report](examples/rule-4850/deep/REPORT.md) |
| `scale-up-linear` | the scale-up instrument (`scaleup.py`: zoom out a LatticeLife torus by blocks and test whether a coarse world predicts the zoomed-out fine one) and its registered calibration on the four parity rules: exact at powers of two up to 128, a fair coin per supercell at mismatched scales, with the coins' independence worked out from the group ring (`mismatch.py`); 296 of 296 cases held. `promote.py` checks that LatticeLife's own `experiments.coarse`, where the instrument now lives, reproduces every record ([plan](docs/scale-up-plan.md)) |
| `scale-up-compete` | worlds of several species, exploratory. `first_look.py`: two Life-like pairs on 128 x 128 and twelve five-species soups with rules drawn as `latticelife autorun` draws them, under the random draw; its spreads set the margins of `scale-up-tie-break`. `laws.py`: laws against time and size at seven sides from 32 to 256 for Life against HighLife and one soup: no mean depends on the side, every spread falls as one over the side, and the soup's rare species survives only on large grids, because what is left of it is 2 x 2 blocks that nothing can break and a small grid often has none |
| `scale-up-sizes` | the registered scale-up test, part 1: the laws of `scale-up-compete` at sides 512 and 1024, 32 starts each (`sizes.py` holds the design both parts share; all 62 predictions held). `extras.py`: what else both parts' runs show, exploratory; `recheck.py`: fresh starts of one world at one side, used to check a registered sample that ran high |
| `scale-up-sizes-large` | part 2: the same 62 predictions at sides 2048 and 4096, 16 starts each, registered with part 1 and run on a rented machine (all 62 held); `pod/` holds the scripts that rented it, ran it there and brought the ledger home |
| `scale-up-closure` | step 4, the zoom-out: `zoom.py` reads a world of several species through blocks with the clock at the block and learns coarse rules as tables; `look.py`, a first look at the pair and the soup (exploratory); `study.py`, the registered test on a torus twice as wide (43 of 45 predictions held) |
| `scale-up-search` | step 4b, the search for a world that organises itself (exploratory): `organised.py`, the measure (the correlation area of block sums, and which clock goes with a zoom-out); `search.py`, the screen of 2,407 worlds; `contests.py`, the rules that grow alone against a copy of themselves, against each other, as three and five copies and against the rules one count away; `rivals.py`, every one of 1,196 random rules against a copy of itself, and what the ones that hold territories have in common; `confirm.py`, the picks again on a grid sixteen times as large from fresh starts; `long.py`, the worlds with territories followed to generation 16,384; `pictures.py`, the worlds drawn as one page |
| `scale-up-territories` | step 4c, the registered test of which rules hold territories against a copy of themselves: 600 fresh rules, each alone and against its copy, and 242 more for the second cut (`study.py`; all 10 predictions held); `territories.py`, the design it shares with `sizing.py`, the look at how far a rule's verdict hangs on its start (199 of 200 rules the same from another) |
| `scale-up-closure-territories` | steps 4d and 4e, worlds of territories zoomed out. `look.py`, the first look at two of them (exploratory): each read through blocks of 4 to 32 on two clocks with `scale-up-closure`'s instrument, who leads a block next learned from its neighbours, and that rule tried at another time, at the next rung, in the other world and run on by itself; `pictures.py` draws the real world beside the coarse rule's own. `study.py`, the registered test on six worlds (73 of 89 predictions held); `ladder.py`, the measures it shares with `sizing.py`, which put the first look's runs through them before any bound was drawn and wrote down the first look's rules (`reference.json`); `extras.py`, each world's pace read off its walls, and the still world's rule run on at that pace (exploratory) |
| `scale-up-class` | step 4f, the registered test of how wide the class is: 38 worlds never zoomed out, the still world's rule kept at eleven paces and tried in each, each world's clock and pace read off its walls, and the rule run on at that pace (`study.py`; 54 of 128 predictions held); `sizing.py` chose the worlds from `scale-up-territories`' records (`worlds.json`) and sized the bounds on `scale-up-closure-territories`' |
| `scale-up-rung` | step 4g, the registered test of one more rung: two worlds on a 2,048 grid to generation 16,384, every block size at the age that matches it, and the rule of each rung run on as the rule of the rung above (`study.py`; all 22 predictions held); `sizing.py` read the first three rungs from runs that exist; `extras.py` reads the run's records further (exploratory): the rule of every lower rung at every rung, the other world's rule, start by start, and where the gap is; `back.py`, a first number for the plan's next decision (exploratory): whether a block that has just changed hands changes back more often than the table knows |
| `scale-up-memory` | step 4h, a coarse rule that remembers (exploratory): `look.py` reads the block leaders `scale-up-rung` kept with a block's past in view (who led it one tick before; how long it has had its leader), sets the table by a block's past beside itself at every rung, scores each reading's rule one tick ahead with a correction for how little a rung has to learn from, and runs each rule on (`look/summary.json`); `pictures.py` draws the table, a line for each rung. Step 4i, the registered test of it on fresh starts at step 4e's size (`study.py`; all 74 predictions held; `sizing.py` put seen runs of that size through every claim and wrote down the look's rules, `reference.json`) |
| `scale-up-gap` | do the large grids agree with each other: the pair at sides 1024, 2048 and 4096 from 512 fresh starts, registered after one sample of the scale-up test ran high (all 9 predictions held: no pair of sides differs by as much as the gap seen) |
| `scale-up-tie-break` | does the birth tie-break change a world of several species: the random draw against the standoff from the same starts, on two Life-like pairs and 24 soups (registered; all 15 predictions held: no difference where contests are rare, a lowered live fraction where they are common) |

## Settling times: a replication and a universality test

[docs/settling-time.md](docs/settling-time.md) takes the loop's own B2/S34 answer to rules with no
exact theory. It uses two registered studies, both built on `lattice_lab.study`: a harness that
writes a study's predictions to the ledger and refuses to run it until they are committed and
pushed.

- **Replication** (`examples/settling-time-replication`). On hexagon tori up to 1024, B2/S34's
  median settling time stays logarithmic in the size, and the power law is rejected. Two
  extreme-value mechanisms predicted the fluctuations from each law's constants. The heavy-tailed
  one failed outright. The light-tailed one (Gumbel) got the shape and constancy right but the
  size wrong.
- **Universality** (`examples/settling-universality`). Eight rules were drawn at random on the
  square, hexagon and both triangular lattices. For all eight, the log law held and the power law
  failed. The fluctuations share one shape and one ratio of spread to growth on every lattice.
  Both match the Gumbel values for the largest of about L^2 independent times: 0.177 +- 0.023
  against 0.2215, and 0.765 +- 0.029 against 0.786. This is extreme-value universality, not
  a critical point's. At these error bars, Kepler's identify cannot yet name the class blind.
- **Round 2** (`examples/settling-time-local`) tested a post-hoc idea for Study A's miss, on
  B2/S34's local settling times (when each block of the torus settles; a new LatticeLife
  instrument). They are the same on every torus size but not independent: late regions cluster.
  The miss itself was a low draw. With all the data, B2/S34's ratio is 0.765 +- 0.042, the same
  as the eight rules'.

## Trusting the answers

- **Self-check.** `selfcheck` runs the loop on synthetic data from every law, with the sizes,
  seed spreads and censoring of real runs. It compares the outcome with pass marks committed in
  `thresholds.toml` before its first run and never edited to pass. The latest result is in
  [docs/selfcheck.md](docs/selfcheck.md); [docs/selfcheck-history.md](docs/selfcheck-history.md)
  records every full run, including the first, which failed, and what changed in the loop.
- **Known rules.** The empty rule `B/S` gives a constant. A linear rule's transients and periods
  match an independent GF(2) computation (`tests/test_known_rules.py`).
- **Order.** `verify` checks every verdict's predictions were written before its run started,
  and every held-out record was appended after that.
- **Reproducibility.** `verify --rerun N` reruns records from their seeds and settings and
  compares the bytes. A registered study gets the same check when it names `rerun`.
- **The prototype's traps** are regression tests (`tests/test_traps.py`): a zero starting
  constant must not vanish; a verdict must survive dropping the smallest sizes; an unsettled run
  must never count against a law.

## Licence

Copyright 2026 PolyLabs Research.

- **Code** is under the [Apache License 2.0](LICENSE): `src/`, `tests/`, the Lean library in
  `proofs/`, the site's build scripts, JavaScript and Apps Script, and every program in
  `examples/` and `consultations/` (Python, shell, C and Lean files).
- **Everything else** is under [Creative Commons Attribution 4.0](LICENSE-CC-BY-4.0): the
  documentation, questions and consultations, the studies' ledgers, records, data, judgements,
  logs and transcripts, and the website's text and figures. Credit "PolyLabs Research,
  lattice-lab" with a link to this repository.
- **The fonts** in `site/public/assets/fonts/` are under the SIL Open Font License 1.1, in the
  `OFL-*.txt` files beside them.
