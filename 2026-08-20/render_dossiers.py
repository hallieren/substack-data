#!/usr/bin/env python3
"""Render sealed pico trajectories into readable, step-numbered dossiers for ch03 coding."""
import json, os, sys, random
from collections import Counter

S = os.path.dirname(os.path.abspath(__file__))
R = '/Users/hannahren/Documents/substack-data/2026-08-16/runs/20260815-sealed'

def trunc(s, head, tail=0):
    s = s or ''
    if len(s) <= head + tail + 20:
        return s
    if tail:
        return s[:head] + f'\n...[{len(s)-head-tail} chars omitted]...\n' + s[-tail:]
    return s[:head] + f'...[{len(s)-head} chars omitted]'

def render(iid, res_row, resolved, gold):
    d = json.load(open(f'{S}/sealed/trajs/{iid}.traj.json'))
    out = []
    n = 0
    problem = None
    for m in d['messages']:
        role = m['role']
        c = m['content']
        parts = c if isinstance(c, list) else [{'kind': 'text', 'text': c}]
        for p in parts:
            k = p.get('kind')
            if role == 'system':
                continue
            if role == 'user' and k == 'text' and problem is None:
                problem = p['text']
                continue
            n += 1
            if k == 'text':
                out.append(f"step {n:3d}  model        {trunc(p['text'], 1200, 200)}")
            elif k == 'tool_call':
                args = json.dumps(p.get('arguments', {}), ensure_ascii=False)
                out.append(f"step {n:3d}  tool_call    {p.get('name')} {trunc(args, 900, 100)}")
            elif k == 'tool_result':
                txt = p.get('text') or json.dumps(p.get('content', ''), ensure_ascii=False)
                out.append(f"step {n:3d}  tool_result  {trunc(txt, 1100, 300)}")
            else:
                out.append(f"step {n:3d}  {k or role}  {trunc(json.dumps(p, ensure_ascii=False), 500)}")

    logdir = f'{S}/sealed/logs/{iid}'
    rep = {}
    if os.path.exists(f'{logdir}/report.json'):
        rep = json.load(open(f'{logdir}/report.json')).get(iid, {})
    ts = rep.get('tests_status', {})
    f2p = ts.get('FAIL_TO_PASS', {})
    p2p = ts.get('PASS_TO_PASS', {})
    patch = ''
    if os.path.exists(f'{logdir}/patch.diff'):
        patch = open(f'{logdir}/patch.diff').read()
    g = gold.get(iid, {})

    hdr = [
        f"### DOSSIER {iid}",
        f"endpoint: resolved={resolved} | run_status={res_row['status']} | cost=${res_row['cost_usd']:.4f} | {res_row['seconds']}s | steps_rendered={n}",
        f"difficulty(SWE-bench annotation): {g.get('difficulty','?')}",
        f"patch_applied={rep.get('patch_successfully_applied','?')} | FAIL_TO_PASS passed {len(f2p.get('success',[]))}/{len(f2p.get('success',[]))+len(f2p.get('failure',[]))} | PASS_TO_PASS broken: {len(p2p.get('failure',[]))}",
        f"F2P still failing: {f2p.get('failure', [])[:6]}",
        f"P2P broken (regressions caused by the submitted patch): {p2p.get('failure', [])[:6]}",
        "",
        "--- PROBLEM STATEMENT (what the agent was asked to fix) ---",
        trunc(problem or '', 1900, 200),
        "",
        "--- TRAJECTORY (read FORWARD; ask each step: given the information available at this step, is this action reasonable?) ---",
    ]
    tail = [
        "",
        "--- SUBMITTED PATCH (what the agent turned in) ---",
        trunc(patch, 3500, 300) if patch else "(empty patch: nothing submitted)",
        "",
        "--- GOLD PATCH (the human maintainer's actual fix; ANSWER KEY, the agent never saw this) ---",
        trunc(g.get('patch', ''), 3500, 300),
        "",
        f"--- GOLD TEST PATCH (tests used to grade) ---",
        trunc(g.get('test_patch', ''), 1500),
    ]
    return '\n'.join(hdr + out + tail)

def main():
    er = json.load(open(f'{R}/eval_report.json'))
    res = {json.loads(l)['instance_id']: json.loads(l) for l in open(f'{R}/results.jsonl')}
    gold = json.load(open(f'{S}/gold.json'))
    fails = sorted(er['unresolved_ids'])
    resolved_set = set(er['resolved_ids'])

    rng = random.Random(42)
    order = fails[:]
    rng.shuffle(order)
    json.dump(order, open(f'{S}/coding_order.json', 'w'), indent=1)

    os.makedirs(f'{S}/dossiers', exist_ok=True)
    sizes = []
    for iid in fails:
        t = render(iid, res[iid], False, gold)
        open(f'{S}/dossiers/{iid}.txt', 'w').write(t)
        sizes.append(len(t))
    print(f'fails rendered: {len(fails)}, median {sorted(sizes)[len(sizes)//2]}B, max {max(sizes)}B, total {sum(sizes)/1e6:.1f}MB')

    # control sample: 12 resolved passes, stratified-ish by repo, seeded
    passes = sorted(resolved_set)
    rng2 = random.Random(7)
    ctrl = rng2.sample(passes, 12)
    json.dump(ctrl, open(f'{S}/control_ids.json', 'w'), indent=1)
    os.makedirs(f'{S}/dossiers_ctrl', exist_ok=True)
    for iid in ctrl:
        t = render(iid, res[iid], True, gold)
        open(f'{S}/dossiers_ctrl/{iid}.txt', 'w').write(t)
    print('controls rendered:', len(ctrl))

if __name__ == '__main__':
    main()
