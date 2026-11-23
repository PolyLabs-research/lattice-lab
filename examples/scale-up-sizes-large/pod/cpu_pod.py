#!/usr/bin/env python3
"""Rent the CPU pod for the large part of the scale-up test (sides 2048 and 4096).

    cd examples/scale-up-sizes-large/pod
    python cpu_pod.py --hours 6 --max-rate 1.12                    # the plan: nothing is created
    python cpu_pod.py --hours 6 --max-rate 1.12 --yes              # creates the pod
    python cpu_pod.py --hours 6 --max-rate 1.12 --yes --wait 20 \\
        --sizes cpu5c:32 cpu5g:16 cpu5c:16                         # the first of these in stock

This belongs to the lab's own machine, not to the study. It uses the lifecycle that machine
already runs for its other projects (`tinyalphazero.cloud`, in ~/Documents/dev/chess): the pod
carries a deadline in its name and deletes itself at it, a timer on the machine deletes any pod
past its deadline, a budget check refuses a launch the account cannot cover, and the API key is
read from a file, never from the command line or the environment. launch.sh, next to this
file, does everything after the launch. The owner confirms the flavour, the hours, the rate
ceiling and the worst cost before every `--yes`.

Large pods are often out of stock for minutes at a time, and RunPod then refuses the request
(nothing is created). `--sizes` names the sizes that will do, best first, as FLAVOUR:VCPUS;
`--wait` keeps asking for that many minutes, taking the first one in stock whose rate is under
the ceiling.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

CHESS_SRC = Path("~/Documents/dev/chess/src").expanduser()
sys.path.insert(0, str(CHESS_SRC))
try:
    from tinyalphazero import cloud
except ImportError as error:  # only on a machine without that lifecycle library
    raise SystemExit(f"the RunPod lifecycle library is not at {CHESS_SRC}: {error}") from None

TAG = "latticelab-sizes"
IMAGE = "runpod/base:1.4.1-ubuntu2404"  # RunPod's CPU base image; its CMD is /start.sh
RAM_PER_VCPU = {"c": 2, "g": 4, "m": 8}  # compute-optimised, general purpose, memory-optimised
EVERY = 20  # seconds between looks at the stock


def size(text: str) -> tuple[str, int]:
    """FLAVOUR:VCPUS, as cpu5c:32."""
    flavor, _, vcpu = text.partition(":")
    if flavor[:3] != "cpu" or flavor[-1:] not in RAM_PER_VCPU or not vcpu.isdigit():
        raise argparse.ArgumentTypeError(f"not a size like cpu5c:32: {text!r}")
    count = int(vcpu)
    if count < 2 or count & (count - 1):
        raise argparse.ArgumentTypeError("the vCPU count must be a power of two, 2 or more")
    return flavor, count


def ram(flavor: str, vcpu: int) -> int:
    return vcpu * RAM_PER_VCPU[flavor[-1]]


def stock(rp: cloud.RunPod, sizes: list[tuple[str, int]]) -> list[dict]:
    """Each size's hourly price and whether it is in stock now, from one query."""
    parts = [
        f'q{i}: cpuFlavors {{ id specifics(input: {{instanceId: "{flavor}-{vcpu}-'
        f'{ram(flavor, vcpu)}"}}) {{ stockStatus securePrice }} }}'
        for i, (flavor, vcpu) in enumerate(sizes)
    ]
    data = rp._gql("query { " + " ".join(parts) + " }")  # noqa: SLF001
    out = []
    for i, (flavor, vcpu) in enumerate(sizes):
        found = [f["specifics"] for f in data[f"q{i}"] if f["id"] == flavor]
        if not found:
            raise cloud.CloudError(f"RunPod lists no flavour {flavor!r}")
        out.append(
            {
                "flavor": flavor,
                "vcpu": vcpu,
                "ram": ram(flavor, vcpu),
                "rate": float(found[0]["securePrice"]),
                "stock": found[0]["stockStatus"],
            }
        )
    return out


def body(deadline: int, flavor: str, vcpu: int, disk_gb: int, tag: str = TAG) -> dict:
    """RunPod's REST v2 request for a CPU pod (checked against its published schema)."""
    return {
        "name": cloud.pod_name(tag, deadline),
        "image": IMAGE,
        "cloud": "SECURE",
        "cpu": {"id": flavor, "vcpuCount": vcpu},
        "disk": disk_gb,
        "ports": ["22/tcp"],
        "startSsh": True,
        "cmd": cloud.watchdog_start_cmd(True),
        "env": {"TAZ_DEADLINE": str(deadline)},
    }


def launch(rp: cloud.RunPod, found: dict, args: argparse.Namespace, balance: float) -> int | None:
    """Create a pod of this size. 0 when it is up, 2 when its own rate was refused (and it was
    deleted at once), None when RunPod had none after all."""
    limits = cloud.Limits.load()
    deadline = int(time.time() + args.hours * 3600)
    request = body(deadline, found["flavor"], found["vcpu"], args.disk, args.tag)
    try:
        pod = rp.create_pod(request)
    except cloud.CloudError as error:
        if "no longer any instances" in str(error):
            print(f"{time.strftime('%H:%M:%S')} none after all: {found['flavor']}:{found['vcpu']}")
            return None
        raise
    cloud.ledger(
        "launch", pod_id=pod["id"], name=request["name"], deadline=deadline,
        spec={"project": "lattice-lab", "flavor": found["flavor"], "vcpu": found["vcpu"],
              "hours": args.hours, "image": IMAGE},
    )  # fmt: skip
    actual = float(pod.get("cost") or found["rate"])
    refusal = None
    if actual > args.max_rate:
        refusal = f"the pod's rate ${actual:.3f}/h is over the ceiling ${args.max_rate:.3f}/h"
    else:
        try:
            cloud.plan(actual, args.hours, balance, limits)
        except cloud.BudgetError as error:
            refusal = str(error)
    if refusal:
        rp.terminate_pod(pod["id"])
        cloud.ledger("terminate", pod_id=pod["id"], reason=f"actual rate refused: {refusal}")
        print(f"terminated {pod['id']} at once: {refusal}")
        return 2
    print(
        f"launched {pod['id']} {request['name']} at ${actual:.3f}/h ({found['flavor']}, "
        f"{found['vcpu']} vCPUs, {found['ram']} GB); worst case ${actual * args.hours:.2f} "
        "by the deadline"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--sizes", type=size, nargs="+", default=[("cpu5c", 32)],
                        help="the sizes that will do, best first, as FLAVOUR:VCPUS")  # fmt: skip
    parser.add_argument("--hours", type=float, required=True, help="the hard deadline, from now")
    parser.add_argument("--max-rate", type=float, required=True, help="the confirmed $/h ceiling")
    parser.add_argument("--wait", type=float, default=0, help="minutes to keep asking for stock")
    parser.add_argument("--disk", type=int, default=20, help="container disk, GB")
    parser.add_argument("--tag", default=TAG, help="the pod's name carries it: [a-z0-9_-]")
    parser.add_argument("--yes", action="store_true", help="actually create the pod")
    args = parser.parse_args(argv)
    try:
        rp = cloud.RunPod()
        limits = cloud.Limits.load()
        balance = rp.balance()["balance"]
        end = time.time() + args.wait * 60
        first = True
        while True:
            try:
                sizes = stock(rp, args.sizes)
            except cloud.CloudError as error:  # a rate limit or a blip: ask again next time
                if first:
                    raise
                print(f"{time.strftime('%H:%M:%S')} could not ask: {str(error)[:120]}")
                sizes = []
            for found in sizes:
                within = found["rate"] <= args.max_rate
                if first:
                    worst = cloud.plan(found["rate"], args.hours, balance, limits) if within else 0
                    print(
                        f"plan: {found['flavor']}, {found['vcpu']} vCPUs, {found['ram']} GB, "
                        f"SECURE, ${found['rate']:.3f}/h, {args.hours} h cap -> worst case "
                        f"${worst:.2f}; stock {found['stock']}"
                        + ("" if within else f"; OVER the ceiling ${args.max_rate:.3f}/h, skipped")
                    )
                if within and found["stock"] and args.yes:
                    result = launch(rp, found, args, balance)
                    if result is not None:
                        return result
            if first:
                print(f"balance ${balance:.2f}; ceiling ${args.max_rate:.3f}/h")
            first = False
            if not args.yes:
                print("dry run: nothing created (pass --yes to launch)")
                return 0
            if time.time() >= end:
                print(f"no pod: none of these sizes could be had in {args.wait:g} minutes")
                return 3
            time.sleep(EVERY)
    except cloud.CloudError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
