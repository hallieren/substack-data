# 2026-08-20: Error analysis of the 107 sealed-run failures (ch03)

Chapter 3 of [AI Agent Evaluation](https://github.com/hallieren/ai-agent-evaluation) executed on pico's sealed SWE-bench Verified run: every one of the 107 failing trajectories read forward, coded with a `first_bad_step`, clustered into a failure mode atlas.

Source run: [`../2026-08-16/runs/20260815-sealed/`](../2026-08-16/) (393 resolved / 107 unresolved, 78.6%). Trajectories: `../2026-08-16/trajs/pico-swebench-verified-sealed-20260815.tar.gz`.

## Files

| File | What it is |
|---|---|
| `trace_review_form.csv` | The coding sheet: one row per failing trace (107), in pre-registered random coding order. Columns include `first_bad_step`, phase, final failure mode, blame side, a behavioral one-line description, a verbatim evidence quote, and the adversarial-adjudication outcome. |
| `CODING_PROTOCOL.md` | The protocol every coder followed: forward reading, first bad step only, behavior not speculation, one primary failure per trace, honest exam-side option. |
| `coding_order.json` | The seeded shuffle (seed 42) fixed before any coding; the saturation curves are computed over this order. |
| `agent_modes.json` | The hand-made clustering of the 60 first-pass agent-side rows into modes M1-M8 (4 more arrived via adjudication overturns). |
| `adjudications.json` | The adversarial second review of all 47 exam-side/unclear calls: 43 upheld (37 spec-underdetermined, 6 grading-machinery), 4 overturned to the agent. |
| `final_modes.json` | Final mode label per trace after adjudication. Totals: agent-side 64 (M1 17, M4 17, M2 9, M3 8, M5 5, M6 4, M7 3, M8 1), exam-side 43 (E1 37, E2 6). |
| `control_group_rows.json` | The 12-trace passing control sample, coded with the same discipline: wrong turns and recovery mechanisms. |
| `render_dossiers.py` | Renders each trajectory into the step-numbered dossier the coders read (endpoint facts + trajectory + submitted patch + gold patch). |

## Method notes

- Coding was performed by Claude subagents under the written protocol; clustering and mode naming by hand. All exam-side calls passed an adversarial review instructed to overturn them by default. The walkthrough exhibit (django__django-11885) was hand-checked step by step against the raw trajectory.
- Gold patches, test patches, and difficulty annotations come from princeton-nlp/SWE-bench_Verified and were used only as the analyst's answer key; the sealed agent never saw them.
- Byte-identical-patch claims (sphinx-doc__sphinx-8595, django__django-10097) verified mechanically: normalized changed-line similarity 1.000 between submitted `patch.diff` and the gold patch.
