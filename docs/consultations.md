# Consultations: other models on our questions

**Status: a record, kept as we go.** Besides the pilots, where one agent works a card in an
isolated container, we put questions we have already answered to other models, to gauge how hard
they are and to collect other routes and ideas. Every claim a consultant makes is checked by
machine before it counts, and anything it predicts is registered and tested like our own
predictions (`examples/fable-units`).

## The protocol

- **The same prompt to every model**, first without hints. A follow-up, if any, is recorded with
  the exact text, and it is the same for every model that gets it.
- **Independent answers.** No model sees another's answer before giving its own.
- **Checked by machine.** Every identity a consultant states is multiplied out again with the
  orchestrator's arithmetic, and every claim about eigenvalues is checked against `eigen.py`.
- **Graded against a rubric** written before the answers were read.
- **Predictions are registered** before they are tested.

## Running a consultation

`lattice-lab consult` (`src/lattice_lab/consult.py`) puts one prompt to Claude Fable
(`claude-fable-5-1`) and ChatGPT through their APIs, concurrently and independently, and keeps
every exchange.

```bash
uv sync --group consult
uv run lattice-lab consult ask NAME --question q.md --context docs/STATUS.md --context card.md
uv run lattice-lab consult ask NAME --preset direction     # STATUS and every write-up: what next?
uv run lattice-lab consult review NAME                     # round 2
```

- **The prompt** is a fixed preamble (what the project is, and that every claim will be checked,
  so state it precisely, say whether it is proved, computed or conjectured, and check it by
  running code where possible), then each `--context` file in full (a directory gives all its
  Markdown files), then the question. Context is the foundation: the m = 37
  consultations showed that a model given the structure already worked out builds on it, so a
  consultation should carry the card, data or write-up its question rests on. Everything in it is
  sent to both providers.
- **Round 1** (`ask`): every consultant answers alone. **Round 2** (`review`, optional): every
  consultant gets the round-1 prompt and all the complete answers, labelled A, B, ... in name
  order without names, and is asked where they agree and conflict, which claims are wrong, and
  for a revised recommendation. The same prompt goes to every consultant in each round.
- **Records** go to `consultations/NAME/round-N/`: `prompt.md`, exactly as sent; for each
  consultant `NAME.json` (model requested and model that served, effort, the parameters sent, the
  prompt's sha256, start and finish times, usage, stop reason, request id, the summarised
  reasoning, the answer) and `NAME.md` (the answer alone); and in round 2 `labels.json`, which
  letter was whom. Files are written once and never overwritten. A failed call leaves no record,
  and an answer cut off at the output limit is kept in `attempts/NAME-K.json` (its summarised
  reasoning is often worth reading) but does not count as the answer, so running the same command
  again asks only the consultants still without one, and refuses if the prompt has changed.
  Commit the directory: git is the record's history.
- **Code.** Both consultants can run code in their provider's sandbox by default (Anthropic's code
  execution tool, OpenAI's code interpreter), and the record keeps every block of the exchange,
  the code and its output included. Fable's earlier, strong answer on the m = 37 cubes came from
  the chat app, where it could compute; its two errors in section 2, without code, were of the
  kind one computation catches. `--no-code` turns it off. The prompt is marked for caching: a
  tool loop rereads it at every step, and uncached each reread bills in full (a three-call test
  billed 36,620 input tokens uncached, against 163 plus 27,186 read from cache, at 2.5% of the
  price). A tool loop that the server pauses is resumed in the same container.
- **Settings.** Fable runs with adaptive thinking (summarised), effort `high`, an advisory task
  budget of 64,000 tokens (thinking and answer together; the model sees it and paces itself), a
  hard limit of 128,000 output tokens, and Anthropic's server-side refusal fallback
  (`fallbacks: "default"`), so a request a safety classifier declines is rerun on a fallback
  model; the record says when that happened and which model answered. The budget is there because
  the first consultation, without one and with a 64,000-token limit, thought until the limit and
  wrote no answer. ChatGPT runs through the Responses API with reasoning effort `high`, summaries
  on, `store: false` and up to 64,000 output tokens. Change these with `--effort fable=xhigh`,
  `--budget fable=96000` (`0` for none), `--max-tokens NAME=N` and `--model chatgpt=ID`;
  `--with fable` asks one only; `--dry-run` prints the prompt and the parameters and calls
  nothing.
- **Keys and model.** `CONSULT_ANTHROPIC_API_KEY`, `CONSULT_OPENAI_API_KEY` and
  `CONSULT_OPENAI_MODEL` (ChatGPT's model has no default). The names are not the usual ones so
  that a cloud session's own Claude credentials are never used for these calls, and the API hosts
  are fixed. In a cloud session, add them to the environment's variables; the network policy must
  also allow `api.openai.com`.
- **Cost.** At Fable's prices ($10 and $50 per million input and output tokens; a cache write
  costs 1.25 times input and a cache read 2.5% of it) output dominates: $3.20 per 64,000 tokens.
  The `direction` prompt, now STATUS and every write-up, is about 264,000 characters (roughly
  70,000 tokens, $0.88 to write to the cache once). The first attempt used all 64,000 output
  tokens and cost $3.33; the second, with the budget, $1.20. What effort and budget are worth
  paying for is measured in section 3. ChatGPT's cost depends on the model.

What comes back is a consultant's view, not a result. Its claims are checked, and its predictions
registered, before anything is built on them.

## 1. The cubes at m = 37 (pilot 4's question), 2026-10-19 and 20

**The prompt** gave the five square rules of pilot 4 as unions of D4 orbits, the observation that
every nonzero eigenvalue of each is a cube in F(2^18) at m = 37, that a random rule does this about
once in 20,000 tries, that none does anything similar at any other odd m from 9 to 161, and that
the same holds for t(x) = x + 1/x; it asked why, for a general condition, and for a proof. **The
rubric**: the arithmetic 2^9 = -6 and 6^2 = -1 (mod 37), so the dilation by 6 acts as a Frobenius;
F(2^9) lies in the cubes; an identity that makes the rules invariant under it; rule 90's
confinement; the shared factor; a proof for all five.

**ChatGPT, unaided** (about 20 minutes, with code). It found the shared factor (f2, f3 and f5 are
f1 times uv, u + v and (1 + u)(1 + v), with u = x + 1/x, v = y + 1/y) and proved the claim with a
certificate: every nonzero value is a cube exactly when f^87381 is idempotent in the group algebra,
and it checked that identity for f1, f4 and rule 90 by computer. Correct (its script and our
eigenvalues agree: f1 has no zero eigenvalue, f4's zeros are exactly the lines k = +-6j), but the
criterion is equivalent to computing every eigenvalue, so it does not explain; it said so itself.

**ChatGPT, after a hint** (the same follow-up for any model: that its criterion confirms without
explaining, and pointing at its own observation that f4 vanishes on lines of slope +-6, with
6^2 = -1). In 35 minutes it gave a structural proof: the ratio R = D3/D2 of square sums is inverted
by the dilation by 6, which acts on traces as the 2^9-th power, and symmetry then puts a related
quantity in F(2^9), inside the cubes. It also proved rule 90's confinement at 37 by number theory:
the product of 1 - xi^a over the quadratic residues is a unit times sqrt 37 in Q(sqrt 37), equal to
37 - 6 sqrt 37, which is 1 mod 2. Every identity checked.

**Claude Fable** (one answer; whether it saw a hint is to be confirmed). The mechanism (each rule,
up to binomial factors, is invariant under the dilation by 31 = 2^9, with exact congruences such
as f4 · O(19,19) = O(15,15) + O(16,16) mod (x^37 - 1, y^37 - 1)); the same unit argument as ChatGPT,
reached independently; a general theorem with two conditions, one on the binomial "units" and one
on the structure; a criterion for the first, that eps^h lies in Z[sqrt p] for the fundamental unit
eps and class number h of Q(sqrt p); and predictions: the pyramid rules at 101 and 197. Every
identity checked, the pyramid at 101 is family rule 31801, which the sixth pilot's registered
census had already recorded as confined there, and the pyramid at 197 is confined, its neighbour
not. One slip: its list of primes where the criterion fails names 109 and 157, where 2 is not a
primitive root, and omits 173 and 181, which are eligible and do fail.

| | the mechanism | rule 90 at 37 | a general condition | predictions |
| --- | --- | --- | --- | --- |
| Pilot 4's agent (with its card, data and tools) | yes | computed | yes, run at 94 sizes | none |
| ChatGPT, unaided | no (a certificate) | computed | equivalent to computing | none |
| ChatGPT, after the hint | yes | by the unit of Q(sqrt 37) | abstract | none |
| Claude Fable | yes | by the unit, with a criterion | yes | yes, all correct where checked |

**What came of it.** Fable's criterion and pyramid recipe made predictions at primes nobody had
looked at, so they were registered and tested (below). Two models finding the same argument for
rule 90 independently is good evidence that it is the right explanation, and it is better than the
computed cube root in the library's `Cubes37.lean`.

## The registered test of Fable's criterion (`examples/fable-units`), 2026-10-20

**The claims.** For a prime p = 5 (mod 8) at which 2 is a primitive root, (U) rule 90 is confined
to the cubes at p (equivalently, 1 + zeta is a cube in F(2^(p-1))) exactly when eps^h lies in
Z[sqrt p], for the fundamental unit eps and class number h of Q(sqrt p); and at p = i^2 + 1 where
(U) holds, the pyramid rule (the centre and the square rings at radii 2, 4, ..., i/2 - 1) is
confined to the cubes, while the pyramid without its largest ring is not.

**The design.** The predictions come from number theory alone (`units.predicted`: eps from the
continued fraction of (1 + sqrt p)/2, h by counting cycles of reduced quadratic forms), with no
cyclotomic arithmetic. The truth comes from direct computation in GF(2)[x]/Phi_p
(`units.confined`: the norm of 1 + zeta to F(4); `units.pyramid_confined`: the norm of every
eigenvalue of the pyramid, one per orbit of doubling and the lattice's symmetries). The grid was
every eligible prime from 302 to 20,000 (405 of them) and the pyramid primes among them below
10,000 (677, 4357, 5477 and 8837). Every eligible prime up to 301 counts as seen. The predictions
were pushed at 08:32:54 UTC (`981793f`), and the run started at 08:33:03.

**The result: both claims held everywhere.**

- **(U), at 405 primes, none wrong.** 144 are confined: at 114 eps itself lies in Z[sqrt p] (a
  and b even in eps = (a + b sqrt p)/2), and at 30 eps does not but 3 divides h. At the other
  261, eps is not in Z[sqrt p], 3 does not divide h, and rule 90 is not confined. The class
  numbers reach 19 and the units 46 digits.
- **The pyramids, 4 of 4.** Each predicted pyramid is confined and each neighbour is not. The
  largest, at 8837 (i = 94, 23 rings), took 88 seconds; the whole run took 2.5 minutes.
- `lattice-lab verify --lab examples/fable-units`: the ledger's 417 entries chain, no problems.

**What the test does and does not show.** Both claims come with Fable's arguments, and filled in
they are proofs, so the test is a check of the argument and of the arithmetic at scale, not the
settling of a conjecture. Fable's step from (U) to eps^h is one line ("i.e."). It is Dirichlet's
class number formula: with eta and eta' the products of 1 - zeta^s over the quadratic residues and
non-residues, eta eta' = p and eta'/eta = eps^(2h), so eta = sqrt p eps^(-h). Since
sqrt p = 2 theta - 1 = 1 (mod 2), eta = 1 (mod 2) exactly when eps^h does, which is when eps^h
lies in Z + 2 O_K = Z[sqrt p]. For the pyramids, Fable's identity
sum_{r <= N} Q_r t(X) t(Y) = t(X/Y) t((XY)^(2N+2)) + t(XY) t((X/Y)^(2N+2)) (with 2N + 2 = i)
puts their values off the axes, up to rule-90 factors, in the field fixed by the dilation by i,
and since 2^((p-1)/4) = +-i with (p - 1)/4 odd, that field lies in the cubes. That the
neighbours fail is not part of any proof; it is an observation, and it held at all four. The one
error in Fable's answer stands: its list of primes where (U) fails names 109 and 157, where 2 is
not a primitive root, and omits 173 and 181.

## 2. What next? (the `direction` preset), 2026-10-20

The first consultation by API (`consultations/2026-10-20-next-steps/`), Fable only, as a check of
the tool; ChatGPT's key is not yet set. The prompt was the preamble, STATUS and this file, and the
`direction` question. **The first attempt** thought for 14 minutes, used all 64,000 output tokens
on thinking and wrote no answer ($3.33; kept as `round-1/attempts/fable-1.json`). Fable now runs
with a task budget (above). **The second** answered in 4.9 minutes: 15,372 thinking tokens, about
6,000 of answer, $1.20.

**What it suggested.**

1. *One theorem for the power mechanisms:* if f = g^N in the group ring at m, every eigenvalue
   of f is an N-th power and P(f) = P(g)/gcd(P(g), N). Twisted powers by d = 2^k are the case
   N = 1 + 2^k, and invariance under a dilation by 2^k is f = f^(2^k). So round 4 should search
   for N, over every prime q dividing 2^sord(m) - 1, not only q = 3. It gave predictions at
   m = 13 and 37.
2. *Rebuild the chance model on Galois orbits:* the eigenvalues of a symmetric rule at a prime p
   with 2 primitive fall into one orbit per slope, which D4 merges further; treat orbits as
   independent except where an identity ties them, and register the expected counts.
3. *Close the XOR law's ten unchecked odd parts* by looking up the factorisations of 2^s - 1
   they need, and reconcile rule 90's list with Martin, Odlyzko and Wolfram (1984).

It called "why a non-confined rule reaches the full bound" mis-posed (a tautology unless posed
as a null model), and asked for two rechecks: that every ledger period is the linear map's, not
one sampled orbit's, and that "the hexagon law, proved for every even n" covers odd parts 1
and 3.

**The orchestrator's first check** (arithmetic by machine, the rest against the write-ups; no
prediction has been run yet):

- **Every number checks**: the factorisations of 2^36 - 1 and 2^18 - 1, the residues
  (2^10 = 10, 2^9 = 5, 2^6 = 12, 2^4 = 3 mod 13; 2^6 = 27 and 2^9 = -6 mod 37) and all six
  predicted periods (819, 455, 63, 4095 and 21 at 13; (2^36 - 1)/65 and 511 at 37). They follow
  from its claim A, which is correct and short, so they test the engines rather than a
  hypothesis.
- **Overstated**: "the five mechanisms are one statement". Splitting, the unit times a cube of
  pilot 6, and rule 90's own confinement at 37 (Fable's earlier criterion) are not f = g^N.
- **Two errors.** Its claim D takes the square parity rule to be t(x) + t(y), which vanishes on
  the diagonals; the rule is t(x) + t(y) + t(x) t(y) (xor-periods-proof.md), whose diagonal
  values are t^2, not 0. And its 7th-power prediction at 37 rests on "no subfield of F(2^18) has
  index divisible by 7", which is false for F(2) and F(4) (indices 262,143 and 87,381); the
  conclusion may still hold for shell rules, but not for the reason given. Its own count of slope
  classes at 13 (5) is right: a machine count gives 5 at 13 and 11 at 37, (p + 7)/4; the 7 it
  then offered is wrong.
- **Already settled in the write-ups it was not given**: the ten odd parts are exactly those
  where a factor of 2^s - 1 could not be factored here (xor-periods-proof.md), equality was
  checked against complete factorisations at the other 489, and the exact engines compute the
  period of the linear map (a single live cell generates the whole ring). The hexagon's odd
  parts 1 and 3 are proved separately, with different values (parity-lattices.md); STATUS's one
  line, "2 * 2^v(n) R(m), proved for every even n", is loose there and should say m >= 5.
- **Worth acting on**: looking up the ten factorisations (published tables may now have them,
  which would finish the XOR and triangle odd parts to 999); the search over N for round 4; and
  stating the chance model per Galois orbit, which open question 1 already asks for.

The lesson for the tool: the `direction` preset sends STATUS, which summarises, so a consultant
flags what the full write-ups settle. A consultation about one result should carry its write-up.

## 3. What effort is worth: a benchmark (`examples/consult-budget`), 2026-10-20

**The question** was the cost of a *verified* answer, not of an answer: a cheap answer that is
wrong, or needs more rounds, is not cheap. The design (`rubric.md`), the questions and the
machine grader were pushed before any call (`f50fbd9`, 10:35:52 UTC). Two questions the project
has answered: **Q1**, pilot 4's five rules at m = 37, word for word as put to ChatGPT and in
the chat app (the mechanism is a dilation by 6 acting as half a Frobenius); **Q2**, pilot 6's
sixteen rules from its card (nine are a unit times a cube). Three settings, each twice per
question: **S0** effort high, 64,000-token budget, no code; **S1** the same with code
execution; **S2** effort xhigh, 128,000-token budget, code. Every congruence and factorisation an
answer listed was evaluated in F2[x, y]/(x^37 - 1, y^37 - 1) by the grader; the rubrics were
graded blind (labels unmasked after `grades.json` was pushed, `31523d2`).

**What went wrong first: half the answers were not Fable's.** Fable's **cyber** safety
classifier declined 6 of the 12 calls, a false positive on GF(2) arithmetic: 5 of Q1's 6, 1 of
Q2's. The server-side fallback reran each on **Claude Opus 4.8**, and the records say so
(`fallback`, `served_by`, and the switch block's category). The cost estimate first priced only
the serving attempt; it now prices every attempt at its own model's rates (`consult.attempts`,
`consult.cost`), from the usage the records keep. The twelve calls cost **$27.78**.

| | answers | verified successes | mean cost | cost per success |
| --- | --- | --- | --- | --- |
| S0: high, 64K, no code | 4 (1 Fable, 3 Opus 4.8) | 0 | $0.78 | none |
| S1: high, 64K, code | 4 (3 Fable, 1 Opus 4.8) | 1 | $2.44 | $9.77 |
| S2: xhigh, 128K, code | 4 (2 Fable, 2 Opus 4.8) | 2 | $3.72 | $7.45 |
| S1, then S2 when the check fails (estimated) | | 62% | $5.23 | $8.37 |
| Fable's answers only: S1 | 3 | 1 | $2.61 | $7.84 |
| Fable's answers only: S2 | 2 | 2 | $4.81 | $4.81 |

**The registered decision rule** (lowest cost per success; within a factor of 1.5, the cheaper
per answer) picks **S1** on all twelve answers, since S1 is within 1.31 of S2. On Fable's
answers alone, which is the comparison the design meant but a selection it did not register, S2
is cheaper per success by a factor of 1.63 and is picked. With one or two successes per arm,
neither is more than a first reading.

**Per question:**

- **Q1: no answer succeeded, at any setting, from either model.** None found the mechanism.
  Without code, both answers (Opus 4.8) restated the observation as "f is a cube in the group
  ring" and stopped. With code, all four went for certificates: three gave a complete,
  machine-confirmed proof of the observation for all five (the norm to F(4) is idempotent,
  ChatGPT's unaided route), and the one Fable answer also derived rule 90's unit criterion by
  Dirichlet's formula. Three of the six asserted that no structural reason exists, or that the
  confinement is a coincidence ("I believe there is none"), which is false and is the costly kind
  of error: it would stop the search. Fable in the chat app had found the mechanism from the
  same question; whether that answer itself came from Fable is not known, since consumer apps
  also fall back to Opus 4.8.
- **Q2: the dearer setting paid.** S2: 2 of 2 (both Fable, all nine found, both reasons right).
  S1: 1 of 2 (the other found the structure only as cube roots in the group ring, with hundreds
  of terms). S0:
  Fable without code found **eight of the nine by hand**, every one machine-confirmed, and missed
  28944; Opus 4.8 without code listed no factorisation and conjectured wrongly.
- **No false claim** reached the grader in any answer: told that a failed claim counts against
  them, all twelve listed only identities that hold. The errors were in the prose, where only the
  rubric caught them.

**What the answers found that the project did not know** (both checked here by machine):

- **Rule 4850 has every nonzero eigenvalue a ninth power at m = 37** (an S2 answer); it is the
  only one of the sixteen. Pilot 6 counted it among the seven that chance explains; a ninth-power
  confinement is far beyond chance, so at least this one has a mechanism nobody has found.
- **17056 is 1112 under the exponent map (a, b) -> (a + b, a - b)**, determinant -2, so the two
  have the same eigenvalues at every odd m (an S1 answer). The sixteen are fifteen independent
  cases.
- One answer re-derived pilot 6's correction of the chance model independently (per-class cube
  rates of 0.937 on the axis and diagonal at 37, about 5.7 expected), and two more found the
  "once in 20,000" figure wrong for the family.

**One weakness of the grader**: a cube root in the group ring counts as a "find", but every
confined rule has one (dense, hundreds of terms), so the rule admits an answer that has not found
the mechanism. It changed no success here (the answer with three such roots failed on the
others), and should require a cube root with few terms next time.

**What this says about the budget.** Code is the large effect: no answer without it succeeded,
and on Q2 three of the four Fable answers with code did. Beyond that, more effort bought
successes on the question where they were possible (Q2), at a lower cost per success, and did
not help on Q1, where every setting chose a certificate over a mechanism. The false economy is
real but is not mainly in dollars: a cheap answer that confidently says "there is no mechanism"
costs more than its price. So the measure that matters is the check, not the setting: machine
checks caught nothing because the models stayed within what they had verified, and the rubric
caught the confident prose. The classifier is the other cost: on these questions a Fable
consultation is an Opus 4.8 consultation about half the time, and the record must be read for
`served_by` before any comparison.
