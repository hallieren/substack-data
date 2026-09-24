# 2026-09-24: the numbers behind "Was Your Agent's Big Find Just Luck?"

Companion data for the article [Was Your Agent's Big Find Just Luck?](https://hallieren.substack.com/p/was-your-agents-big-find-just-luck).
This drop has no experiment of ours. The article explains how Anthropic checked
one autonomous discovery, and every number in its figures is transcribed here
from the preprint so the figures can be checked and rebuilt without reopening it.

Sources:
- Yoon, Athukoralage, Ameisen, Kauderer-Abrams, Perry, Durrant. "Autonomous AI
  agents discover reverse transcriptases with tandem repeat arrays." Anthropic
  preprint, September 2026.
  https://www-cdn.anthropic.com/22573675ada52a8ca8a97a1a4b4326b2f208a071.pdf
- Anthropic. "Claude discovers a novel enzyme system with CRISPR-like repeats."
  23 September 2026. https://www.anthropic.com/news/claude-discovers-novel-enzyme-system
  Used for context only. Its round numbers (950 agents, 210M tokens, 3,500
  candidates, 20 reports) differ from the preprint; the article uses the preprint.

The worked example is the ART repeat array. A harness of Claude Code agents
(worker and supervisor per task, plus curator and editor) searched 1.94 billion
protein clusters for new reverse transcriptase partner genes. A deep dive
rejected one candidate partner, a follow-up the brief never asked for sent a
worker to read the non-coding DNA upstream of related enzymes, and it saw a
tandem repeat array by eye. The authors then ranked the reports, audited the
transcript, reran the campaign ten times (the array was missed every time), and
turned the find into a fixed-input benchmark of 3,500 attempts.

## Layout

- `data/blog02_search_funnel.csv`: the five funnel stages. Feeds the log-scale
  funnel figure.
- `data/blog03_candidate_outcomes.csv`: the 17 promoted partner families by final
  outcome, with members. Feeds the unit chart. The highlighted square is
  Unannotated #506.
- `data/blog04_path_to_art.csv`: the steps from the rejected candidate to the lab,
  with role and number where one exists. Feeds the relay figure.
- `data/blog05_reruns.csv`: the original campaign and the ten reruns on three
  yes/no checks. Feeds the rerun grid. Rerun order is not meaningful.
- `data/blog06_reading_vs_recognition.csv`: recognition with and without tools,
  the share of file attempts that never read 200 contiguous nt, and the
  lowest and highest DNA-read bins. Feeds the two-lane figure.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. Figure 1 of the article is a
schematic of the brief's target versus the ART locus (after the preprint's Fig. 2B)
and carries no numbers. Per-level recognition curves (Fig. 4C to 4H) are shown
only as charts in the preprint; values not stated in its text are not
transcribed. Both the report tournament and the benchmark were graded by
Claude Mythos 5, and the preprint reports no human agreement check.
