# PRFAQ — ChangeLens

> Worked example. Hypothetical product, not real.
> Demonstrates assumption tagging, honest uncertainty, and explicit out-of-scope.

---

## Press Release

**Headline:** ChangeLens turns a week of engineering activity into a five-minute status update.

**Subheadline:** Engineering managers stop spending Friday afternoons reconstructing what their teams shipped.

**Brooklyn, NY, June 3, 2026** — ChangeLens today launched a private beta of its weekly status digest for engineering teams. ChangeLens watches a team's GitHub, Linear, and (optionally) Slack activity and produces a structured weekly summary covering what shipped, what stalled, and what is blocked — sourced from the work itself, not from a survey.

Before ChangeLens, an engineering manager at a 25-person team spent an average of 87 minutes per Friday assembling a status report by reading commits, scrolling Slack, and asking individual engineers what they did `[assumption — survey of 14 EMs, n is small]`. The output was usually wrong by Monday because something else broke over the weekend.

With ChangeLens, the same manager opens a pre-drafted digest Friday morning, edits it in place, and ships it before lunch. The data is sourced from the systems of record, so corrections happen once instead of three times.

> "We measured 87 minutes per manager per week. Across our 11 engineering managers, that is nine hours of senior IC time we were burning on a deliverable nobody trusted. ChangeLens cut that to under 12 minutes per manager."
> — Priya Shah, VP Engineering, Northbeam (private beta participant)

> "I used to keep a Notion doc open all week and jot things down so I would not forget. I still forgot. Now my draft is already there and I just argue with it for ten minutes."
> — Tom L., Engineering Manager, Northbeam

ChangeLens is available in private beta. Visit changelens.dev to request access.

---

## Customer FAQ

**Q: What does ChangeLens actually do?**
A: It connects to your GitHub org and your Linear workspace. Every Friday at 9 a.m. local time, it produces a structured status digest for each engineering manager covering: what shipped this week, what is in review, what is blocked, who is unblocked but stalled, and what slipped from last week's plan.

**Q: Who edits the digest before it goes out?**
A: You do. ChangeLens never sends anything externally. The digest opens in your team's tool of choice (Notion, Confluence, or markdown) and you review and edit before sharing.

**Q: What if my team uses Jira instead of Linear?**
A: Jira is on the v2 roadmap `[assumption]`. v1 ships with GitHub Issues and Linear.

**Q: Does it read private repos?**
A: Yes, with the GitHub App permissions you grant. It never reads code contents — only PR titles, descriptions, labels, review state, and merge events.

**Q: How accurate is the "blocked" detection?**
A: ChangeLens flags a PR as blocked if it has been in review for 5+ business days with no merge. In the private beta, this matched the team's own understanding 78% of the time. The remaining 22% required a human edit. `[fact — private beta, n=11 EMs, 6 weeks]`

**Q: What does it cost?**
A: $19 per engineering manager per month. No charge per IC. Free for teams of 5 or fewer.

**Q: Does my data leave my infrastructure?**
A: ChangeLens stores GitHub and Linear metadata it has pulled. It does not store source code. Full data residency options are available on the team plan. `[open question — exact list of regions, see Open Questions]`

---

## Internal FAQ

**Q: What did we consider and reject?**
A: (1) A Slack bot that asks each engineer "what did you do this week?" — rejected because it adds tax on ICs and the answer quality is poor. (2) A GitHub Action that posts a weekly summary to a channel — rejected because it does not aggregate across repos or compare to last week's plan. (3) An LLM that reads commits and writes a paragraph — this is what ChangeLens is, but with structure and gates instead of a wall of prose.

**Q: What happens if we do nothing?**
A: Engineering managers continue to spend 60–90 minutes per week on a deliverable they distrust. We have directional data on this from 14 EMs `[assumption — small n]`. The cost is real but slow-burn; nobody will quit over it, but it taxes the most expensive people in the org.

**Q: What is the largest risk?**
A: The digest is wrong in a way the manager does not catch, and a downstream consumer (the CTO, the board) makes a decision based on the bad summary. Mitigation: digests are clearly marked as drafts requiring human review before sharing; we never auto-send. We will measure "fields edited before sharing" as a leading indicator of trust.

**Q: Why now?**
A: Two things changed in 2025–2026: (1) LLM cost dropped enough that structured summarization of a week of PR and issue activity costs ~$0.12 per team per week `[fact — internal cost test]`; (2) GitHub Apps gained fine-grained permissions in 2024, removing the "give us your whole org" objection that killed earlier attempts at this category.

**Q: Why us?**
A: The two founders ran engineering at companies with 50+ engineers and built three internal versions of this tool. The unfair advantage is calibration on what an EM actually wants to read on Friday morning, not distribution. `[assumption — needs market validation beyond private beta]`

**Q: What does it cost to build?**
A: 2 engineers × 14 weeks for v1 (GitHub + Linear + Notion export). Estimated $180k loaded cost. Infrastructure is ~$400 per month at 100 teams.

**Q: How will we know it is working?**
A: See success metrics below. Headline: median time-to-publish drops from 60+ minutes to under 15.

**Q: How will we know it is failing?**
A: If fewer than 30% of beta teams publish their digest in week 4, we have built a tool that does not fit the workflow. Pull the cord.

**Q: What is explicitly out of scope for v1?**
A: See MVP Boundary.

---

## MVP Boundary

### In scope (v1)

- GitHub org integration (PRs, issues, reviews)
- Linear integration (issues, status, assignees)
- Markdown and Notion export
- Per-EM weekly digest, configurable schedule
- Manager-facing edit UI

### Out of scope (explicit)

- Jira integration (v2)
- Slack channel reading (v2; deferred for privacy review)
- Auto-publishing to external channels (we will never do this in v1)
- IC-facing surveys
- Multi-team rollups (org-wide views)
- Custom metrics or OKR tracking

---

## Success Metrics

| Metric | Baseline | Target | How measured | Time to evaluate |
|--------|----------|--------|--------------|------------------|
| Median time-to-publish per EM | 87 min `[assumption, n=14]` | < 15 min | In-app timer + survey | 6 weeks post-launch |
| Weekly active EMs (published a digest) | 0 | 70% of paying EMs | Server-side | Week 4 of each cohort |
| Manager-reported trust (1–5) | n/a | ≥ 4.0 median | Monthly survey | 12 weeks post-launch |
| Fields edited per digest | n/a | 1–4 (sweet spot) | App telemetry | Continuous |

> "Fields edited" being too low (0–1) means the manager did not read it; too high (5+) means the draft was bad. We watch the distribution, not the mean.

---

## Risks

| Risk | Severity | Likelihood | Mitigation | Owner |
|------|----------|------------|------------|-------|
| Digest is wrong, decision-maker acts on it | 5 | 2 | Explicit "draft, review before sharing" framing; never auto-send | PM |
| GitHub revokes or limits the App permission scope | 4 | 2 | Maintain a fallback to read-only token | Eng lead |
| LLM cost spikes break unit economics | 3 | 3 | Cap tokens per digest; cache aggregates | Eng lead |
| EM workflow does not tolerate "another tool" | 4 | 3 | Notion and markdown export means it lives where their docs already live | PM |
| Privacy review delays Slack integration past v2 | 2 | 4 | Slack is already out of scope for v1 | PM |

---

## Decision Recommendation

**Recommendation:** proceed_with_changes

**Rationale:** The customer problem is real and measurable, the technical approach is de-risked by recent LLM cost drops and GitHub permissions changes, and the private beta produced strong directional signal. Recommended changes: tighten the success metric on trust (require 4.0 median, not 3.5), and explicitly defer Slack ingestion to v2 so v1 ships in 14 weeks instead of 20.

---

## Open Questions

| # | Question | Owner | Due |
|---|----------|-------|-----|
| 1 | Final data residency regions (EU? CA?) | Legal | Pre-launch |
| 2 | Pricing for >50 EMs at a single org (enterprise tier?) | Sales | Week 6 of beta |
| 3 | Whether Linear and GitHub Issues can share a unified "issue" model or need separate code paths | Eng lead | Week 2 of build |

---

## Assumption Labels

Tags used inline above:

- `[fact]` — measured or sourced, see private beta data
- `[assumption]` — believed true, untested at scale (sample size or generalization issue)
- `[inference]` — derived from facts in this doc
- `[open question]` — see table above
