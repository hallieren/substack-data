# 2026-08-31 · Cross-session memory eval, Alexa for Shopping

Companion data for the article on evaluating agent memory (Chapter 10 of [AI Agent Evaluation](https://hallieren.github.io/ai-agent-evaluation/chapters/ch10-memory/)). The subject is Amazon's Alexa for Shopping assistant, which keeps a user profile across conversations. Four brand-new conversations were run back to back on one morning: a baseline probe, a write-only conversation (five corrections plus two price alerts), and two read-only conversations with no hints. The unit of evaluation is the whole four-conversation stretch, not any single reply.

## Layout

- `questions.md` — the 29 questions verbatim, the execution rules, and a map from each question to the memory mechanism it probes.
- `results.md` — the full transcript: every question, every reply verbatim, observed side effects, session timestamps.
- `evidence/` — screenshots of the assistant panel at the four session boundaries.

## Headline results

- **Forgetting (write path): fail.** The trip-date update (Sep 14 → Sep 5) was enthusiastically confirmed, then never reached memory. The budget update sent seconds earlier ($1,300 → $900) held everywhere. The end-of-session self-audit already exposed the loss.
- **Crosstalk and missed recall (read path): pass.** Alerts on two lookalike models ($950 on the ZV-E10 II, $600 on the original ZV-E10) never swapped; planted owned gear was recalled and excluded from a built kit.
- **Consistency: fail on a fact field.** The same verbatim recommendation question in three conversations returned three different cameras, which is treated as sampling, not a defect. The failure is factual: the budget on file was $900, yet one answer claimed a "$900–$1,300 range" that appears in no conversation.
- **Self-reports vs actions.** The assistant set, listed, and deleted the alerts correctly throughout, while twice denying it had that data or that ability. Audit memory against the action log, not the agent's self-report.
- **Deletion.** Asked to forget, it stated it cannot delete stored profile data from within a conversation, only stop referencing it for the session.

## Notes

- Personal identifiers are redacted: the account holder's name appears as `[name]`, the inferred location as `[city]`; the same redaction is applied to the screenshots. Everything else is verbatim.
- Product prices are as displayed inside the assistant's replies at run time.
- The assistant is a black box; this is a single-morning sample of one product, run under a fixed ask-and-record protocol with no judging in the loop.
