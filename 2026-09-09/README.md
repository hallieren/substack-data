# 2026-09-09: the numbers behind "Are You Scoring Your Agent's Brain or Its Shell?"

Companion data for the article [Are You Scoring Your Agent's Brain or Its Shell?](https://hallieren.substack.com/p/are-you-scoring-your-agents-brain-or).
This drop has no experiment of ours. The article explains one paper, and
every number in its four figures is transcribed here from that paper so the
figures can be checked and rebuilt without reopening the PDF.

Source: T. J. Barton, C. Constantakis, P. Hauseman, A. Mous, A. Hoffman,
B. Bergeron, H. Goodreau. "What LLM Trading Agents Actually Do in Production:
A Six-Month, Population-Scale Record from Two Fleets." arXiv:2609.05663,
2026-09-09. https://arxiv.org/abs/2609.05663

## Layout

- `data/table3_volatility_sextiles.csv`: the paper's Table 3, 6,400 closed
  DXAP positions (Jun 8 to Jul 24) in six buckets by entry-time volatility.
  Feeds figure 2 (six kinds of weather, one speed).
- `data/capture_gap.csv`: Sec. 6.1 and 6.2, positions that reached +300 bps
  of favorable excursion within 24h and what happened to them, plus the
  2%/4% bracket result. Feeds figure 3. The 37.4% middle share is derived,
  100 minus 49.3 minus 13.3.
- `data/harness_levers.csv`: Sec. 4.1, 4.2 and 5.3, the operating-layer
  effects quoted in figure 1 and the prompt-side null.
- `data/model_league.csv`: Sec. 8.4, the paired replay of three frontier
  models. The paper names claude-fable-5 and qwen3.7-plus and refers to
  "the qwen3.7 pair"; the third model's exact id is not given in the text.

## Unit conversions used in the article

1 bps = 0.01%. So 300 bps = 3%, 39.0 bps = 0.39%, and the 1.1 bps regret
span across models = 0.011%. Hourly volatility of 30.8 to 175.2 bps is
0.3% to 1.75% an hour. The "8.75% of equity per hour" line multiplies 1.75%
by 5x leverage.

## What is not here

No trajectories, no scripts, no model calls. The figure HTML lives with the
article draft. Anything not in the paper's text or Table 3 was not used.
