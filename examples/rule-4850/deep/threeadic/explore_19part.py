"""The 19-part left over by 4850's sparse 3-part solution N = (t_x t_y t_xy t_x/y prod_{(5,2)-orbit} t_w)^3:
f * N is a 27th power off the diagonal lines; is its 19-part structured?  Minimal mod-19 orbit support
of log_t(f N) mod 19 on the classes off the diagonal (and (1,6)), with any further vanishing allowed on
the cyclotomic classes; compare with f's own 19-part and random 19-parts (step6 null)."""
import numpy as np
from step5_support import Phi_matrix, logt_classes
from step6_calib import min_orbits
P19 = Phi_matrix(19)
t19 = np.array(logt_classes(4850, 4, 19))
T = [0, 1, 7]
fn19 = (t19 + 3 * P19[T].sum(axis=0)) % 19
print("log_t f mod 19:", t19.tolist())
print("log_t (f N) mod 19:", fn19.tolist())
z9 = [0] * 11
for label, tgt in (("f", t19), ("f*N", fn19)):
    for allowed in ([1], [0, 1, 2]):
        print(label, "allowed vanishing classes", allowed, "-> min orbits mod 19:",
              min_orbits(z9, tgt.tolist(), allowed, ("19",)))
rng = np.random.default_rng(7)
vals = []
for i in range(40):
    r19 = rng.integers(0, 19, 11); r19[6] = 0
    vals.append(min_orbits(z9, r19.tolist(), [1], ("19",)))
print("random 19-parts, vanishing on the diagonal allowed: min orbits histogram",
      {k: vals.count(k) for k in sorted(set(vals))})
