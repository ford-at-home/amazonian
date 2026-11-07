# PRFAQ — <idea_name>

> Working Backwards artifact. Fill every section. Empty sections fail review.
> Tag every claim inline: `[fact]`, `[assumption]`, `[inference]`, `[open question]`.

---

## Press Release

**Headline:** <customer outcome in plain language, past tense>

**Subheadline:** <one sentence: who benefits, how>

**<City>, <Date>** — <Company> today announced <product or feature>. <One paragraph: what it is, who it is for, the problem it removes.>

<Paragraph: what life looked like before. The customer's pain in concrete terms.>

<Paragraph: what life looks like now. The specific change the customer experiences.>

> "<Quote from a leader at the company. One sentence on why this matters.>"
> — <Name>, <Title>, <Company>

> "<Quote from a representative customer. Sounds like a person, not marketing copy. Mentions the specific outcome they got.>"
> — <Name>, <Role>, <Customer Org>

To learn more or get started, visit <URL>.

---

## Customer FAQ

> Questions a real customer would ask on launch day. 5–10 Q&A. Plain language.

**Q: <Question 1>**
A: <Answer.>

**Q: <Question 2>**
A: <Answer.>

**Q: <Question 3>**
A: <Answer.>

---

## Internal FAQ

> Questions a leadership reviewer will ask. 8–15 Q&A. Dodging any of these is a failed review.

**Q: What did we consider and reject?**
A: <Specific alternatives, with the reason each was rejected.>

**Q: What happens if we do nothing?**
A: <Concrete consequence, with a number where possible.>

**Q: What is the largest risk?**
A: <The one that would kill the project.>

**Q: Why now?**
A: <What changed in the market, technology, regulation, or customer behavior that makes this the right moment.>

**Q: Why us?**
A: <The team's unfair advantage, or honest acknowledgement of where there is none.>

**Q: What does it cost?**
A: <Engineering effort, infrastructure, vendor, opportunity cost.>

**Q: What is the rollout plan?**
A: <Stages, gates, blast-radius limits.>

**Q: How will we know it is working?**
A: <Reference the success metrics below.>

**Q: How will we know it is failing?**
A: <The metric or signal that triggers a rollback or pivot.>

**Q: What is explicitly out of scope?**
A: <Reference the MVP boundary.>

---

## MVP Boundary

### In scope (v1)

- ...
- ...

### Out of scope (explicit)

- ...
- ...
- ...

> Out-of-scope must list at least three items. "We will not also do X" is a feature, not an omission.

---

## Success Metrics

| Metric | Baseline | Target | How measured | Time to evaluate |
|--------|----------|--------|--------------|------------------|
|        |          |        |              |                  |

> Every target must be measurable within 90 days of launch.

---

## Risks

> Severity and likelihood use the canonical scales from `GLOSSARY.md#severity-and-likelihood`.
> Severity: `catastrophic` | `high` | `medium` | `low`. Likelihood: `likely` | `possible` | `unlikely` | `speculative`.

| Risk | Severity | Likelihood | Mitigation | Owner |
|------|----------|------------|------------|-------|
|      |          |            |            |       |

---

## Decision Recommendation

**Recommendation:** <proceed | proceed_with_changes | do_not_proceed | needs_more_info>

**Rationale:** <Short paragraph. Reference the strongest evidence and the largest risk. A `proceed` recommendation paired with any `catastrophic + likely` or `catastrophic + possible` risk that lacks a documented mitigation is incoherent; revise the recommendation or mitigate the risk before submission.>

---

## Open Questions

| # | Question | Owner | Due |
|---|----------|-------|-----|
| 1 |          |       |     |

> Questions answerable with one phone call should be answered before submission, not listed here.

---

## Assumption Labels

Tags used inline above:

- `[fact]` — verifiable, with a source
- `[assumption]` — believed true, untested
- `[inference]` — derived from facts above
- `[open question]` — listed in the Open Questions table
