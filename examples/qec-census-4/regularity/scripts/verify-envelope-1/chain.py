import sys; sys.path.insert(0, '.')
from fit import *
# forward chain: tightest-envelope (UP) fits on n in [nmin, cut], residual f(n_mid)-d at the next thresholds in (cut, cut+60]
for nmin in (30, 100):
  print(f'--- UP fits, train [{nmin}, cut] ---')
  for name in ('c*sqrt(n)', 'c*sqrt(n)*ln n', 'a+b*n', 'c*sqrt(n)(1-e^-n/n0)', 'A*sqrt(n)+B', 'c*sqrt(n ln n)', 'a*n^b'):
    row = []
    for cut in (150, 200, 250, 300):
        p, _ = fit_up(name, nmin, cut)
        nxt = [(d, a, b) for d, a, b in thr if cut < b <= cut + 60]
        row.append([round(float(fev(name, (a+b)/2, p) - d), 2) for d, a, b in nxt])
    allr = [x for r in row for x in r]
    print(f'{name:22s}', row, ' mean %+.2f' % np.mean(allr), ' all<0' if all(x < 0 for x in allr) else (' all>0' if all(x > 0 for x in allr) else ''))
