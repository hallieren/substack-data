import json, statistics, math
data=json.load(open('steps_tokens.json'))
cats=json.load(open('sphinx7985_cats.json'))
costs=sorted(d['cost'] for d in data)
n=len(costs)
med=statistics.median(costs); mean=statistics.mean(costs)
p95=costs[int(0.95*n)]; mx=costs[-1]

# ---------- blog-02: 500 traces sorted by cost ----------
W,H=952,560
bw=W/n
def Y(c): return H-c/0.07*H
bars=[]
for i,c in enumerate(costs):
    rank=i+1
    fill='var(--grey-2)' if rank<=250 else ('var(--accent)' if rank>475 else '#A9A9A7')
    h=H-Y(c)
    bars.append(f'<rect x="{i*bw:.2f}" y="{Y(c):.2f}" width="{bw:.2f}" height="{max(h,2.5):.2f}" fill="{fill}"/>')
grid=[]
for gv,glab in [(0.02,'$0.02'),(0.04,'$0.04'),(0.06,'$0.06')]:
    gy=Y(gv)
    grid.append(f'<line x1="0" y1="{gy:.1f}" x2="{W}" y2="{gy:.1f}" stroke="var(--grey-1)" stroke-width="2"/>')
    grid.append(f'<text x="-14" y="{gy+9:.1f}" text-anchor="end" class="axlab">{glab}</text>')
# boundary marks
marks=[]
for rank,v,lab,anch,dx in [(250,med,'median $0.0098','end',-10),(475,p95,'P95 $0.047','end',-10)]:
    x=rank*bw
    marks.append(f'<line x1="{x:.1f}" y1="26" x2="{x:.1f}" y2="{H}" stroke="var(--ink)" stroke-width="2" stroke-dasharray="7 7" opacity=".5"/>')
    marks.append(f'<text x="{x+dx:.1f}" y="12" text-anchor="{anch}" class="axlab">{lab}</text>')
marks.append(f'<text x="{W-46:.1f}" y="64" text-anchor="end" class="axlab">max $0.067</text>')
# mean horizontal line
my=Y(mean)
marks.append(f'<line x1="0" y1="{my:.1f}" x2="{W}" y2="{my:.1f}" stroke="var(--grey-3)" stroke-width="2.5" stroke-dasharray="4 7"/>')
marks.append(f'<text x="10" y="{my-12:.1f}" class="axlab" fill="var(--text-secondary)">mean $0.0151, dearer than 65% of traces</text>')
# region brackets below axis
def bracket(x1,x2,y):
    return (f'<path d="M {x1:.1f} {y} v 12 H {x2:.1f} v -12" fill="none" stroke="var(--grey-3)" stroke-width="2"/>')
B=H+16
regions=f'''
{bracket(0,250*bw,B)}
<text x="{125*bw:.1f}" y="{B+52}" text-anchor="middle" class="axlab">250 traces</text>
<text x="{125*bw:.1f}" y="{B+90}" text-anchor="middle" class="axlab" font-weight="600" fill="var(--ink)">$1.20</text>
{bracket(250*bw+4,475*bw-4,B)}
<text x="{362*bw:.1f}" y="{B+52}" text-anchor="middle" class="axlab">226 traces</text>
<text x="{362*bw:.1f}" y="{B+90}" text-anchor="middle" class="axlab" font-weight="600" fill="var(--ink)">$5.03</text>
{bracket(475*bw+4,W,B)}
<text x="{W:.1f}" y="{B+52}" text-anchor="end" class="axlab" fill="var(--accent)">24 traces</text>
<text x="{W:.1f}" y="{B+90}" text-anchor="end" class="axlab" font-weight="600" fill="var(--accent)">$1.32</text>
'''
sorted_svg=f'''<svg viewBox="-108 -6 {W+152} {H+126}" xmlns="http://www.w3.org/2000/svg">
{''.join(grid)}
{''.join(bars)}
{''.join(marks)}
<line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="var(--grey-2)" stroke-width="2"/>
{regions}
</svg>'''

# ---------- blog-03 barcode ----------
COLS=26
cell=34; gap=5
cmap={'locate':'var(--grey-2)','verify':'var(--grey-3)','edit':'var(--ink)','hunt':'var(--accent)','final':'#B9B9B7'}
cells=[]
for s in range(1,131):
    r,c=(s-1)//COLS,(s-1)%COLS
    x=c*(cell+gap); y=r*(cell+gap)
    cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="6" fill="{cmap[cats[str(s)]]}"/>')
rows=math.ceil(130/COLS)
bw_=COLS*(cell+gap)-gap
bh_=rows*(cell+gap)-gap
lx=((130-1)%COLS+1)*(cell+gap)-gap+10
ly=((130-1)//COLS)*(cell+gap)
barcode_svg=f'''<svg viewBox="0 0 {bw_+150} {bh_+8}" xmlns="http://www.w3.org/2000/svg">
{''.join(cells)}
<text x="{lx+4}" y="{ly+cell-8}" class="axlab" fill="var(--accent)" font-weight="600">✕ killed</text>
</svg>'''

# ---------- blog-04 scatter ----------
W2,H2=920,600
xmax=175; ymax=8.4e6
pts=[]
for d in data:
    x=d['steps']/xmax*W2; y=H2-d['ctx']/ymax*H2
    pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="var(--grey-3)" opacity=".38"/>')
hl=[]
for iid,l1,l2,dx,dy,anch in [
  ('sympy__sympy-13877','median trace','46 steps · 1.0M tokens',-236,-136,'start'),
  ('sphinx-doc__sphinx-7985','dearest trace','130 steps · 7.9M tokens',-16,58,'end')]:
    d=[q for q in data if q['iid']==iid][0]
    x=d['steps']/xmax*W2; y=H2-d['ctx']/ymax*H2
    hl.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="var(--accent)"/>')
    hl.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anch}" class="axlab" fill="var(--ink)" font-weight="600">{l1}</text>')
    hl.append(f'<text x="{x+dx:.1f}" y="{y+dy+30:.1f}" text-anchor="{anch}" class="axlab">{l2}</text>')
ceil_y=H2-8e6/ymax*H2
grid2=[]
for gv,glab in [(2e6,'2M'),(4e6,'4M'),(6e6,'6M')]:
    gy=H2-gv/ymax*H2
    grid2.append(f'<line x1="0" y1="{gy:.1f}" x2="{W2}" y2="{gy:.1f}" stroke="var(--grey-1)" stroke-width="2"/>')
    grid2.append(f'<text x="-14" y="{gy+9:.1f}" text-anchor="end" class="axlab">{glab}</text>')
xt=[]
for gv in [50,100,150]:
    gx=gv/xmax*W2
    xt.append(f'<line x1="{gx:.1f}" y1="{H2}" x2="{gx:.1f}" y2="{H2+10}" stroke="var(--grey-2)" stroke-width="2"/>')
    xt.append(f'<text x="{gx:.1f}" y="{H2+44}" text-anchor="middle" class="axlab">{gv}</text>')
scatter_svg=f'''<svg viewBox="-84 -30 {W2+130} {H2+92}" xmlns="http://www.w3.org/2000/svg">
{''.join(grid2)}
<line x1="0" y1="{ceil_y:.1f}" x2="{W2}" y2="{ceil_y:.1f}" stroke="var(--accent)" stroke-width="2.5" stroke-dasharray="9 8"/>
<text x="{W2}" y="{ceil_y-12:.1f}" text-anchor="end" class="axlab" fill="var(--accent)" font-weight="600">8M-token ceiling, 18 runs killed here</text>
{''.join(pts)}
{''.join(hl)}
<line x1="0" y1="{H2}" x2="{W2}" y2="{H2}" stroke="var(--grey-2)" stroke-width="2"/>
{''.join(xt)}
<text x="{W2}" y="{H2+44}" text-anchor="end" class="axlab">steps</text>
<text x="-84" y="-12" class="axlab">context tokens read</text>
</svg>'''

head='''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Where Did the Money Go · Figures</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@250;300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--paper:#FAFAF8;--ink:#0A0A0A;--grey-1:#F0F0EE;--grey-2:#D4D4D2;--grey-3:#737373;--accent:#002FA7;
--text-secondary:#525252;--text-helper:#737373;
--sans:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif;--mono:"JetBrains Mono","SF Mono",Menlo,Consolas,monospace;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);font-family:var(--sans);color:var(--ink);-webkit-font-smoothing:antialiased;font-feature-settings:"ss01","cv11","tnum"}
section.figure{width:1080px;background:var(--paper);margin:48px auto;padding:64px;display:flex;flex-direction:column}
h2{font-size:54px;font-weight:400;letter-spacing:-.02em;line-height:1.18;margin-bottom:12px}
h2 b{font-weight:600;color:var(--accent)}
.sub{font-family:var(--mono);font-size:27px;line-height:1.45;color:var(--text-helper);margin-bottom:34px}
.axlab{font-family:var(--mono);font-size:26px;fill:var(--grey-3)}
.legend{display:flex;flex-wrap:wrap;gap:14px 34px;margin-top:30px}
.legend .it{display:flex;align-items:center;gap:12px;font-family:var(--mono);font-size:26px;color:var(--text-secondary)}
.sw{width:30px;height:30px;border-radius:7px;flex:none}
.maprow{display:grid;grid-template-columns:1fr 56px 1fr;gap:18px;align-items:center;border-top:1px solid var(--grey-2);padding:22px 0}
.maprow.first{border-top:none}
.mL{font-size:30px;line-height:1.35}
.mL b{font-weight:600}
.mL .d{font-family:var(--mono);font-size:24px;color:var(--text-helper);margin-top:6px}
.mArr{font-size:34px;color:var(--accent);text-align:center;font-weight:600}
.mR{font-size:29px;line-height:1.4}
.mR code{font-family:var(--mono);font-size:25px;background:var(--grey-1);border-radius:7px;padding:3px 9px}
.mR .d{font-family:var(--mono);font-size:24px;color:var(--text-helper);margin-top:6px}
.colhead{display:grid;grid-template-columns:1fr 56px 1fr;gap:18px;font-family:var(--mono);font-size:24px;font-weight:600;letter-spacing:.06em;color:var(--grey-3);margin-bottom:8px}
.hunts{margin-top:36px;border-top:1px solid var(--grey-2);padding-top:10px}
.hunts .hh{font-family:var(--mono);font-size:24px;font-weight:600;letter-spacing:.06em;color:var(--accent);margin:14px 0 6px}
.hunt-it{display:grid;grid-template-columns:1fr 330px;gap:20px;align-items:baseline;font-size:29px;line-height:1.45;padding:10px 0}
.hunt-it .res{font-family:var(--mono);font-size:25px;color:var(--accent);font-weight:600;text-align:right}
.bars{display:flex;flex-direction:column;gap:44px;margin-top:10px}
.bar-g .cap{font-family:var(--mono);font-size:27px;color:var(--text-secondary);margin-bottom:12px}
.bar-track{height:88px;background:var(--grey-1);border-radius:10px;position:relative;overflow:hidden}
.bar-fill{height:100%;border-radius:10px 0 0 10px;display:flex;align-items:center}
.bar-fill span{font-family:var(--mono);font-size:34px;font-weight:600;color:#fff;padding-left:24px}
</style></head><body>
'''
figs=[]
# blog-01 mapping, rows ordered to match the article's three steps
maprows=[
 ("cost and latency as first-class metrics","report them, budget them, alarm on them",
  "<code>cost_usd</code>, <code>seconds</code>, tokens on every line of <code>results.jsonl</code>","logged since day one, read today"),
 ("report three numbers","median, P95, max, never the mean",
  "$0.0098 / $0.047 / $0.067","mean $0.0151 describes no trace"),
 ("orphan steps","steps that serve no subgoal of the task",
  "reads and searches unrelated to the final patch","the dearest trace has 10"),
 ("budget line","an alarm pinned at P95, verdict concern",
  "<code>max_spend_tokens = 8M</code>","existed, but wired as a kill switch"),
 ("task type","budget lines are drawn per type, never merged",
  "the repo the issue lives in","django $0.0088 vs sphinx $0.0123 median"),
]
rowshtml=''.join(
 f'<div class="maprow{" first" if i==0 else ""}"><div class="mL"><b>{a}</b><div class="d">{b}</div></div><div class="mArr">→</div><div class="mR">{c}<div class="d">{d}</div></div></div>'
 for i,(a,b,c,d) in enumerate(maprows))
figs.append(f'''<section class="figure" data-name="blog-01">
<h2>Chapter 9 maps onto this run with <b>zero new parts</b></h2>
<div class="sub">pico + DeepSeek V4-Flash · SWE-bench Verified, 500 tasks, sealed run of 2026-08-15 · no re-run needed</div>
<div class="colhead"><div>THE BOOK SAYS</div><div></div><div>IN THIS RUN IT IS</div></div>
{rowshtml}
</section>''')

# blog-02 sorted-cost queue
figs.append(f'''<section class="figure" data-name="blog-02">
<h2>The <b>24 dearest traces</b> out-bill the cheapest <b>250</b></h2>
<div class="sub">all 500 traces lined up by cost, cheapest to dearest · one thin bar = one trace · height = its cost</div>
{sorted_svg}
</section>''')

# blog-03 barcode
hunts=[
 ("Tried to download the future version of the fix from GitHub","blocked, no network"),
 ("Tried to install a sphinx released after the code freeze","blocked, no network"),
 ("Dug through git, tags and all, for commits from the future","empty, history sealed"),
 ("Searched the whole disk for another copy of the answer","nothing found"),
]
huntshtml=''.join(f'<div class="hunt-it"><div>{a}</div><div class="res">{b}</div></div>' for a,b in hunts)
figs.append(f'''<section class="figure" data-name="blog-03">
<h2>Ten steps of the dearest trace went <b>hunting for the answer key</b></h2>
<div class="sub">sphinx-doc__sphinx-7985 · 130 steps read left to right · final patch touches one file</div>
{barcode_svg}
<div class="legend">
<div class="it"><span class="sw" style="background:var(--grey-2)"></span>locate &amp; read · 50</div>
<div class="it"><span class="sw" style="background:var(--grey-3)"></span>reproduce &amp; verify · 50</div>
<div class="it"><span class="sw" style="background:var(--ink)"></span>edit the fix · 16</div>
<div class="it"><span class="sw" style="background:var(--accent)"></span>answer-key hunt · 10</div>
<div class="it"><span class="sw" style="background:#B9B9B7"></span>wrap-up · 4</div>
</div>
<div class="hunts">
<div class="hh">WHAT THE 10 BLUE STEPS DID, IN PLAIN WORDS</div>
{huntshtml}
</div>
</section>''')

# blog-04 scatter
figs.append(f'''<section class="figure" data-name="blog-04">
<h2>The context re-read grows with <b>the square of the steps</b></h2>
<div class="sub">each dot = one task · 2.8&times; the steps of the median trace reads 7.7&times; the tokens</div>
{scatter_svg}
</section>''')

# blog-05 alarm bars
figs.append(f'''<section class="figure" data-name="blog-05">
<h2>The traces the alarm flags fail <b>2.7&times; as often</b></h2>
<div class="sub">budget line pinned at P95 · over the line means someone goes and reads the trace</div>
<div class="bars">
<div class="bar-g"><div class="cap">all 500 traces · 107 failed</div>
<div class="bar-track"><div class="bar-fill" style="width:21.4%;background:var(--grey-3)"><span>21%</span></div></div></div>
<div class="bar-g"><div class="cap">the 24 traces above P95 · 14 failed</div>
<div class="bar-track"><div class="bar-fill" style="width:58.3%;background:var(--accent)"><span>58%</span></div></div></div>
</div>
</section>''')

out=head+'\n'.join(figs)+'\n</body></html>'
open('/Users/hannahren/Documents/daily/articles/2026-08-28/figures/index.html','w').write(out)
print('written',len(out))
