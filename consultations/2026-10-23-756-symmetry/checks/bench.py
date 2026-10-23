import sys, subprocess, time, random, importlib.util
D_='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/sym/'
spec=importlib.util.spec_from_file_location('parts','/home/user/lattice-lab/examples/qec-open-distance/parts.py'); P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
D=P.distance; bb=P.bb
def run(exe,A,B,l,m,b,anchors):
    n,r,k,rows,marks=P._code(A,B,l,m,'Z')
    text="\n".join([f"{n} {r} {k} {b} {b} {len(anchors)}"," ".join(map(str,anchors)),*rows,*marks])+"\n"
    t=time.time(); out=subprocess.run([D_+exe],input=text,capture_output=True,text=True).stdout
    finds=[l_ for l_ in out.split("\n") if l_.startswith("best")]
    nodes=[int(l_.split()[1]) for l_ in out.split("\n") if l_.startswith("done")][0]
    return (len(finds[-1].split())-2 if finds else None), nodes, round(time.time()-t,2)
mode=sys.argv[1]
if mode=='small':
    rng=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 11); bad=0; tested=0; seen=set()
    for l,m in [(3,4),(3,7),(4,6),(2,9),(3,6),(3,8),(6,3)]:
        for _ in range(400):
            A=[(rng.randrange(l),rng.randrange(m)) for _ in range(3)];B=[(rng.randrange(l),rng.randrange(m)) for _ in range(3)]
            if len(set(A))<3 or len(set(B))<3 or not bb.k_linalg(A,B,l,m) or l*m+bb.k_linalg(A,B,l,m)//2>28: continue
            key=(l,m,tuple(A),tuple(B))
            if key in seen or len(seen)>=int(sys.argv[3] if len(sys.argv)>3 else 60): continue
            seen.add(key)
            want=D.distance_brute(A,B,l,m,'Z')['d']
            for anchors in ([0,l*m], list(range(2*l*m))):
                got=run('pack',A,B,l,m,64,anchors)[0]  # one pass, bound 64: exact least weight
                tested+=1; bad+= got!=want
    print('small codes: tested',tested,'mismatches',bad)
elif mode not in ("medium",):
    l,m,A,B,bs=eval(mode)
    for b in bs:
        print(b, 'nopack', run('nopack',A,B,l,m,b,[0,l*m]), 'pack', run('pack',A,B,l,m,b,[0,l*m]), flush=True)
if mode=='medium':
    import json
    def deep(exe,A,B,l,m):
        for b in range(2,40):
            w,nodes,t=run(exe,A,B,l,m,b,[0,l*m])
            if w is not None: return w
    cases=[]
    for e in json.load(open('/home/user/lattice-lab/examples/qec-bb/codes.json'))['codes'] if isinstance(json.load(open('/home/user/lattice-lab/examples/qec-bb/codes.json')),dict) else json.load(open('/home/user/lattice-lab/examples/qec-bb/codes.json')):
        if e.get('A') and e.get('n',0)<=300 and e['n']!=288: cases.append((e['l'],e['m'],[tuple(t) for t in e['A']],[tuple(t) for t in e['B']],e.get('d')))
    rng=random.Random(5)
    while len(cases)<len([c for c in cases if c[4]])+20:
        l,m=rng.choice([(6,9),(5,12),(7,10),(9,8),(4,15),(6,14),(8,9)])
        A=[(rng.randrange(l),0),(0,rng.randrange(m)),(0,rng.randrange(m))];B=[(0,rng.randrange(m)),(rng.randrange(l),0),(rng.randrange(l),0)]
        if len(set(A))<3 or len(set(B))<3 or not bb.k_linalg(A,B,l,m): continue
        cases.append((l,m,A,B,None))
    bad=0
    for l,m,A,B,pub in cases:
        a,b_=deep('pack',A,B,l,m),deep('nopack',A,B,l,m)
        bad+= a!=b_ or (pub is not None and a!=pub)
        print(l,m,'pack',a,'nopack',b_,'published',pub,flush=True)
    print('mismatches',bad)
