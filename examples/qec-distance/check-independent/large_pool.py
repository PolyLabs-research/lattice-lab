import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
jobs = json.load(open(sys.argv[1])); outp = Path(sys.argv[2]); workers = int(sys.argv[3])
key = lambda j: (j["file"], j["i"], j["kind"], j["trans"])
done = {key(json.loads(l)) for l in outp.read_text().splitlines()} if outp.exists() else set()
todo = [j for j in jobs if key(j) not in done]
def run(j):
    p = subprocess.run([sys.executable, "large_job.py", json.dumps(j)], capture_output=True, text=True, timeout=j["limit"] + 1000)
    return p.stdout.strip().splitlines()[-1] if p.returncode == 0 else json.dumps({**j, "error": p.stderr[-500:]})
with ThreadPoolExecutor(workers) as ex:
    for f in as_completed([ex.submit(run, j) for j in todo]):
        line = f.result()
        with open(outp, "a") as fh: fh.write(line + "\n")
        r = json.loads(line)
        print(r["i"], r["kind"], r["trans"], r.get("dfs"), r.get("ilp"), r.get("wit_mine"), r.get("error", ""), flush=True)
