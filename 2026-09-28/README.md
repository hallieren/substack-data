# 2026-09-28: the numbers behind "Is Your Top-Scoring Version Really Better?"

Companion data for the article [Is Your Top-Scoring Version Really Better?](https://hallieren.substack.com/p/is-your-top-scoring-version-really).
This drop has no experiment of ours. The article explains one paper on
self-improving coding agents, and every number in its figures is transcribed
here from the paper so the figures can be checked and rebuilt without
reopening it.

Source: Xinghong Fu (MIT), Aravinth Kulanthaivelu, Yutaro Yamada (Sakana AI).
"Self Improvement via Fast Tree-search" (SIFT). arXiv:2609.19526v1, 17
September 2026. https://arxiv.org/abs/2609.19526 (full HTML text read at
https://arxiv.org/html/2609.19526v1; a local copy is in the article's
folder). Prompt listings in Appendix B.2 and tool schemas in B.5 were not
rendered in that copy and are not transcribed.

The worked example is the paper's TerminalBench 2.1 run. The coding model,
gpt-5-mini, stays fixed while an improver model, gpt-5, rewrites its prompt
and tools for 30 rounds. Each new version gets two verdicts: a quiz, a fixed
50-task subset run once for one score, and a judge, gpt-5.4-high, that reads
the full post-change code of two versions side by side, never sees the tasks
or scores, and is compared pairwise against the ten strongest incumbents
each round, with wins pooled by a Bradley-Terry model. At the end, the
starting version, the version with the best quiz score, and the judge's
first pick were each run on the full 89-task benchmark three times. The best
quiz score (19/50) came in at 28.1%, below the 29.2% start; the judge's
first pick (18/50) reached 36.7%, the best of the run. Reading the code, the
judge caught what no quiz score showed: a self-check gated behind a flag
that is off by default, and a rewritten shell tool that opens a fresh shell
on every call despite claiming to keep state.

## Layout

- `data/blog02_quiz_vs_full_exam.csv`: Table 4, the search-eval quiz score
  (of 50) and the repeated full-benchmark mean (% of 89, three runs) for the
  starting agent, the judge's first pick, the run's best quiz score, and the
  no-judge ablation's best quiz score. Feeds the two-panel bar figure
  (v2-blog-02.png).
- `data/blog03_swe60_reruns.csv`: Table 7, node 11 of the no-judge ablation
  on SWE-60, the search-time score plus three full reruns and their mean.
  Feeds the dot-strip figure (v2-blog-03.png).
- `data/blog04_judge_qualitative.csv`: section 4.3, what the judge found
  reading the code of the best quiz score versus its own first pick on
  TerminalBench, with the judge's quoted phrases. Feeds the two-column
  comparison figure (v2-blog-04.png).
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. Figure 1 of the article
(v3-blog-01.png) is a schematic of the improvement loop, the quiz box and
the judge box, and carries no plotted numbers; the process facts it names
(30 rounds, the 50-task quiz, the gpt-5-mini/gpt-5/gpt-5.4-high models) are
in `prose_numbers.csv` instead. The paper's Polyglot results (section 4.1,
Table 1 to Table 3, Figure 4 transfer plots) and its Bradley-Terry
diagnostics, speedup breakdowns and node lineage (Figures 5 to 9) are not
used by the article and are not transcribed. All four figures used in the
article are original artwork rendered from figures/index.v2.html and
figures/index.v3.html, not third-party images.
