# 2026-09-14: the numbers behind "How to Let Your Agent Rewrite Its Own Playbook"

Companion data for the article [How to Let Your Agent Rewrite Its Own Playbook](https://hallieren.substack.com/p/how-to-let-your-agent-rewrite-its-own).
This drop has no experiment of ours. The article explains one paper, and every
number in its figures is transcribed here from that paper so the figures can be
checked and rebuilt without reopening it.

Source: Yuxing Lu, Yicheng Chen, Shanchan Wu, Sercan Ö. Arık (Google).
"Procedural Graphs: Self-Evolving Execution Structures for LLM Agents."
arXiv 2609.09153v1, 8 September 2026. https://arxiv.org/abs/2609.09153

The single worked example throughout is the paper's virtual CFO in
EnterpriseArena: monthly liquidity decisions over up to 132 months, three
undisclosed crises, capital arriving one to six months after it is requested,
20 episodes per split in the self-evolution study.

## Layout

- `data/blog01_multichallenge_modes.csv`: Table 2 / Table 10, MultiChallenge
  overall success for the unguided agent and the five playbook construction
  modes. Feeds figure 1. "One offline static update" is the paper's Mode 2,
  which Section 5.3 calls "a single offline update"; the formal mode
  definitions in Appendix D.2 did not survive the HTML conversion we read.
- `data/blog04_enterprisearena_rounds.csv`: Table 11, the ten rounds of
  self-evolution on the CFO task. Validation full-horizon survival and mean
  lifespan per round, whether the gate kept or rolled back the candidate, test
  survival of kept checkpoints, and the paper's note on what each round
  changed (Appendix E.2 and E.3). Feeds figure 4.
- `data/prose_numbers.csv`: every other number the article states, with its
  section.

## What is not here

No trajectories, no scripts, no model calls. Figures 2, 3, and 5 are diagrams
of the paper's Section 3 and Algorithm 1 and carry no numbers beyond the
20-episode split size. The figure HTML lives with the article draft. All
benchmarks were run by the paper's authors; the MultiChallenge score is an
LLM judge's.
