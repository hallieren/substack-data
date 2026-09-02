import json, glob, statistics, re, os
BASE='/Users/hannahren/Documents/substack-data/2026-08-16'
rows=[json.loads(l) for l in open(f'{BASE}/runs/20260815-sealed/results.jsonl')]
res={r['instance_id']:r for r in rows}

# resolved status
rep=json.load(open(f'{BASE}/runs/20260815-sealed/report.json'))
print('report keys', list(rep)[:10])

# step counts from trajs
steps={}
for r in rows:
    iid=r['instance_id']
    p=f'trajs-sealed/trajs/{iid}.traj.json'
    if not os.path.exists(p): continue
    t=json.load(open(p))
    n=0
    for m in t['messages']:
        c=m.get('content')
        if m['role']=='assistant' and isinstance(c,list) and any(k.get('kind')=='tool_call' for k in c):
            n+=1
    steps[iid]=n

costs=sorted(r['cost_usd'] for r in rows)
n=len(costs)
med=statistics.median(costs); mean=statistics.mean(costs)
p95=costs[int(0.95*n)]
out={
 'n':n,'median':med,'mean':mean,'p95':p95,'max':costs[-1],'sum':sum(costs),
 'tail_over_median':costs[-1]/med,
 'sum_above_p95':sum(c for c in costs if c>p95),
 'n_above_p95':sum(1 for c in costs if c>p95),
 'sum_below_median':sum(c for c in costs if c<=med),
 'n_below_median':sum(1 for c in costs if c<=med),
}
sec=sorted(r['seconds'] for r in rows)
out['sec_median']=statistics.median(sec); out['sec_p95']=sec[int(0.95*n)]; out['sec_max']=sec[-1]
st=sorted(steps.values())
out['steps_median']=statistics.median(st); out['steps_p95']=st[int(0.95*len(st))]; out['steps_max']=st[-1]; out['steps_min']=st[0]
print(json.dumps(out,indent=1))

# per repo
from collections import defaultdict
byrepo=defaultdict(list)
for r in rows: byrepo[r['instance_id'].split('__')[0]].append(r['cost_usd'])
for k,v in sorted(byrepo.items(), key=lambda kv:-statistics.median(kv[1])):
    v=sorted(v)
    print(f'{k:20s} n={len(v):3d} med={statistics.median(v):.4f} p95={v[int(0.95*len(v))]:.4f} max={v[-1]:.4f}')

# steps vs tokens (quadratic check)
data=[]
for r in rows:
    iid=r['instance_id']
    if iid in steps:
        data.append({'iid':iid,'steps':steps[iid],'ctx':r['input_tokens']+r['cache_read_tokens'],'out':r['output_tokens'],'cost':r['cost_usd'],'sec':r['seconds']})
json.dump(data,open('steps_tokens.json','w'))
top=sorted(data,key=lambda d:-d['cost'])[:10]
for d in top: print(d['iid'], d['steps'],'steps', f"{d['ctx']:,}ctx", f"${d['cost']:.4f}")
