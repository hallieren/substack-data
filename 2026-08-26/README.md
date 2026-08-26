# 2026-08-26: the seed eval set runs for the first time (ch07 follow-along)

Companion data for the article "给 agent 造一个可以砸的世界". Method:
*AI Agent Evaluation* ch07 — sandbox, minimal harness, replay layering —
applied to pico, continuing the 2026-08-21 case set.

## Layout

- `harness/` — the six components (runner / traces / assertions / judge /
  stats / report, 614 lines) + `cases.py` loader, `verify_accept.py`
  pre-flight, and `SPEC.md` (architecture spec, stub/real boundary table,
  fidelity gap register).
- `accept/` — one acceptance bundle per case: `accept.py` (exit 0 = met,
  1 = not met, else = probe broken) + `meta.json` (declared suites, surfaces,
  setup). Policy P1: derived from issue text only, never the maintainer patch.
  `CONTRACT.md` is the authoring contract.
- `issues/` — the extracted issue texts (problem_statement only) + meta.
- `runs/verify-accept.json` — pre-flight: all 14 accept scripts red (exit 1)
  on their unfixed worlds; every world rebuilt twice with identical content
  hashes (`reset_identical`).
- `runs/full/` — the run: 14 cases × 5 repeats, $2.27 total.
  `results.jsonl` (one row per run), `trajs/` (pico-1 trajectories),
  `world/` (per-run world probes: accept exits, baseline/post suite
  failures, patch), `judge-cache.json` (judge-red-justification votes),
  `report.md` (the layered report the article quotes).

## Repro

```
cd pico && uv run python <here>/harness/verify_accept.py          # no model calls
cd pico && uv run python <here>/harness/runner.py runs/full --repeat 5
cd pico && uv run python <here>/harness/report.py runs/full --repeats 5
```

Holdout cases (pico-003/010/013/018) were not run (ch04 policy: release
evals only).

## Registered caveats

See `../daily`-side evidence README (preregistration) and `harness/SPEC.md`:
narrow declared suites (lenient direction), claims_backed regex floor,
two accept scripts with structural probes beyond the issue's literal words
(pico-002, pico-012), and one P1 grey-zone disclosure (pico-012 authoring).
pico-017's "doomed" premise did not hold empirically — an exam-side finding,
kept as-is in the data.
