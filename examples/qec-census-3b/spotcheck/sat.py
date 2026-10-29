"""
Spot-check C6 (docs/census-stage3b-spotcheck-plan.md): certified lower bounds on the distance of
a bivariate bicycle code by SAT, with the solver's UNSAT proof checked by drat-trim.

**The claim** "no Z-logical of weight <= w", encoded as CNF; UNSAT proves it.
- **Variables.** x_q for each qubit q: the support of c.
- **c in ker H_X.** For each row h of H_X, x restricted to h has even parity. With w(h) = 6, that
  is the 32 clauses that forbid each odd assignment of h's six variables, so no auxiliary
  variables are needed.
- **c is nontrivial.** For each X-logical L_j in a basis of ker H_Z modulo the rowspace of H_X
  (distance._logicals_bits), y_j = parity of x over L_j, by a chain of Tseitin XOR gates. Then
  one clause y_1 or ... or y_k: c in ker H_X is a Z-logical exactly when some L_j has odd overlap
  with it (distance.py's module docstring).
- **|c| <= w.** Sinz's sequential counter: s_{i,j} means "at least j of x_1..x_i are true".
- **Translation.** One clause, x_0 or x_lm: some translate of a least-weight logical contains
  qubit 0 or qubit lm (distance_ilp's translation argument, distance.py). It changes nothing
  about the claim's truth, and cuts the search a great deal.

**The certificate.** CaDiCaL writes a DRAT proof of UNSAT (binary DRAT, half the size of the
text form; drat-trim detects it), and drat-trim checks it against the CNF. Both run under their
own time limits (CaDiCaL's -t, drat-trim's -t) as well as Python's, so neither outlives a job
that dies. A proof larger than PROOF_CAP bytes is not checked (drat-trim holds it in memory):
the claim is then "unverified", which concludes nothing. A verified claim rests on the encoding
above (tested against enumeration in tests/test_qec_census_3b_spotcheck.py), the translation
argument, and drat-trim.

When the formula is SAT, the model is a Z-logical of weight <= w. It is checked by
distance.verify_witness, and it is an upper bound.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from itertools import product
from pathlib import Path

TOOLS = Path(os.environ.get("SPOTCHECK_TOOLS",
                            "/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/"
                            "scratchpad/tools"))  # fmt: skip
CADICAL = TOOLS / "cadical" / "build" / "cadical"
DRAT_TRIM = TOOLS / "drat-trim" / "drat-trim"
PROOF_CAP = int(os.environ.get("SPOTCHECK_PROOF_CAP", 40 * 10**9))


class CNF:
    def __init__(self):
        self.nvars = 0
        self.clauses: list[list[int]] = []

    def var(self) -> int:
        self.nvars += 1
        return self.nvars

    def add(self, clause):
        self.clauses.append(list(clause))

    def xor_gate(self, a: int, b: int) -> int:
        """A fresh variable z with z = a XOR b."""
        z = self.var()
        self.add([-z, a, b])
        self.add([-z, -a, -b])
        self.add([z, -a, b])
        self.add([z, a, -b])
        return z

    def even(self, vs):
        """The parity of vs is even: forbid every odd assignment (for short rows)."""
        for signs in product((0, 1), repeat=len(vs)):
            if sum(signs) % 2 == 1:  # an odd assignment: the clause rules it out
                self.add([-v if s else v for v, s in zip(vs, signs, strict=True)])

    def at_most(self, xs, w: int):
        """Sinz's sequential counter for sum(xs) <= w."""
        n = len(xs)
        if w >= n:
            return
        if w == 0:
            for x in xs:
                self.add([-x])
            return
        s = [[self.var() for _ in range(w)] for _ in range(n)]
        self.add([-xs[0], s[0][0]])
        for j in range(1, w):
            self.add([-s[0][j]])
        for i in range(1, n):
            self.add([-xs[i], s[i][0]])
            self.add([-s[i - 1][0], s[i][0]])
            for j in range(1, w):
                self.add([-xs[i], -s[i - 1][j - 1], s[i][j]])
                self.add([-s[i - 1][j], s[i][j]])
            self.add([-xs[i], -s[i - 1][w - 1]])

    def dimacs(self) -> str:
        lines = [f"p cnf {self.nvars} {len(self.clauses)}"]
        lines += [" ".join(map(str, c)) + " 0" for c in self.clauses]
        return "\n".join(lines) + "\n"


def encode(hx: list[int], logicals: list[int], n: int, w: int, anchors=None) -> tuple[CNF, list]:
    """The CNF of 'a Z-logical of weight <= w exists' (module docstring), and x's variables."""
    cnf = CNF()
    x = [cnf.var() for _ in range(n)]
    for row in hx:
        cnf.even([x[q] for q in range(n) if row >> q & 1])
    ys = []
    for L in logicals:
        support = [x[q] for q in range(n) if L >> q & 1]
        acc = support[0]
        for v in support[1:]:
            acc = cnf.xor_gate(acc, v)
        ys.append(acc)
    cnf.add(ys)
    if anchors is not None:
        cnf.add([x[a] for a in anchors])
    cnf.at_most(x, w)
    return cnf, x


def certify(hx, logicals, n: int, w: int, anchors=None, limit: float = 14400.0) -> dict:
    """Solve the claim at weight w. UNSAT: the proof checked by drat-trim ('verified'). SAT: the
    model's support (a logical of weight <= w). Returns status, the support if any, the seconds."""
    cnf, x = encode(hx, logicals, n, w, anchors)
    with tempfile.TemporaryDirectory(prefix="spotcheck-sat-") as d:
        f, proof = Path(d) / "f.cnf", Path(d) / "f.drat"
        f.write_text(cnf.dimacs())
        t0 = time.time()
        try:
            run = subprocess.run([str(CADICAL), "-q", "-t", str(int(limit)), str(f), str(proof)],
                                 capture_output=True, text=True, timeout=limit + 300)  # fmt: skip
        except subprocess.TimeoutExpired:
            run = None
        solve_s = time.time() - t0
        base = {"w": w, "seconds": round(solve_s, 1), "vars": cnf.nvars,
                "clauses": len(cnf.clauses)}  # fmt: skip
        if run is None or run.returncode == 0:  # 0: CaDiCaL stopped at its limit, unknown
            return {"status": "timelimit", **base}
        if run.returncode == 10:  # SAT
            model = {int(v) for line in run.stdout.splitlines() if line.startswith("v")
                     for v in line[1:].split() if int(v) > 0}  # fmt: skip
            support = [q for q in range(n) if x[q] in model]
            return {"status": "sat", "support": support, **base}
        if run.returncode != 20:
            raise RuntimeError(f"cadical returned {run.returncode}: {run.stderr[-500:]}")
        size = proof.stat().st_size
        if size > PROOF_CAP:
            return {"status": "unverified", "reason": f"proof of {size} bytes not checked",
                    "proof_bytes": size, **base}  # fmt: skip
        t1 = time.time()
        check_limit = max(limit, 3600)
        try:
            argv = [str(DRAT_TRIM), str(f), str(proof), "-t", str(int(check_limit))]
            check = subprocess.run(argv, capture_output=True, text=True,
                                   timeout=check_limit + 300)  # fmt: skip
            verified = "s VERIFIED" in check.stdout
            reason = None if verified else (check.stdout[-300:] or f"exit {check.returncode}")
        except subprocess.TimeoutExpired:
            verified, reason = False, "drat-trim did not finish"
        out = {"status": "verified" if verified else "unverified", **base,
               "check_seconds": round(time.time() - t1, 1), "proof_bytes": size}  # fmt: skip
        if reason:
            out["reason"] = reason
        return out
