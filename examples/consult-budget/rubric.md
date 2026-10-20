# What a consultation's effort is worth: the registered design

Written and pushed before any call. The question: at which settings does consulting Claude Fable
cost least **per verified correct answer**, not per answer. A cheap answer that is wrong, or
needs several more rounds, is not cheap.

## The questions

Two questions whose answers the project already has, each self-contained (no documents):

- **Q1, the five rules at m = 37** (`q1-five.md`): the fourth pilot's question, word for word as
  put to ChatGPT and to Fable in the chat app on 2026-10-19 and 20 (docs/consultations.md,
  section 1), with a request for machine-checkable congruences appended.
- **Q2, the sixteen rules at m = 37** (`q2-sixteen.md`): the sixth pilot's card, with its data and
  its one hint (nobody has checked whether the rules factor), without its tools and deliverables,
  and with a request for machine-checkable factorisations.

## The settings

| arm | effort | task budget | output limit | code execution |
| --- | --- | --- | --- | --- |
| S0 | high | 64,000 | 128,000 | no (the first consultation's setting) |
| S1 | high | 64,000 | 128,000 | yes |
| S2 | xhigh | 128,000 | 128,000 | yes |

Each arm answers each question twice, independently: 12 calls, run concurrently per question.
The prompt is the same in every arm (the consultation preamble and the question). Spending cap:
$60 in all, from the records' cost estimates; the run stops before a question that could pass
it.

## Grading

**By machine** (`bench.py grade`): every congruence and factorisation in the answer's JSON block
is evaluated in F2[x, y]/(x^37 - 1, y^37 - 1) with the orchestrator's arithmetic. A claim that
fails is **false**; one that cannot be parsed is **unreadable** (counted separately, not false).

**Q1 rubric** (graded blind: the answers relabelled at random, the labels unmasked only after
every grade is written):

- R1 the arithmetic: 2^9 = -6 (or 31 = 2^9) mod 37, so a dilation acts on values as a Frobenius
  power;
- R2 the subfield: F(2^9) lies in the cubes (511 is prime to 3);
- R3 an invariance identity: some f, times factors whose values are cubes, is invariant under
  the dilation mod 37, as a congruence that the machine confirms;
- R4 rule 90's confinement at 37 explained, not only computed (for instance by the unit of
  Q(sqrt 37));
- R5 the shared factor: f2, f3, f5 are f1 times ab, a + b, (a + 1)(b + 1), a = x + 1/x,
  b = y + 1/y, or the equivalent;
- R6 a proof that covers all five, including f4 and the characters where a multiplier vanishes.

**Q1 succeeds** when R1, R2, R3 and R6 hold and the machine finds no false claim.

**Q2, by machine**: a target is **found** when the answer gives a factorisation of it that the
machine confirms, with a factor of two or more terms raised to a power divisible by 3. The
nine that are a unit times a cube (1112, 2436, 3461, 10498, 13584, 17056, 18246, 26883, 28944)
are the known finds; a confirmed factorisation of that kind for any of the other seven counts
too.

**Q2 rubric** (blind): Q1 why the unit's values are cubes at 37 (products of rule-90 values, or
the equivalent); Q2 why exactly the three are confined at 61 too ((a + 1)(b + 1), through
Psi_3 or 3 = 2^6 mod 61, or the equivalent); Q3 says the remaining seven are unexplained, or
gives a correct reason.

**Q2 succeeds** when all nine are found, rubric items Q1 and Q2 hold, and the machine finds no
false claim.

## What is reported

Per arm: answers, successes, false claims, mean cost, time and tool calls, and the **cost per
verified success**, the arm's total cost over its successes. Also the escalation policy "S1, and
S2 when the check fails", estimated from the arms' rates as c1 + (1 - p1) c2 per question, with
success 1 - (1 - p1)(1 - p2), assuming independence.

**The decision rule**: recommend the arm (or the escalation policy) with the lowest cost per
verified success; where two are within a factor of 1.5 of each other, the cheaper per answer.
With two answers per question per arm, this can tell 0 of 4 from 4 of 4 and little finer, so it
is a first measurement, to be repeated on real consultations.
