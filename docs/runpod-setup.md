# Running stage 3c (and the spot-check) on RunPod CPU pods

Stage 3c (`examples/qec-census-3c`) was stopped on 2026-10-28 after 24 of its 49 tori, because
the cloud session's container kept restarting. Each restart threw away the torus in progress: 2 x 75
lost about 23 hours twice. This note moves the run to a pod that stays up. Nothing about the
study changes: it is the same code, the same settings and `--workers 4`. The run resumes from the
committed records with `study.py resume`, which starts 2 x 75 again from the beginning.

## The automated route (what Claude runs)

Two scripts in `examples/qec-census-3c/runpod/` do everything below without a shell on the pod:

- `launch.py` creates, lists, inspects, stops and deletes the pod through RunPod's REST API. It
  only touches pods named `lattice-lab-census-3c`, so other pods on the account are left alone.
- `pod-run.sh` runs on the pod at every start. It does steps 1–6 below: packages, venv,
  self-test, hardware record, `resume --workers 4`, and committing records as they arrive. A pod
  restart resumes the run by itself.

What it needs from you, once:

1. **A RunPod secret named `lattice_lab_github_token`** (RunPod console → Secrets) holding a
   fine-grained GitHub token for **PolyLabs-research/lattice-lab** only, with *Contents: read and
   write*. RunPod substitutes it into the pod as `GH_TOKEN` when the pod boots
   (`{{ RUNPOD_SECRET_lattice_lab_github_token }}`). It never passes through the Claude session.
2. **RunPod API access in the Claude environment**: `rest.runpod.io` allowed, and the RunPod
   API key as an environment variable `RUNPOD_API_KEY` (or a network secret for that host).
   Both take effect in a new session.

Then, in a session on this branch:

```bash
python3 examples/qec-census-3c/runpod/launch.py create        # prints the pod id
python3 examples/qec-census-3c/runpod/launch.py status POD_ID
```

Progress shows up on the branch: `examples/qec-census-3c/runpod-status.txt` holds the phase
(`selftest`, `running`, `done` or `failed`), the torus in progress and the record count, and it is
committed each time the torus changes. Records and ledger entries are committed within 2 minutes
of being written. The pod's log (`/workspace/pod-run.log`) is also the container output, so the RunPod
console's log view shows it; the census's own log stays on the volume (`/workspace/s3c-run.log`). When the status says
`done`, the pod idles until `launch.py stop` (or `delete`) ends the billing.

The manual steps below do the same thing by hand.

## The pod

| Setting | Choice | Why |
|---|---|---|
| Type | **CPU Pod** (no GPU) | Nothing here uses a GPU. |
| Tier | **Compute-optimized** | Each exact search is single-threaded C against a 30-minute wall-clock limit, so per-core speed matters. |
| Size | **8 vCPU, 16 GB RAM** (4 vCPU / 8 GB is enough for the census alone) | The census uses 4 cores (`--workers 4`, as registered); the other 4 run the spot-check. The census needs about 1–2 GB. |
| Billing | **On-demand, Secure Cloud** (not spot or interruptible) | A pre-empted pod brings back the restart problem. |
| Image | Ubuntu 24.04 base (any recent Ubuntu with `apt`) | |
| Storage | Container disk, 20 GB | RunPod gives CPU pods no pod volume, so a restart starts from a fresh clone. The records survive because they are pushed within 2 minutes. |

## 1. Packages, and keeping everything on the volume

```bash
apt-get update && apt-get install -y build-essential git tmux curl zlib1g-dev
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.local/bin/env

# uv's cache and its Python install on the volume, so a restart keeps them
cat >> ~/.bashrc <<'EOF'
export UV_CACHE_DIR=/workspace/.uv-cache
export UV_PYTHON_INSTALL_DIR=/workspace/.uv-python
export SPOTCHECK_TOOLS=/workspace/tools
export DISTQLDPC=/workspace/tools/DistQLDPC
EOF
source ~/.bashrc
```

After a pod restart, `~/.bashrc` and `~/.local` are gone (they sit on the container disk). Re-run
this step; it takes a minute. Everything under `/workspace` stays.

## 2. The repository

lattice-lab is private. Create a fine-grained GitHub token limited to **PolyLabs-research/lattice-lab**
with *Contents: read and write*, and use it only on this pod.

```bash
cd /workspace
git clone --branch ccr-ab9f0bb1-qb20sx \
  https://x-access-token:<TOKEN>@github.com/PolyLabs-research/lattice-lab.git
cd lattice-lab
git config user.name "<your name>" && git config user.email "<your email>"
git log --oneline -1    # 342e15a Census stage 3c: resumed after a fourth container restart ...

uv python install 3.13
uv sync --group dev --group qec   # numpy, scipy, kepler and latticelife at their pinned commits, pytest, pyscipopt
```

The token sits in `.git/config` on the volume. Revoke it when the run is done.

## 3. Self-test (about 2 minutes)

```bash
uv run --no-sync pytest -q tests/test_qec_census_3c.py tests/test_qec_census_3b.py
wc -l examples/qec-census-3c/records.jsonl    # 24
uv run --no-sync python -c "import importlib.util as u; s = u.spec_from_file_location('c', 'examples/qec-census-3c/study.py'); c = u.module_from_spec(s); s.loader.exec_module(c); print(c.consistency())"
# must print [] : the code, stage 3b's cited records and the tori are as registered
```

Both test files must pass. They compute only on stage-1 tori and synthetic values, never on a
held-out torus. The last command is the same check the run makes before it starts. If anything
fails, stop and tell me before resuming.

## 4. Record the hardware (once, before resuming)

The search limit is wall-clock time. On a faster CPU some searches that timed out in the cloud
session may finish, so the write-up has to say which records came from which machine. Commit
this first:

```bash
{ date -u; nproc; lscpu | grep -E 'Model name|MHz|Thread|Core|Socket'; free -g | head -2; cc --version | head -1; } \
  > examples/qec-census-3c/hardware-runpod.txt
git add examples/qec-census-3c/hardware-runpod.txt
git commit -m "Census stage 3c: hardware of the RunPod machine the run resumes on"
git push -u origin ccr-ab9f0bb1-qb20sx
```

## 5. Resume the run

```bash
tmux new -s census
cd /workspace/lattice-lab
.venv/bin/python -u examples/qec-census-3c/study.py resume --workers 4 2>&1 | tee -a /workspace/s3c-run.log
# detach with Ctrl-b d; reattach with: tmux attach -t census
```

`resume` adds a `run_resumed` entry to the ledger. The auto-commit script below picks it up with
the records.

## 6. Commit records as they arrive

In a second tmux window (`Ctrl-b c`):

```bash
cd /workspace/lattice-lab
while true; do
  if ! git diff --quiet -- examples/qec-census-3c/records.jsonl examples/qec-census-3c/ledger.jsonl; then
    n=$(wc -l < examples/qec-census-3c/records.jsonl)
    git add examples/qec-census-3c/records.jsonl examples/qec-census-3c/ledger.jsonl
    git commit -q -m "Census stage 3c: records ($n tori)"
    for t in 2 4 8 16; do git push -q -u origin ccr-ab9f0bb1-qb20sx && break; sleep $t; done
  fi
  sleep 120
done
```

It also catches the observations and verdict entries the run writes to the ledger when it
finishes. `examples/qec-census-3c/records.one` is a temporary file of the run's own; it is in
`.gitignore`.

## 7. If the pod restarts

A pod restart keeps `/workspace` but kills both processes, and the torus in progress starts over.
Repeat step 1's environment lines, then steps 5 and 6. Don't run step 4 again unless the hardware
changed; if it did, commit a second file.

## 8. Checking on it

- `tmux attach -t census` shows the run's log: one line per torus as it starts.
- `wc -l examples/qec-census-3c/records.jsonl` gives the tori done (24 at the start, 49 at the end).
- The run is finished when `study.py` prints a verdict and exits. The ledger then ends with the
  observations and verdict entries, which step 6 commits.
- Tell me (or start a session pointed at the branch) and I'll check the records, judge them and
  write up stage 3b/3c, disclosing the cloud restarts and the move.

## 9. The spot-check on the spare cores

The spot-check (`docs/census-stage3b-spotcheck-plan.md`) needs three tools built from source, at
the commits the plan was validated with.

```bash
mkdir -p /workspace/tools && cd /workspace/tools
git clone https://github.com/arminbiere/cadical && (cd cadical && git checkout c60730422e758ef1cebe7aeddf2dda31c996bf04 && ./configure && make -j4)
git clone https://github.com/marijnheule/drat-trim && (cd drat-trim && git checkout 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 && make)
git clone https://github.com/guluchen/DistQLDPC && (cd DistQLDPC && git checkout e52d15baa7a430104329d20467c12375fe60f0f2 && make -j4)

cd /workspace/lattice-lab
uv run --no-sync pytest -q tests/test_qec_census_3b_spotcheck.py   # 13 tests; skipped if the tools are missing
```

`sat.py` reads the tools from `$SPOTCHECK_TOOLS` and `distq.py` from `$DISTQLDPC`, which step 1
sets. The runner is `examples/qec-census-3b/spotcheck/run.py` (`sample`, `run --workers N`,
`judge`).

The spot-check gets a pod of its own, after the census finished:

```bash
python3 examples/qec-census-3c/runpod/launch.py create --job spotcheck   # 32 vCPU, 400 GB disk
```

That pod runs `examples/qec-census-3b/spotcheck/pod-run.sh`. It builds the three tools, runs the
spot-check tests (every check once on [[72,12,6]]), records the hardware and tool commits, and
then runs `run.py run` on every core. It commits `spotcheck/records.jsonl` and
`spotcheck/runpod-status.txt` every 5 minutes, and `spotcheck/judge.json` at the end.
