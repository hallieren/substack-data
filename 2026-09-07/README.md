# 2026-09-07: one improvement cycle on pico (ch15 follow-along)

Companion data for the article "仪表盘红了，先动哪根杠杆" (Which lever fixes
your agent's worst failure). Method: *AI Agent Evaluation* ch15, failure
mining on stored runs, bottleneck-to-lever mapping read backwards, one lever
moved (a gate), two-part verification. Continues the 09-04 release gate,
whose sev-1 red light (test files left in the diff) is this cycle's target.

## Question

The 09-04 gate went red on pico leaving test files in its diff. Editing the
prompt is the reflex; the prompt already forbids it. Which lever does the
evidence point at, and does moving it fix the mode without breaking the rest?

## Design

- Failure mining, zero model calls: `mine.py` pools all 169 stored runs
  (08-26 seed x5, 09-04 seed x3, 09-03 replay and harvest), tags pico's
  signals (red line, budget death, judge escalation, no-fix not escalated),
  stratifies by signal x task type, sev-1 all in, draws 33 for reading.
  One hardcoded pattern, `testtree.target` (a tool call that writes into the
  test tree), the same function the gate enforces.
- Reading: `analysis/coding-borrow.md` (ten flagged runs, by hand),
  `analysis/coding-sample.md` (23 more, sonnet subagents on `view.py`
  compact views, names and criteria checked by hand),
  `analysis/atlas-extension.md` (new rows, six columns).
- Hypotheses and the lever: `cycle.md` (ch15 template). H1 prompt, falsified
  by reading. H2 tool description, global in a four-tool agent, kept for the
  next cycle. H3 gate, moved: `gate_variant.py` wraps the 08-26 runner in
  pico's own `gate` callback; refusals logged to `runs/gate/gate-log.jsonl`.
- Arm: pico-001 / pico-004 / pico-016 (the only seed cases whose stored runs
  ever wrote into the test tree) x 5, the 08-26 SYSTEM unchanged, same
  worlds, seal, accept scripts, assertions, judge, concurrency 6, model
  deepseek-v4-flash. Baseline: the 08-26 runs of the same cases (15,
  strictly paired); the 09-04 runs (9, with the 09-02 prompt line) shown as
  a wider pool.
- Rejection rule written before the arm: the article's evidence README,
  mirrored in `cycle.md`.

## Headline numbers

| line | criterion | baseline 08-26 (15) | gated arm (15) | light |
|---|---|---|---|---|
| test files left in the final diff | 0 | 2 | 1 (pico-004-r4, python heredoc, budget death) | **RED** |
| runs that wrote or tried to write into the test tree | recorded | 6 | 5 (3 calls refused, 4 heredoc writes unseen) | recorded |
| runs with a write the gate never saw | 0 | no gate | 3 | **RED** |
| pass rate on the three cases, paired | >= 25% | 9/15 = 60% | 8/15 = 53% (-7 ± 35 pts) | green |
| other red lines | 0 | 2 | 0 | green |
| budget deaths | recorded | 8 | 8 | recorded |

Verdict under the pre-written rule: failure, roll back. The gate refused
every write it could parse and pico never retried a refused call; the three
leaks all went through a python heredoc inside a bash call, the form the
preregistration listed as unseen. Arm cost $0.70, 29 minutes. Full tables in
`analysis/verify.md`, the cycle's conclusion and next candidates in
`cycle.md`.

## Layout

| Path | What it is |
|---|---|
| `testtree.py` | the one rule: does this tool call write into the test tree (miner, gate, verifier share it) |
| `mine.py` → `analysis/pool.md`, `pool.json` | the pool, strata, draw, pre-sort piles |
| `timelines.py` → `analysis/borrow-timelines.json` | first write, restore, end of run for the flagged runs |
| `view.py` | compact trajectory view for trace reading (windowed or full) |
| `analysis/coding-borrow.md`, `coding-sample.md`, `atlas-extension.md` | the reading and the atlas increment |
| `cycle.md` | the improvement cycle template, filled |
| `gate_variant.py` | the arm runner, 08-26 harness + the gate row |
| `runs/gate/` | results.jsonl, trajs/, world/, gate-log.jsonl, judge-cache.json, log.txt |
| `verify.py` → `analysis/verify.md`, `verify.json` | the two-part verification, per-run and per-case |

## Repro

```
export PICO=/path/to/pico   # a pico checkout, see the root README
python mine.py && python timelines.py                                   # no model calls
uv run --project "$PICO" --env-file "$PICO/.env" python gate_variant.py "$PWD/runs/gate" pico-001 pico-004 pico-016 --repeat 5
uv run --project "$PICO" --env-file "$PICO/.env" python verify.py       # judge cache reused, the red-justification branch may call the judge
```

## Registered limits

- Three cases, not the 14-case suite. The gate's blast radius is one kind
  of call, and the article names the narrowed regression as its boundary.
- 15 vs 15 runs on the pass-rate line can only see a collapse (Wald
  half-width of the difference about 35 points at p = 0.6).
- The gate sees write_file/edit_file by path and bash by visible write
  forms; a python heredoc opening a test file for writing is not seen and
  would show only in the diff.
- Twelve days between baseline and arm under the same vendor model name;
  a vendor-side change is confounded with the gate.
- Registered aside from the reading: the acceptance probe sits at
  /tmp/accept.py inside the world and is visible to the agent (pico-009-r2
  deleted and rewrote it; pico-012-r3 read it late). Belongs in the 08-26
  fidelity register, not fixed here.
