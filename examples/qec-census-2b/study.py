"""
A registered continuation of stage 2 of the code census (examples/qec-census-2): the jobs its
registered run could not do, with the predictions stage 2 registered for them, copied verbatim.

    uv run --no-sync python examples/qec-census-2b/study.py register
    uv run --no-sync python examples/qec-census-2b/study.py run --workers 4
    uv run --no-sync python examples/qec-census-2b/study.py resume --workers 4   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-2b

**Why.** Stage 2's registered run (its ledger: registration, run_started, two run_resumed,
observations, verdict) ran to its end with the verdict "incomplete": 54 of its 222 jobs failed,
the torus jobs of the 46 held-out tori with lm >= 129 and the 8 H7 jobs on those tori (3x45,
3x49, 3x50, 5x27, 5x30, 7x21). census.c had `#define MAXLM 128` (WORDS 4: 2lm <= 256 bits), and
its `k` command exits 1 above that, so census.classes, the first call of torus_record and of
law_record after the guard, raised on each of them. The error rows are in
../qec-census-2/records.jsonl (and in its observations entry). census.c's main() checks the size
before it enters either mode, so nothing was computed on those tori: no rank, k, class or
distance (census.classes had only listed the raw parameters, index tuples from l and m). Stage 2's
verdict stays "incomplete"; this study neither edits its ledger or records nor replaces its verdict.

**The code change** (code_change.json: each file's old and new sha256 and the patch as exact
old/new pairs, which reversed give the old file byte for byte; the tests check it).
- census.c: MAXLM 128 -> 160 and WORDS 4 -> 5 (2lm <= 320 bits), a static assertion that WORDS
  holds 2 MAXLM bits, the comment's 256 -> 320, and a refusal above MAXLM that names lm and
  MAXLM. Nothing else: the rank, the order of the raw codes and the canonical form are as they
  were. The old binary and the new give byte-identical output on every raw code of the 116
  stage-1 tori census.py runs on (5,472,121 codes; development), and the tests check it on
  several, with bb.k_linalg on samples and the k counts of stage 1's file headers; and k on a
  sample of 3x51's raw codes (lm = 153, outside every hold-out list: lm > 150) against
  bb.k_linalg. Every held-out torus has lm <= 150 <= MAXLM. Stage 1's files record the old
  census.c (sha256 a9a3d730...) and census.py (5f652666...); their k are the new census.c's too.
- census.py: Stage2Permit admits one more caller, this file's `job`, with this study's own ledger
  and question id (census.STAGE2B_ID), on the same terms as stage 2's (registered, a run started
  and not finished, the torus held out and registered here); `ranks` raises with census.c's
  message when it refuses; and the docstring says so. stage2_registration_problem takes the
  ledger and id. Nothing else.
Stage 2's study.py, rules.py and tests are unchanged, so its pinned files now differ from its
registration in census_c and census_py only; this registration pins them as they are now.

**The jobs** are exactly stage 2's failed jobs (the error rows' keys), as stage 2 registered them
(its protocol entry's specs, verbatim), with any registered job that waits on one of them (none:
no frontier or cross-check job is on these tori). They run stage 2's own job code, imported
(stage2._dispatch: torus_record, law_record), with stage 2's instruments, limits and timeouts;
only the permit, the code check and the scheduler are this file's.

**The predictions** are stage 2's registered prediction entries, copied verbatim and restricted
to the continuation's items: H1 to H4 on its tori, H5 and H6 on its tori with codes, H7 on its 8
instances; H8 and H9 have no item on these tori (their tori have n <= 252, lm <= 126, and their
jobs succeeded), so they are copied empty and reported "not applicable". Each copy records its
source entry (seq and hash) and the source question's hash. `fed` would list items on other tori
judged from these tori's records (an H2 or H4 item whose odd torus is one of them): none is.
Nothing here computes on any torus (the tests check it with every primitive stubbed to raise).

**decide** gives two judgements.
- *The continuation's own verdict*: stage 2's decide, unchanged, over this run's records and the
  copied predictions (stage 2's per-part rules and verdict rule), with the pinned files checked
  against this registration; a part without items is "not applicable".
- *The combined report*: stage 2's decide over stage 2's registered predictions (its ledger) and
  its registered run's records (its observations entry), each error row replaced by this run's
  record of the same job. The files that differ from stage 2's registration must be exactly the
  documented ones (census_c and census_py), and all files as this study registered them. The
  report says plainly that stage 2's registered verdict stays "incomplete", and that the combined
  judgement rests on predictions registered before either run.
"""

from __future__ import annotations

import difflib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
STAGE2_DIR = HERE.parent / "qec-census-2"


def _load(name: str, path: Path):
    """A module from its file, registered under `name` (once per process)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stage2 = _load("qec_census_stage2", STAGE2_DIR / "study.py")
census, rules, distance = stage2.census, stage2.rules, stage2.distance

from lattice_lab.ledger import Ledger, record_lines  # noqa: E402
from lattice_lab.study import Study, StudyError, append_records, main  # noqa: E402

ID = census.STAGE2B_ID
PYTHON = ROOT / ".venv" / "bin" / "python"
RECORDS = HERE / "records.jsonl"
LEDGER = HERE / "ledger.jsonl"
STAGE2_LEDGER = STAGE2_DIR / "ledger.jsonl"
STAGE2_RECORDS = STAGE2_DIR / "records.jsonl"
CODE_CHANGE = HERE / "code_change.json"
# the files that differ from stage 2's registration, by its HASHED keys, and their sources
CHANGED = {"census_c": "census.c", "census_py": "census.py"}
CENSUS_FILES = {"census.c": census.CENSUS_C, "census.py": census.HERE / "census.py"}
# stage 1's files record these (data/*.jsonl headers)
STAGE1_CENSUS_C = "a9a3d730c46834dbe085f03dd612f0caebb919739a729aea91777e4a2bad8e9e"
STAGE1_CENSUS_PY = "5f652666feb0b2bc54b950235d43c01be747ee7ed535b58d0826161ed502c326"
PARTS = ("H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _name(ell: int, m: int) -> str:
    return f"{ell}x{m}"


# ---------------------------------------------------------------- stage 2's registered run


def stage2_ledger(path: Path | None = None) -> dict:
    """Stage 2's ledger, which must verify and hold its finished run: the question, the
    prediction entries by part, run_started, the observations and the verdict."""
    path = Path(path) if path is not None else STAGE2_LEDGER
    ledger = Ledger(path)
    if ledger.verify():
        raise StudyError(f"{path} does not verify: {ledger.verify()[:3]}")
    entries = ledger.entries
    kinds = [e["kind"] for e in entries]
    if not kinds or kinds[0] != "question" or kinds[-2:] != ["observations", "verdict"]:
        raise StudyError(f"{path} does not hold a finished run: {kinds}")
    if entries[0]["body"].get("id") != census.STAGE2_ID:
        raise StudyError(f"{path}'s question is not {census.STAGE2_ID}")
    return {
        "question": entries[0],
        "predictions": {e["body"]["part"]: e for e in entries if e["kind"] == "prediction"},
        "run_started": next(e for e in entries if e["kind"] == "run_started"),
        "observations": entries[-2],
        "verdict": entries[-1],
    }


def failed_rows(records: Path | None = None, ledger: dict | None = None) -> list[dict]:
    """Stage 2's error rows, read from its records file, each with its offset and sha256, which
    must be among the records its observations entry cites."""
    path = Path(records) if records is not None else STAGE2_RECORDS
    ledger = ledger or stage2_ledger()
    cited = {(r["offset"], r["sha256"]) for r in ledger["observations"]["body"]["records"]}
    out = []
    for offset, digest, line in record_lines(path):
        row = json.loads(line)
        if "error" not in row:
            continue
        if (offset, digest) not in cited:
            raise StudyError(f"{path}: the error row at {offset} is not in the observations")
        out.append({"offset": offset, "sha256": digest, "row": row})
    return out


def jobs(ledger: dict | None = None, failed: list[dict] | None = None) -> list[dict]:
    """The continuation's jobs: stage 2's registered specs (its protocol entry, verbatim) of the
    failed jobs, and of every registered job that waits on one of them (`after`, transitively),
    in stage 2's order."""
    ledger = ledger or stage2_ledger()
    failed = failed if failed is not None else failed_rows(ledger=ledger)
    registered = ledger["predictions"]["protocol"]["body"]["jobs"]
    keys = {f["row"]["key"] for f in failed}
    unknown = keys - {j["key"] for j in registered}
    if unknown:
        raise StudyError(f"error rows of jobs stage 2 did not register: {sorted(unknown)}")
    grew = True
    while grew:
        more = {j["key"] for j in registered if set(j.get("after", [])) & keys}
        grew = not more <= keys
        keys |= more
    return [j for j in registered if j["key"] in keys]


def tori(specs: list[dict] | None = None) -> list[tuple[int, int]]:
    """The tori of the continuation's jobs, the largest (lm) first."""
    specs = specs if specs is not None else jobs()
    return sorted({(j["l"], j["m"]) for j in specs}, key=lambda t: (-t[0] * t[1], t))


def fed(preds: dict, names: set[str]) -> dict[str, list[str]]:
    """The items of other tori that stage 2's decide judges from a record of one of `names`: an
    H2 item with a multiple > 1 or an H4 item from this run, whose odd torus is among them."""
    out = {"H2": [], "H4": []}
    for part in out:
        for name, want in preds[part]["body"]["predicted"].items():
            odd = _name(*want["odd_torus"])
            uses = want.get("multiple", 1) > 1 if part == "H2" else want["source"] == "this run"
            if name not in names and odd in names and uses:
                out[part].append(name)
    return out


# ---------------------------------------------------------------- the copied predictions


def _items(part: str, body: dict):
    """A prediction body's items: the dict or list that decide judges item by item."""
    return {"H5": "tori", "H6": "tori", "H7": "instances", "H8": "tori", "H9": "sizes"}.get(
        part, "predicted"
    )


def restrict(part: str, body: dict, names: set[str], law_keys: set[str]) -> dict:
    """A copy of a registered prediction body with its items restricted to the continuation's
    (`names`: its tori and the items they feed; `law_keys`: its H7 instances). Every value kept
    is the registered one; only the source entry's question hash goes (register writes the new
    question's), recorded as `source_question` by predictions()."""
    out = {k: v for k, v in body.items() if k != "question"}
    field = _items(part, body)
    items = body[field]
    if part == "H7":
        out[field] = [x for x in items if x["key"] in law_keys]
    elif part == "H9":
        out[field] = {n: at for n, at in items.items() if set(at["three"] + at["other"]) & names}
    elif isinstance(items, dict):
        out[field] = {k: v for k, v in items.items() if k in names}
    else:
        out[field] = [k for k in items if k in names]
    if part == "H8":
        out["excluded"] = [x for x in body["excluded"] if x["torus"] in names]
    return out


def item_count(part: str, body: dict) -> int:
    return len(body[_items(part, body)])


# ---------------------------------------------------------------- the code change


def code_change() -> dict:
    return json.loads(CODE_CHANGE.read_text())


def old_source(name: str, change: dict | None = None) -> str:
    """The file as stage 2 registered it (and, for census.c, as stage 1 ran it): the current
    file with code_change.json's patch reversed, each new text occurring exactly once."""
    change = change or code_change()
    text = Path(CENSUS_FILES[name]).read_text()
    for pair in change[name]["patch"]:
        if text.count(pair["new"]) != 1:
            raise StudyError(f"{name}: a patch's new text does not occur exactly once")
        text = text.replace(pair["new"], pair["old"])
    return text


def change_summary() -> dict:
    """For the question: each changed file's old and new sha256 (the old one checked against
    the reversed patch), its unified diff, and what the change is."""
    change = code_change()
    out = {}
    for name, entry in change.items():
        old, new = old_source(name, change), Path(CENSUS_FILES[name]).read_text()
        if hashlib.sha256(old.encode()).hexdigest() != entry["old_sha256"]:
            raise StudyError(f"{name}: the reversed patch does not give the registered file")
        if _sha256_file(CENSUS_FILES[name]) != entry["new_sha256"]:
            raise StudyError(f"{name} is not the file code_change.json describes")
        diff = difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            f"a/examples/qec-census/{name}",
            f"b/examples/qec-census/{name}",
        )
        out[name] = {
            "old_sha256": entry["old_sha256"],
            "new_sha256": entry["new_sha256"],
            "hunks": len(entry["patch"]),
            "diff": "".join(diff),
        }
    out["census.c"]["what"] = (
        "capacity only: MAXLM 128 -> 160, WORDS 4 -> 5 (2lm <= 320 bits), a static assertion "
        "that WORDS holds 2 MAXLM bits, the comment's 256 -> 320, and a refusal above MAXLM "
        "naming lm and MAXLM (exit 1, as before); the rank, the raw codes' order and the "
        "canonical form are unchanged"
    )
    out["census.py"]["what"] = (
        "Stage2Permit admits this study's job with this study's ledger and id (census.STAGE2B_*; "
        "stage2_registration_problem takes the ledger and id), ranks raises with census.c's "
        "message when it refuses, and the docstring says so; nothing else"
    )
    out["stage1"] = (
        f"stage 1's data headers record census.c {STAGE1_CENSUS_C[:8]}... (= stage 2's "
        f"registered census_c) and census.py {STAGE1_CENSUS_PY[:8]}...; the old and new census.c "
        "give byte-identical ranks on every raw code of the 116 stage-1 tori (development), so "
        "stage 1's k are the new census.c's; the tests check it on several tori, with the k "
        "counts of their headers and bb.k_linalg on samples"
    )
    return out


# ---------------------------------------------------------------- the registered code

HASHED = {
    **stage2.HASHED,
    "continuation_py": HERE / "study.py",
    "continuation_tests_py": ROOT / "tests" / "test_qec_census_2b.py",
    "code_change_json": CODE_CHANGE,
    "stage2_ledger": STAGE2_LEDGER,
    "stage2_records": STAGE2_RECORDS,
}


def code_hashes() -> dict[str, str]:
    return {key: _sha256_file(path) for key, path in HASHED.items()}


def _registration(ledger_path: Path | None = None) -> list[dict] | str:
    path = Path(ledger_path) if ledger_path is not None else census.STAGE2B_LEDGER
    if not path.is_file():
        return f"{path} does not exist: the continuation is not registered"
    entries = Ledger(path).entries
    if not entries or entries[0]["kind"] != "question":
        return f"{path} holds no question"
    return entries


def registered_code_problem(ledger_path: Path | None = None) -> str | None:
    """Why the pinned files (HASHED) are not those this registration hashed, or None."""
    entries = _registration(ledger_path)
    if isinstance(entries, str):
        return entries
    want, now = entries[0]["body"].get("sha256") or {}, code_hashes()
    changed = sorted(key for key in set(want) | set(now) if want.get(key) != now.get(key))
    if changed:
        return f"changed since the registration (or not hashed by it): {', '.join(changed)}"
    return None


def registered_jobs(ledger_path: Path | None = None) -> dict[str, dict]:
    """The continuation's registered jobs by key (its protocol entry)."""
    entries = _registration(ledger_path)
    if isinstance(entries, str):
        raise StudyError(entries)
    protocol = [e for e in entries if e["kind"] == "prediction" and e["body"].get("part")]
    protocol = [e for e in protocol if e["body"]["part"] == "protocol"]
    if len(protocol) != 1:
        raise StudyError("the continuation's ledger holds no protocol entry")
    return {j["key"]: j for j in protocol[0]["body"]["jobs"]}


# ---------------------------------------------------------------- running it


def job(spec: dict, records: str | None = None) -> dict:
    """Run one job and return its record, as stage 2's job does: inside a Stage2Permit (census.py
    grants it here only while this study's ledger holds its registration and a started run, for
    its registered tori), the pinned files must be those registered and the spec a registered
    job; then stage 2's own job code (stage2._dispatch) computes it."""
    path = Path(records) if records else RECORDS
    began = time.time()
    with census.Stage2Permit([(spec["l"], spec["m"])]):
        problem = registered_code_problem()
        if problem:
            raise StudyError(problem)
        if registered_jobs().get(spec["key"]) != spec:
            raise StudyError(f"{spec['key']} is not a registered job of the continuation")
        body = stage2._dispatch(spec, path)
    solver = {"solver": distance.scip_version(), "scip_fix": distance.SCIP_FIX}
    usage = stage2._usage()
    return {**spec, **body, **solver, "job_seconds": round(time.time() - began, 1), **usage}


WORKER = stage2.WORKER.replace('"qec_census_stage2"', '"qec_census_stage2b"')


def _run(spec: dict, path: Path) -> dict:
    """One job in its own worker process (stage 2's worker, loading this file); any failure is
    returned as an error row."""
    code = WORKER.format(path=str(HERE / "study.py"))
    timeout = stage2.TIMEOUTS[spec["test"]]
    try:
        out = subprocess.run(
            [str(PYTHON), "-c", code, json.dumps(spec), str(os.getpid()), str(path)],
            cwd=HERE,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if out.returncode:
            return {**spec, "error": out.stderr[-2000:]}
        return json.loads(out.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {**spec, "error": f"subprocess timeout after {timeout} s"}
    except Exception as exc:
        return {**spec, "error": f"{type(exc).__name__}: {exc}"}


def execute(path: Path, workers: int, run=None, window: float | None = None, clock=None) -> None:
    """Stage 2's scheduler (its execute) over the continuation's jobs: every job without a
    record in `path`, at most `workers` at a time, the first ready one in jobs() order whose
    timeout fits in the window (stage2._window(): QEC_CENSUS2_WINDOW, else 115 minutes); a
    StudyError, before the observations, when nothing more fits, so that resume continues. The
    real run (no `run` given) first refuses pinned files that differ from the registration."""
    path = Path(path)
    if run is None:
        problem = registered_code_problem()
        if problem:
            raise StudyError(problem)
    run = run or _run
    window = stage2._window() if window is None else window
    clock = clock or time.monotonic
    start = clock()

    def fits(spec: dict) -> bool:
        return window <= 0 or clock() - start + stage2.TIMEOUTS[spec["test"]] <= window

    done = set()
    if path.exists():
        data = path.read_bytes()
        if data and not data.endswith(b"\n"):
            cut = data.rfind(b"\n") + 1
            raise StudyError(
                f"{path} ends with an incomplete line at byte {cut}: truncate it to {cut} "
                "bytes, then resume"
            )
        done = {json.loads(line)["key"] for _, _, line in record_lines(path)}
    todo = [j for j in jobs() if j["key"] not in done]
    slots = max(1, workers)
    running = {}
    with ThreadPoolExecutor(slots) as pool:
        while todo or running:
            while len(running) < slots:
                ready = next(
                    (j for j in todo if all(a in done for a in j.get("after", [])) and fits(j)),
                    None,
                )
                if ready is None:
                    break
                todo.remove(ready)
                running[pool.submit(run, ready, path)] = ready
            if not running:
                if any(all(a in done for a in j.get("after", [])) for j in todo):
                    raise StudyError(
                        f"the window ends: {len(todo)} jobs left, none of whose timeouts fits in "
                        "what is left of it; resume continues"
                    )
                raise StudyError(f"jobs wait on records no job will write: {todo}")
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in finished:
                spec = running.pop(future)
                append_records(path, [future.result()])
                done.add(spec["key"])


# ---------------------------------------------------------------- the registration

VERDICT_RULE = (
    "the continuation's own verdict: stage 2's decide, unchanged, over this run's records and "
    "the copied predictions (stage 2's per-part rules and its verdict rule: fail when the "
    "instruments fail or a part fails; hold when every part holds or is not applicable, every "
    "registered job has a record, no job failed, and the pinned files are those registered "
    "here; incomplete otherwise); a part with no item here (H8, H9) is not applicable, unless "
    "stage 2's rules judge it failing"
)
COMBINED_RULE = (
    "a report beside the verdict, not a replacement for stage 2's: stage 2's decide over stage "
    "2's registered predictions and its registered run's records (its observations entry), each "
    "error row replaced by this run's record of that job; its overall outcome by stage 2's "
    "verdict rule, where the pinned-files condition is that the files differing from stage 2's "
    "registration are exactly census_c and census_py (this study's documented change) and every "
    "file is as this study registered it. Stage 2's registered verdict stays 'incomplete'."
)
EXCLUDED_SEEN = [
    "nothing was computed on any held-out torus: no rank, k, class or distance. Stage 2's run "
    "refused the 46 tori with lm >= 129 at census.c's size check (its error rows), which main() "
    "makes before either mode; before that, census.classes had only listed their raw parameters",
    "in development, once, the old census.c (MAXLM 128) was run as 'census k 3 43' to see its "
    "message: it exited at the same size check with 'census: size out of range' and computed "
    "nothing (3x43 is held out; this is the refusal stage 2's run recorded)",
    "the old and new census.c on every raw code of the 116 stage-1 tori census.py runs on "
    "(census_tori(), each through census.guard): byte-identical output, 5,472,121 codes, and "
    "the k counts equal to every stage-1 file header's raw_by_k",
    "the new census.c on 3x51 (lm = 153: k > 0 on 83,521 of 585,225 raw codes, max k 136 = "
    "8lm/9) and 2x80 (lm = 160: k = 0 throughout, by the lemma), with bb.k_linalg on 20 random "
    "raw codes of each; and 'census k 7 23' (lm = 161), refused with the new message. None of "
    "these is held out or isomorphic to a held-out torus (their orders exceed 150)",
    "arithmetic on stage 2's ledger and records: the error rows' keys, the registered specs and "
    "predictions, the items restricted to the failed tori",
    "tests/test_qec_census_2b.py: the patch reversed against the registered hashes; the old and "
    "new census.c on stage-1 tori (3x7, 6x6, 6x15, 3x33, 7x14) with bb.k_linalg samples; 3x51 "
    "against bb.k_linalg; the refusal at lm = 161; the registration, the permit, job, execute "
    "and decide with every computing primitive stubbed to raise (synthetic records, stage 2's "
    "real records)",
]
KNOWN_LIMITATIONS = [
    "the continuation's jobs run after stage 2's, on census.c with MAXLM 160 and census.py with "
    "the wider permit; the stage-2 code that computes (study.py, rules.py, the instruments) is "
    "the registered code, unchanged",
    "the continuation's own verdict covers its items only, and H7's registered threshold over "
    "its 8 instances is not stage 2's threshold over 15: the combined report judges H7 as "
    "registered",
    "the combined report is a report: the original registration's verdict is 'incomplete' and "
    "stays so; the combined judgement rests on predictions registered before either run",
    "search.c (distance.distance_search) holds k <= 128 logicals, census.c's new capacity "
    "does not change that, and stage 2's registered H2 bounds on some continuation tori exceed "
    "128 (130 on 3x49 and 7x21; 133 on 3x50, 5x30, 6x25 and 10x15; 3x51 just outside reaches "
    "136): a class with k > 128 has its searches (d2, and the law job's) recorded as instrument "
    "error runs ('beyond search.c's limits'), which H6 counts as unresolved, so H5 and H6 there "
    "would be unresolved and the verdict incomplete, not hidden",
    *stage2.KNOWN_LIMITATIONS,
]


def question() -> dict:
    ledger = stage2_ledger()
    failed = failed_rows(ledger=ledger)
    specs = jobs(ledger, failed)
    names = {_name(*t) for t in tori(specs)}
    preds = ledger["predictions"]
    keys = {j["key"] for j in specs}
    return {
        "id": ID,
        "title": "Stage 2 of the code census, continued: the jobs its run could not do "
        "(census.c's capacity), with the predictions stage 2 registered for them",
        "statement": "On the held-out tori with lm >= 129, stage 2's registered predictions H1 "
        "to H7 (copied verbatim, restricted to these tori and their 8 H7 instances) are tested "
        "by stage 2's own job code, now that census.c holds lm <= 160.",
        "continues": {
            "study": "examples/qec-census-2",
            "question": ledger["question"]["hash"],
            "run_started": ledger["run_started"]["hash"],
            "observations": ledger["observations"]["hash"],
            "verdict": ledger["verdict"]["hash"],
            "verdict_value": ledger["verdict"]["body"]["verdict"],
            "stays": "stage 2's registered verdict is 'incomplete' and stays so: this study "
            "neither edits its ledger or records nor replaces its verdict",
        },
        "reason": "census.c had #define MAXLM 128 (WORDS 4, 2lm <= 256 bits) and its 'k' command "
        "exits 1 above it, so stage 2's torus jobs on the 46 held-out tori with lm >= 129 and "
        "its 8 H7 jobs on those tori failed at census.classes, their first call after the "
        "guard; the error rows are in examples/qec-census-2/records.jsonl and its observations",
        "failed_jobs": [
            {
                "key": f["row"]["key"],
                "test": f["row"]["test"],
                "torus": _name(f["row"]["l"], f["row"]["m"]),
                "lm": f["row"]["l"] * f["row"]["m"],
                "records_offset": f["offset"],
                "sha256": f["sha256"],
                "error": f["row"]["error"].strip().splitlines()[-1][-300:],
            }
            for f in failed
        ],
        "jobs": [j["key"] for j in specs],
        "waiting_on_failed": sorted(keys - {f["row"]["key"] for f in failed}),
        "tori": [list(t) for t in tori(specs)],
        "fed": fed(preds, names),
        "no_computation_before": "nothing was computed on these tori before this registration: "
        "census.c's main() checks lm against MAXLM before entering either mode, and in stage 2's "
        "jobs census.classes reaches census.c before computing anything (it lists the raw "
        "parameters, index tuples from l and m, first); torus_record and law_record call it "
        "first after the guard, so the error left each job before any structure, search or "
        "program. Development ran the old census.c once on 3x43 (refused at the same check) and "
        "nothing else on a held-out torus (excluded_seen)",
        "code_change": change_summary(),
        "per_part_rules": "stage 2's decide (examples/qec-census-2/study.py, pinned), unchanged",
        "verdict_rule": VERDICT_RULE,
        "combined_rule": COMBINED_RULE,
        "sha256": code_hashes(),
        "excluded_seen": EXCLUDED_SEEN,
        "known_limitations": KNOWN_LIMITATIONS,
    }


def predictions() -> list[dict]:
    ledger = stage2_ledger()
    specs = jobs(ledger)
    names = {_name(*t) for t in tori(specs)}
    preds = ledger["predictions"]
    feeds = fed(preds, names)
    law_keys = {j["key"] for j in specs if j["test"] == "law"}
    out = []
    for part in PARTS:
        entry = preds[part]
        keep = names | set(feeds.get(part, []))
        body = restrict(part, entry["body"], keep, law_keys)
        out.append(
            {
                **body,
                "source_entry": {
                    "ledger": "examples/qec-census-2/ledger.jsonl",
                    "seq": entry["seq"],
                    "hash": entry["hash"],
                },
                "source_question": entry["body"]["question"],
                "copied": "verbatim from the source entry, its items restricted to the "
                "continuation's tori and H7 instances"
                + ("" if item_count(part, body) else " (none here: not applicable)"),
            }
        )
    source = preds["protocol"]
    out.append(
        {
            "part": "protocol",
            "kind": "the registered procedure of the continuation (not a prediction)",
            "jobs": specs,
            "sha256": code_hashes(),
            "verdict_rule": VERDICT_RULE,
            "per_part_verdict_rule": source["body"]["verdict_rule"],
            "combined_rule": COMBINED_RULE,
            "source_entry": {
                "ledger": "examples/qec-census-2/ledger.jsonl",
                "seq": source["seq"],
                "hash": source["hash"],
            },
        }
    )
    return out


# ---------------------------------------------------------------- the verdict


def _verdict(parts: dict, instruments: str, *blockers) -> str:
    """Stage 2's verdict rule over parts' outcomes: fail when the instruments fail or a part
    fails; hold when every part holds or is not applicable and nothing blocks (missing or failed
    jobs, changed files); incomplete otherwise."""
    if instruments == "fail" or "fails" in parts.values():
        return "fail"
    if all(v in ("holds", "not applicable") for v in parts.values()) and not any(blockers):
        return "hold"
    return "incomplete"


def _for_stage2(registered: list[dict]) -> list[dict]:
    """The copied predictions as stage 2's decide reads them: the protocol with the jobs, the
    hashes of stage 2's pinned files as registered here, and stage 2's verdict rule."""
    out = [p for p in registered if p["part"] != "protocol"]
    reg = next(p for p in registered if p["part"] == "protocol")
    sha = {key: reg["sha256"].get(key) for key in stage2.HASHED}
    out.append(
        {
            "part": "protocol",
            "jobs": reg["jobs"],
            "sha256": sha,
            "verdict_rule": reg["per_part_verdict_rule"],
        }
    )
    return out


def own_verdict(rows: list[dict], registered: list[dict]) -> dict:
    """Stage 2's decide over this run's records and the copied predictions; parts without items
    are not applicable (a 'fails' from stage 2's rules is kept); the pinned files checked
    against this registration."""
    preds = {p["part"]: p for p in registered}
    v = stage2.decide(rows, _for_stage2(registered))
    empty = [part for part in PARTS if not item_count(part, preds[part])]
    # an empty part is not applicable, unless stage 2's rules found it failing: that is kept
    parts = {
        p: ("not applicable" if p in empty and out != "fails" else out)
        for p, out in v["parts"].items()
    }
    want, now = preds["protocol"]["sha256"], code_hashes()
    changed = sorted(key for key in set(want) | set(now) if want.get(key) != now.get(key))
    blockers = (v["missing"], v["failed_jobs"], v["prior_failed"], changed)
    return {
        **v,
        "verdict": _verdict(parts, v["instruments"], *blockers),
        "parts": parts,
        "code_changed": changed,
        "not_applicable": empty,
        "verdict_rule": VERDICT_RULE,
    }


def combined(rows: list[dict], ledger: dict | None = None) -> dict:
    """The combined report (COMBINED_RULE)."""
    ledger = ledger or stage2_ledger()
    ours = {r.get("key") for r in rows}
    earlier = ledger["observations"]["body"]["rows"]
    kept = [r for r in earlier if not ("error" in r and r.get("key") in ours)]
    replaced = sorted(r["key"] for r in earlier if "error" in r and r.get("key") in ours)
    registered = [e["body"] for e in ledger["predictions"].values()]
    v = stage2.decide(kept + rows, registered)
    documented = sorted(CHANGED)
    unexplained = sorted(set(v["code_changed"]) - set(documented))
    problem = registered_code_problem()
    blockers = (v["missing"], v["failed_jobs"], v["prior_failed"], unexplained, problem)
    original = ledger["verdict"]
    return {
        "outcome": _verdict(v["parts"], v["instruments"], *blockers),
        "parts": v["parts"],
        "instruments": v["instruments"],
        "missing": v["missing"],
        "failed_jobs": v["failed_jobs"],
        "prior_failed": v["prior_failed"],
        "duplicates": v["duplicates"],
        "protocol_failures": v["protocol_failures"],
        "records": {
            "stage2": len(kept),
            "continuation": len(rows),
            "replaced_error_rows": replaced,
        },
        "code_changed_since_stage2_registration": v["code_changed"],
        "documented_change": documented,
        "unexplained_change": unexplained,
        "registered_code_problem": problem,
        "original": {
            "verdict": original["body"]["verdict"],
            "verdict_entry": original["hash"],
            "parts": original["body"]["parts"],
        },
        "statement": "Stage 2's registered verdict is "
        f"'{original['body']['verdict']}' (its ledger's verdict entry {original['hash'][:12]}...) "
        "and stays so: this combined judgement does not replace it. It judges each stage-2 part "
        "by stage 2's registered rules over stage 2's successful records and this continuation's "
        "records, and every prediction it judges by was registered before either run (stage 2's "
        "prediction entries; this continuation copies those of the failed items verbatim).",
        "rule": COMBINED_RULE,
        "detail": v["detail"],
    }


def decide(rows: list[dict], registered: list[dict]) -> dict:
    own = own_verdict(rows, registered)
    return {
        **own,
        "combined": combined(rows),
        "known_limitations": KNOWN_LIMITATIONS,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
