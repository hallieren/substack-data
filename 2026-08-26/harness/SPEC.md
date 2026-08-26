# Harness Architecture Spec — pico (ch07 loot #1)

Adopted 2026-08-26. Three rulings per ch07's Decision section.

## 1. The six-component data flow

```
case(YAML, ch04) ──> runner ──> trace(JSONL, ch02 schema) ──┬──> assertions(ch05 floor) ──┐
                       │                                    │                             ├──> stats(ch06) ──> report(ch02)
                       │                                    └──> judge(ch05, red-just.) ──┘
                       └── world(sealed SWE-bench container)
```

No synth component: the persona axis does not travel to a coding agent (ch04
ruling); its replacement, the test-coverage-state axis, lives in the world,
not in a counterparty. The six components contain no Django/astropy/SWE-bench
knowledge; all world knowledge lives in `world` (the container + per-case
accept bundles).

## 2. Stub / real-call boundary table

| tool / dependency | stub or real | mechanism | why |
|---|---|---|---|
| bash, read_file, write_file, edit_file | real tool, sandbox world | docker exec in sealed container | irreversible only inside a throwaway world; reset = fresh container |
| outbound network | sealed off | `--network none` | the coding agent's send_email: nothing may leak out |
| git history | sealed | timesafe seal (2026-08-15) | the future refs were an answer channel; leniency here inflated scores |
| repo test suite | real | runs in container | it is the world's own physics, and a ready-made assertion layer |
| model API | ALWAYS real | provider call | the model is the thing under test; stub it and the eval tests itself |

Fidelity gap register (sandbox assumptions vs a real dev environment), one
known gap per row, ch07 anti-self-deception rule:

| sandbox assumption | real-world behavior | gap | verdicts affected |
|---|---|---|---|
| no network | real dev work fetches docs/packages | tasks needing lookup undertested | accept_green (false red risk on lookup-dependent fixes) |
| suites = declared narrow labels | a real CI runs everything | regressions outside declared suites invisible | no_regression_in_touched_suites (lenient — the fatal direction) |
| x86 emulation timing | native speed | timeouts fire earlier than production | terminates_with_report (false budget-death) |
| claims_backed regex floor | humans read the claim in context | subtle unbacked claims pass | claims_backed (lenient) |

## 3. Replay / simulation layering

- Level 1 (verdict replay, zero model calls): `report.py <run_dir>` re-judges
  stored traces byte-deterministically. Used every time an assertion changes.
- Level 2 (fixed-input rerun, deterministic environment): `runner.py` — same
  case, same seed world, same seal; the model re-reasons. This run IS level 2
  ×5 repeats. Variance that remains is the agent's own (ch06).
- Level 3 (free simulation): not applicable without a live counterparty;
  for pico the exploratory tier is new worlds, not new dialogue.
- Iron rule: deviation raises an alarm, never a forced verdict — a run whose
  world breaks (accept green pre-fix, broken probe, container failure) is
  flagged `world invalid` and never scored as an agent verdict.

## 4. Build or buy

Built (a few hundred lines; the building is the course). Trace schema is
pico-1, mappable to OTel GenAI conventions; migration to a platform stays
open.
