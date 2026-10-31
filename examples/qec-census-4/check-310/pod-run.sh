#!/usr/bin/env bash
# The long rerun of the [[310,10,22]] check (launch.py --job check-310): the unpruned search (C2),
# both SAT claims (C6, w = 21 and w = 20) and DistQLDPC (C5) with 24-hour limits, into
# examples/qec-census-4/check-310/records-long.jsonl. A restart resumes (check.py skips done jobs).
set -uo pipefail

W=/workspace
R=$W/lattice-lab
D=examples/qec-census-4/check-310
BRANCH=ccr-ab9f0bb1-qb20sx
STATUS=$D/runpod-status.txt
RUNLOG=$W/check-run.log
REC=records-long.jsonl
exec > >(tee -a "$W/pod-run.log") 2>&1
echo "=== pod start $(date -u +%FT%TZ) pod=${RUNPOD_POD_ID:-?}"

export DEBIAN_FRONTEND=noninteractive
export UV_CACHE_DIR=$W/.uv-cache UV_PYTHON_INSTALL_DIR=$W/.uv-python UV_INSTALL_DIR=$W/.uv-bin
export PATH=$W/.uv-bin:$PATH
export DISTQLDPC=$W/tools/DistQLDPC
mkdir -p "$W/tools"

cd "$R" || exit 1
git config user.name "${POD_GIT_NAME:-lattice-lab census pod}"
git config user.email "${POD_GIT_EMAIL:-census-pod@users.noreply.github.com}"

push() {
  for t in 2 4 8 16; do
    git push -q -u origin "$BRANCH" && return 0
    # a merge, not a rebase: it leaves the files study.py is appending to untouched (no stash),
    # since nothing else commits to examples/qec-census-3d
    git pull -q --no-rebase --no-edit origin "$BRANCH" || git merge --abort 2>/dev/null
    sleep "$t"
  done
  echo "PUSH FAILED: commits stay on the pod until the next successful push"; return 1
}

commit() {  # commit the given paths if they changed (whole lines only), then push
  local msg=$1 f paths=(); shift
  for f in "$@"; do
    [ -e "$f" ] || continue
    [ -s "$f" ] && [ "$(tail -c1 "$f" | od -An -c | tr -d ' ')" != '\n' ] && return 0
    paths+=("$f")
  done
  [ ${#paths[@]} -gt 0 ] || return 0
  git add -- "${paths[@]}"
  if ! git diff --cached --quiet; then
    git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01LBDpbJNXFaJgMYrZEKJamq"
    push
  fi
}

records() { if [ -f "$D/$REC" ]; then wc -l < "$D/$REC"; else echo 0; fi; }
last_kind() { tail -1 "$D/ledger.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["kind"])'; }

status() {
  {
    echo "phase: $1"
    echo "detail: ${2:-}"
    echo "updated: $(date -u +%FT%TZ)"
    echo "pod: ${RUNPOD_POD_ID:-?}"
    echo "records: $(records) of 6 jobs"
  } > "$STATUS"
  commit "Check of [[310,10,22]]: pod status ($1)" "$STATUS"
}

hold() { echo "holding: $1"; sleep infinity; }

apt-get update -q && apt-get install -yq build-essential git curl zlib1g-dev ca-certificates python3 procps \
  || { echo "apt failed"; hold "apt"; }
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
command -v uv >/dev/null || { status failed "uv did not install"; hold "uv"; }

git fetch -q origin "$BRANCH" && [ -n "$(git log "origin/$BRANCH..HEAD" --oneline)" ] && push

export SPOTCHECK_TOOLS=$W/tools TMPDIR=$W/tmp
mkdir -p "$TMPDIR"


# 1. the tools: DistQLDPC at the census's commit, CaDiCaL and drat-trim at the spot-check's
build() {  # name url commit make-command
  local name=$1 url=$2 rev=$3 cmd=$4
  [ -d "$W/tools/$name/.git" ] || git clone -q "$url" "$W/tools/$name" || return 1
  git -C "$W/tools/$name" checkout -q "$rev" || return 1
  (cd "$W/tools/$name" && bash -c "$cmd") > "$W/build-$name.log" 2>&1
}
status building "DistQLDPC, CaDiCaL, drat-trim"
[ -x "$DISTQLDPC/bin/distqldpc" ] || build DistQLDPC https://github.com/guluchen/DistQLDPC \
  "$DQ_COMMIT" "make -j$(nproc)" || { status failed "DistQLDPC build"; hold "distqldpc"; }
[ -x "$W/tools/cadical/build/cadical" ] || build cadical https://github.com/arminbiere/cadical \
  c60730422e758ef1cebe7aeddf2dda31c996bf04 "./configure && make -j$(nproc)" \
  || { status failed "CaDiCaL build"; hold "cadical"; }
[ -x "$W/tools/drat-trim/drat-trim" ] || build drat-trim https://github.com/marijnheule/drat-trim \
  2e3b2dc0ecf938addbd779d42877b6ed69d9a985 "make" || { status failed "drat-trim build"; hold "drat-trim"; }

# 2. the venv and the self-test (the spot-check's tests: SAT encoding against enumeration,
#    every instrument once on [[72,12,6]])
uv python install 3.13 && uv sync --frozen --group dev --group qec || { status failed "uv sync"; hold "sync"; }
status selftest
if ! uv run --no-sync pytest -q -rs tests/test_qec_census_3b_spotcheck.py tests/test_qec_census_3b_spotcheck_run.py > "$W/selftest.log" 2>&1; then
  cat "$W/selftest.log"; status failed "the spot-check tests failed"; hold "tests"
fi
grep -q SKIPPED "$W/selftest.log" && { status failed "a test was skipped"; hold "skips"; }
{ date -u +%FT%TZ; echo "pod: ${RUNPOD_POD_ID:-?}"; nproc; lscpu | grep -E 'Model name|MHz'; free -g | head -2
  for t in DistQLDPC cadical drat-trim; do echo "$t $(git -C "$W/tools/$t" rev-parse HEAD)"; done; } > "$D/hardware-runpod.txt"
commit "Check of [[310,10,22]]: hardware and tools of the RunPod machine" "$D/hardware-runpod.txt"

# 3. the long rerun, committing records as they arrive
run=""
on_stop() {
  commit "Check of [[310,10,22]]: records ($(records) jobs), pod stopping" "$D/$REC"
  [ -n "$run" ] && kill "$run" 2>/dev/null; exit 0
}
trap on_stop TERM INT
status running "check.py --limit 86400 --only C2,C6,C5"
.venv/bin/python -u "$D/check.py" --limit 86400 --workers 6 --only C2,C6,C5 --out "$D/$REC" >> "$RUNLOG" 2>&1 &
run=$!
while kill -0 "$run" 2>/dev/null; do
  sleep 300 & wait $!
  commit "Check of [[310,10,22]]: records ($(records) jobs)" "$D/$REC"
  status running "check.py --limit 86400; last: $(tail -1 "$RUNLOG" | cut -c1-120)"
done
wait "$run"; code=$?
run=""
commit "Check of [[310,10,22]]: records ($(records) jobs), run ended" "$D/$REC"
status done "check.py exited with $code"
hold "end"
