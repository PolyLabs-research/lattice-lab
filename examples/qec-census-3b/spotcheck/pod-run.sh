#!/usr/bin/env bash
# The stage 3b/3c spot-check on a RunPod CPU pod (docs/runpod-setup.md, section 9). The pod's
# start command (examples/qec-census-3c/runpod/launch.py --job spotcheck) clones the branch and
# runs this script, at every start; a restart resumes from the committed records. Each step is
# safe to repeat.
#
#  1. packages, uv, and the tools: CaDiCaL and drat-trim at the commits the encoding was tested
#     with; DistQLDPC at its head when first cloned (the plan), recorded in distqldpc-commit.txt
#     and checked out again at every later start
#  2. the venv (uv sync --frozen, with pyscipopt)
#  3. self-test: the spot-check tests, every check once on [[72,12,6]]
#  4. the hardware and tool commits, committed once per machine
#  5. run.py run --workers $(nproc), with records committed as they arrive; then run.py judge
#
# run.py appends to /workspace/spotcheck-records.jsonl, outside the repository; whole lines of
# it are copied into spotcheck/records.jsonl before each commit, so a rebase never meets a file
# being written. Progress is pushed to the branch: spotcheck/records.jsonl and
# spotcheck/runpod-status.txt.
set -uo pipefail

W=/workspace
R=$W/lattice-lab
D=examples/qec-census-3b/spotcheck
BRANCH=ccr-ab9f0bb1-qb20sx
STATUS=$D/runpod-status.txt
RUNLOG=$W/spotcheck-run.log
RUNREC=$W/spotcheck-records.jsonl
MIN_DISK_GB=${SPOTCHECK_MIN_DISK_GB:-120}  # 3 SAT claims at ~27 GB of binary proof each
T=$W/tools
exec > >(tee -a "$W/pod-run.log") 2>&1
echo "=== pod start $(date -u +%FT%TZ) pod=${RUNPOD_POD_ID:-?}"

export DEBIAN_FRONTEND=noninteractive
export UV_CACHE_DIR=$W/.uv-cache UV_PYTHON_INSTALL_DIR=$W/.uv-python UV_INSTALL_DIR=$W/.uv-bin
export PATH=$W/.uv-bin:$PATH
export SPOTCHECK_TOOLS=$T DISTQLDPC=$T/DistQLDPC
export TMPDIR=$W/tmp  # DRAT proofs are written here; the container disk is sized for them
mkdir -p "$TMPDIR" "$T"

cd "$R" || exit 1
git config user.name "${POD_GIT_NAME:-lattice-lab spot-check pod}"
git config user.email "${POD_GIT_EMAIL:-census-pod@users.noreply.github.com}"

push() {  # after a refused push, rebase onto the branch: the pod's commits touch only its own files
  for t in 2 4 8 16; do
    git push -q -u origin "$BRANCH" && return 0
    git pull -q --rebase --autostash origin "$BRANCH" || git rebase --abort 2>/dev/null
    sleep "$t"
  done
  echo "PUSH FAILED: commits stay on the pod until the next successful push"; return 1
}

commit() {  # commit the given paths if they changed, then push
  local msg=$1 f; shift
  for f in "$@"; do  # a file being appended to is committed only once it ends in a whole line
    [ -s "$f" ] && [ "$(tail -c1 "$f" | od -An -c | tr -d ' ')" != '\n' ] && return 0
  done
  git add -- "$@"
  if ! git diff --cached --quiet; then
    git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01LBDpbJNXFaJgMYrZEKJamq"
    push
  fi
}

records() { if [ -f "$D/records.jsonl" ]; then wc -l < "$D/records.jsonl"; else echo 0; fi; }

sync_records() {  # the whole lines of run.py's file into the repository's copy
  [ -f "$RUNREC" ] || return 0
  python3 -c 'import sys; b = open(sys.argv[1], "rb").read(); open(sys.argv[2], "wb").write(b[:b.rfind(b"\n") + 1])' \
    "$RUNREC" "$D/records.jsonl"
}

count() { local c; c=$(grep -c "$1" "$RUNLOG" 2>/dev/null); echo "${c:-0}"; }

status() {  # phase [detail]: write and commit runpod-status.txt
  {
    echo "phase: $1"
    echo "detail: ${2:-}"
    echo "updated: $(date -u +%FT%TZ)"
    echo "pod: ${RUNPOD_POD_ID:-?}"
    echo "records: $(records)"
    echo "log: $(count '^start ') started, $(count '^done ') done, $(count '^died ') died (all starts on this disk)"
    echo "disk: $(df -h --output=used,avail "$W" 2>/dev/null | tail -1)"
  } > "$STATUS"
  commit "Spot-check: pod status ($1)" "$STATUS"
}

hold() { echo "holding: $1"; sleep infinity; }

py() { uv run --no-sync python "$@"; }

# 1. packages, uv and the tools
apt-get update -q && apt-get install -yq build-essential git curl zlib1g-dev ca-certificates python3 procps \
  || { echo "apt failed"; hold "apt"; }
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
command -v uv >/dev/null || { status failed "uv did not install"; hold "uv"; }

git fetch -q origin "$BRANCH" && [ -n "$(git log "origin/$BRANCH..HEAD" --oneline)" ] && push

# leftovers of jobs killed by an earlier stop (proofs, compiled programs)
rm -rf "$TMPDIR"/spotcheck-* "$TMPDIR"/qec-parts-* 2>/dev/null
avail=$(df -BG --output=avail "$TMPDIR" | tail -1 | tr -dc 0-9)
if [ "${avail:-0}" -lt "$MIN_DISK_GB" ]; then
  status failed "only ${avail}G free under $TMPDIR (need ${MIN_DISK_GB}G for the DRAT proofs)"
  hold "disk"
fi

build() {  # name url commit(or "") make-command
  local name=$1 url=$2 rev=$3 cmd=$4
  [ -d "$T/$name/.git" ] || git clone -q "$url" "$T/$name" || return 1
  [ -z "$rev" ] || git -C "$T/$name" checkout -q "$rev" || return 1
  (cd "$T/$name" && bash -c "$cmd") > "$W/build-$name.log" 2>&1
}
status building "CaDiCaL, drat-trim, DistQLDPC"
[ -x "$T/cadical/build/cadical" ] || build cadical https://github.com/arminbiere/cadical \
  c60730422e758ef1cebe7aeddf2dda31c996bf04 "./configure && make -j$(nproc)" \
  || { status failed "CaDiCaL build"; hold "cadical"; }
[ -x "$T/drat-trim/drat-trim" ] || build drat-trim https://github.com/marijnheule/drat-trim \
  2e3b2dc0ecf938addbd779d42877b6ed69d9a985 "make" \
  || { status failed "drat-trim build"; hold "drat-trim"; }
DQ_PIN=$D/distqldpc-commit.txt
dq_rev=$(cat "$DQ_PIN" 2>/dev/null || true)
[ -x "$T/DistQLDPC/bin/distqldpc" ] || build DistQLDPC https://github.com/guluchen/DistQLDPC \
  "$dq_rev" "make -j$(nproc)" \
  || { status failed "DistQLDPC build (see /workspace/build-DistQLDPC.log)"; hold "distqldpc"; }
if [ -z "$dq_rev" ]; then
  git -C "$T/DistQLDPC" rev-parse HEAD > "$DQ_PIN"
  commit "Spot-check: DistQLDPC commit, cloned at the first start" "$DQ_PIN"
fi

# 2. the venv
uv python install 3.13 && uv sync --frozen --group dev --group qec \
  || { status failed "uv sync"; hold "sync"; }

# 3. self-test (the runner's tests run every check on [[72,12,6]], at its d and a wrong one)
status selftest
if ! uv run --no-sync pytest -q tests/test_qec_census_3b_spotcheck.py tests/test_qec_census_3b_spotcheck_run.py; then
  status failed "the spot-check tests failed (see /workspace/pod-run.log)"
  hold "tests"
fi
skipped=$(uv run --no-sync pytest -q -rs tests/test_qec_census_3b_spotcheck_run.py 2>&1 | grep -c SKIPPED)
[ "$skipped" = 0 ] || { status failed "$skipped runner tests skipped: tools missing"; hold "skips"; }

# 4. the hardware and the tool commits
hw=$(mktemp)
{ nproc; lscpu | grep -E 'Model name|MHz|Thread|Core|Socket'; free -g | head -2; cc --version | head -1
  for t in cadical drat-trim DistQLDPC; do echo "$t $(git -C "$T/$t" rev-parse HEAD)"; done; } > "$hw"
model=$(grep 'Model name' "$hw")
[ -n "$model" ] || model="nproc $(nproc) $(uname -m)"
if ! grep -qlF "$model" "$D"/hardware-runpod*.txt 2>/dev/null; then
  out=$D/hardware-runpod.txt
  [ -e "$out" ] && out=$D/hardware-runpod-$(date -u +%Y%m%dT%H%M).txt
  { date -u +%FT%TZ; echo "pod: ${RUNPOD_POD_ID:-?}"; cat "$hw"; } > "$out"
  commit "Spot-check: hardware and tool commits of the RunPod machine" "$out"
fi

# 5. run, committing records as they arrive (run.py again, up to 3 times, if it fails)
[ -f "$RUNREC" ] || { [ -f "$D/records.jsonl" ] && cp "$D/records.jsonl" "$RUNREC"; }
workers=${SPOTCHECK_WORKERS:-$(nproc)}
run=""
on_stop() {  # a pod stop: run.py ends its jobs' process groups; commit what is written
  [ -n "$run" ] && kill -TERM "$run" 2>/dev/null
  sync_records
  commit "Spot-check: records ($(records) jobs), pod stopping" "$D/records.jsonl"
  exit 0
}
trap on_stop TERM INT
code=1
for attempt in 1 2 3; do
  status running "run.py run --workers $workers (attempt $attempt)"
  .venv/bin/python -u "$D/run.py" run --workers "$workers" --out "$RUNREC" >> "$RUNLOG" 2>&1 &
  run=$!
  while kill -0 "$run" 2>/dev/null; do
    sleep 300 & wait $!
    sync_records
    [ -f "$D/records.jsonl" ] && commit "Spot-check: records ($(records) jobs)" "$D/records.jsonl"
    status running "run.py run --workers $workers (attempt $attempt)"
  done
  wait "$run"; code=$?
  run=""
  sync_records
  [ -f "$D/records.jsonl" ] && commit "Spot-check: records ($(records) jobs), run ended" "$D/records.jsonl"
  [ "$code" = 0 ] && break
  echo "run.py exited with $code (attempt $attempt)"
done
if [ "$code" = 0 ]; then
  if .venv/bin/python "$D/run.py" judge --out "$D/records.jsonl" > "$W/judge.json" 2>> "$RUNLOG"; then
    cp "$W/judge.json" "$D/judge.json"
    commit "Spot-check: judged" "$D/judge.json"
    status done "run.py exited 0; see judge.json"
  else
    status failed "run.py judge failed (see /workspace/spotcheck-run.log)"
  fi
else
  status failed "run.py exited with $code three times (see /workspace/spotcheck-run.log)"
fi
hold "end"
