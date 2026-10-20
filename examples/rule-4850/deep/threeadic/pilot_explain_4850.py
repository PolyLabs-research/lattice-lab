"""What the seventh pilot's condition says about 4850 and relatives at 37 (cube level?)."""
import sys, time
sys.path.insert(0, "/home/user/pilot-37c-round2")
sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
import mechanism
import census37 as C
for n, r in ((4850, 4), (482758, 5), (10491524, 6), (20982139, 6), (178279803, 6)):
    t0 = time.time()
    w = mechanism.explain(C.rule(n, r), 37)
    print(n, w, round(time.time() - t0, 2), "s", flush=True)
