# 2026-09-14: the numbers behind "How to Let an Agent Edit Its Own Playbook Without Drifting"

Companion data for the article [How to Let an Agent Edit Its Own Playbook Without Drifting](https://hallieren.substack.com/p/how-to-let-an-agent-edit-its-own).
This drop has no experiment of ours. The article explains one paper, and every
number in its figures is transcribed here from that paper so the figures can be
checked and rebuilt without reopening it.

Source: Yuxing Lu, Yicheng Chen, Shanchan Wu, Sercan Ö. Arık (Google).
"Procedural Graphs: Self-Evolving Execution Structures for LLM Agents."
arXiv 2609.09153v1, 8 September 2026. https://arxiv.org/abs/2609.09153

The worked example is the paper's virtual CFO in EnterpriseArena: monthly
liquidity decisions over up to 132 months, three undisclosed crises, capital
arriving one to six months after it is requested, 20 episodes per split in the
self-evolution study. Survival throughout is full-horizon survival, the share
of the 20 episodes still solvent at month 132 (Appendix C.1), not mean
lifespan. The localization ablation switches to ALFWorld because the paper did
not run it on the CFO task.

## Layout

- `data/blog03_enterprisearena_rounds.csv`: Table 11, the ten rounds of
  self-evolution on the CFO task. Validation full-horizon survival and mean
  lifespan per round, whether the gate kept or rolled back the candidate, test
  survival of kept checkpoints, and the paper's note on what each round
  changed (Appendix E.2 and E.3). Feeds the rounds figure.
- `data/blog04_localization_ablation.csv`: Table 3, the same graph consumed
  four ways (no graph, full graph pasted in, full graph turned into a hint,
  localized two-hop subgraph turned into a hint) on MultiChallenge, GDPval,
  and ALFWorld, with average tokens. The localization figure plots the
  ALFWorld column; the other two are cited in its caption.
- `data/prose_numbers.csv`: every other number the article states, with its
  section, including the survival metric definition and the gate rule.

## What is not here

No trajectories, no scripts, no model calls. The flowchart figure and the
checklist figure are diagrams of the paper's Section 3 and of the article's own
checklist and carry no numbers. The figure HTML lives with the article draft.
All benchmarks were run by the paper's authors. Earlier revisions of this drop
carried the MultiChallenge construction modes (Table 2), the Table 1
confidence intervals, and the Table 8 comparison; the article no longer uses
them, and they remain in git history.
