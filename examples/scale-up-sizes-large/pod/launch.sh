#!/usr/bin/env bash
# Run part 2 of the scale-up test (sides 2048 and 4096) on a rented CPU pod, from the lab's own
# machine: rent the pod, check its speed, start the registered run there, bring the ledger and
# the records back as they grow, and delete the pod when the verdict is in, when anything
# fails, or ten minutes before the deadline. Started detached, so it does not depend on the
# session that started it:
#
#   systemd-run --user --unit=sizes-large --collect \
#       bash examples/scale-up-sizes-large/pod/launch.sh HOURS MAX_RATE
#   e.g. HOURS 6 and MAX_RATE 1.12 (cpu5c, 32 vCPUs): $6.72 at most
#
# The log and the pulled files go to ~/lattice-lab-runs/sizes-large/. Nothing in the repository
# is changed: when the run is done, copy pulled/ledger.jsonl and pulled/records.jsonl into
# examples/scale-up-sizes-large/, verify, and commit. The pod's own deadline and the sweeper
# timer on this machine cap the cost whatever happens to this script.
set -u
HOURS=${1:?hours}
MAX_RATE=${2:?the confirmed ceiling in dollars an hour}
VCPU=${VCPU:-32}
WORKERS=${WORKERS:-14}  # a run at side 4096 holds 3 GB, and 32 vCPUs are 16 cores with 64 GB
FLAVOR=${FLAVOR:-cpu5c}
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
D=examples/scale-up-sizes-large
OUT=$HOME/lattice-lab-runs/sizes-large
mkdir -p "$OUT/pulled"
exec >> "$OUT/launch.log" 2>&1
CHESS=$HOME/Documents/dev/chess
RP=("$CHESS/.venv/bin/python" "$CHESS/scripts/runpod_pod.py")
PY=$REPO/.venv/bin/python
say() { echo "$(date -Is) $*"; }
cd "$REPO" || exit 1

# the pod clones from GitHub, so what runs there must be what is pushed, and still unrun
BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT=$(git rev-parse HEAD)
git fetch -q origin "$BRANCH"
[ "$(git rev-parse "origin/$BRANCH")" = "$COMMIT" ] || { say "HEAD is not what origin/$BRANCH holds"; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || { say "the tree has uncommitted changes"; exit 1; }
[ "$(tail -1 "$D/ledger.jsonl" | "$PY" -c 'import json, sys; print(json.loads(sys.stdin.read())["kind"])')" = prediction ] \
  || { say "the ledger does not end with the registration"; exit 1; }
[ ! -e "$D/records.jsonl" ] || { say "there are records already"; exit 1; }

say "launch: $FLAVOR, $VCPU vCPUs, $HOURS h cap, at most \$$MAX_RATE/h; $BRANCH at ${COMMIT:0:8}; $WORKERS workers"
out=$("$PY" "$D/pod/cpu_pod.py" --flavor "$FLAVOR" --vcpu "$VCPU" --hours "$HOURS" --max-rate "$MAX_RATE" --yes 2>&1)
echo "$out"
POD=$(echo "$out" | sed -n 's/^launched \([a-z0-9]*\) .*/\1/p')
DEADLINE=$(echo "$out" | sed -n 's/^launched [a-z0-9]* taz-[a-z0-9_-]*-dl\([0-9]*\) .*/\1/p')
[ -n "$POD" ] && [ -n "$DEADLINE" ] || { say "no pod launched; stopping"; exit 1; }

SSH=()
pull() {  # whatever the pod has so far; a file that is not there yet is skipped
    [ ${#SSH[@]} -gt 0 ] || return 0
    local rsh="${SSH[*]:0:${#SSH[@]}-1}" host=${SSH[-1]} f
    for f in "lattice-lab/$D/records.jsonl" "lattice-lab/$D/ledger.jsonl" pod-run.log hardware.txt verdict.json STATE; do
        rsync -a -e "$rsh" "$host:/root/run/$f" "$OUT/pulled/" 2> /dev/null
    done
}
terminate() {
    for _ in 1 2 3 4 5 6; do
        "${RP[@]}" terminate "$POD" && { say "terminated $POD"; return 0; }
        sleep 30
    done
    say "COULD NOT TERMINATE $POD: its own deadline and the sweeper remain"
    return 1
}
fail() {
    say "FAILED: $*"
    pull
    terminate
    notify-send -u critical "lattice-lab sizes-large" "failed: $*" 2> /dev/null || true
    exit 1
}

ready=$("${RP[@]}" wait-ssh "$POD" --timeout 900) || fail "no SSH"
line=$(echo "$ready" | sed -n 's/^ssh ready: //p' | tail -1)
[ -n "$line" ] || fail "no ssh command in: $ready"
read -r -a SSH <<< "$line"  # resolved once: nothing below asks the API again until the end
say "ssh: ${SSH[-1]}"

# a host can be many times slower than it should be: time a plain loop (0.24 s on the lab's machine)
gate=$("${SSH[@]}" 'python3 -c "
import time
t = time.time(); x = 0
for i in range(5000000): x += i
print(round(time.time() - t, 2))"') || fail "the speed gate did not run"
say "speed gate: $gate s"
awk -v t="$gate" 'BEGIN { exit !(t > 0.6) }' && fail "a slow host: $gate s for a loop that takes 0.24 s here"

"${SSH[@]}" 'cat > /root/pod-run.sh' < "$D/pod/pod-run.sh" || fail "staging"
timeout 30 "${SSH[@]}" "nohup setsid bash /root/pod-run.sh $BRANCH $COMMIT $WORKERS > /root/pod-run.out 2>&1 < /dev/null &" > /dev/null 2>&1
sleep 45
"${SSH[@]}" 'test -s /root/run/STATE' || fail "the job did not start"
say "job started on $POD"

while :; do
    sleep 180
    # the state is read before the pull: once it says done, what the pull brings is final
    state=$("${SSH[@]}" 'cat /root/run/STATE' 2> /dev/null)
    pull
    records=$(wc -l < "$OUT/pulled/records.jsonl" 2> /dev/null || echo 0)
    say "state: ${state:-?}; $records of 96 records"
    case "$state" in
        done)
            kind=none
            for _ in 1 2 3 4 5; do  # the pod is deleted only once its results are here
                kind=$(tail -1 "$OUT/pulled/ledger.jsonl" | "$PY" -c 'import json, sys; print(json.loads(sys.stdin.read())["kind"])')
                records=$(wc -l < "$OUT/pulled/records.jsonl" 2> /dev/null || echo 0)
                [ "$kind" = verdict ] && [ "$records" = 96 ] && break
                sleep 20
                pull
            done
            [ "$kind" = verdict ] && [ "$records" = 96 ] \
                || fail "done, but the pulled ledger ends with $kind and there are $records records"
            terminate
            say "done: the ledger and $records records are in $OUT/pulled"
            notify-send "lattice-lab sizes-large" "done: $records records pulled" 2> /dev/null || true
            exit 0
            ;;
        failed*) fail "the pod's run: $state" ;;
    esac
    [ "$(date +%s)" -lt $((DEADLINE - 600)) ] || fail "ten minutes to the deadline, at $records records"
done
