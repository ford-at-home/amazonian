# Weekly Business Review — 2026-09-14 to 2026-09-20 — ChangeLens

> Worked example. Hypothetical product carried over from `01-working-backwards-prfaq/examples/example-prfaq.md`. Demonstrates the variance classification rule and prior-action review.

---

## Executive Summary

Weekly active EMs slipped from 73% to 64% — first week below the 70% target since launch week 6. Hypothesis: the new "blocked PR" highlight rolled out Tuesday is producing a higher false-positive rate, triggering manager skepticism mid-draft. Action item AI-37 (audit blocked-PR precision on a 100-PR sample) is owned by Eng with a 2026-09-23 due date. Median time-to-publish held at 11 minutes, but fields-edited-per-digest moved out of the 1–4 sweet spot to a median of 5 — same root cause hypothesis.

---

## Input Metrics

| Metric | This week | Last week | Δ | Δ % | Owner |
|--------|-----------|-----------|---|-----|-------|
| Drafts generated | 312 | 318 | −6 | −1.9% | Eng |
| GitHub API error rate | 0.4% | 0.3% | +0.1pp | +33% | Eng |
| Blocked-PR flag fired | 47 | 21 | +26 | +124% | PM |

## Output Metrics

| Metric | This week | Last week | Δ | Δ % | Owner |
|--------|-----------|-----------|---|-----|-------|
| Weekly active EMs (published) | 64% | 73% | −9pp | −12.3% | PM |
| Median time-to-publish (min) | 11 | 12 | −1 | −8.3% | PM |
| Fields edited per digest (median) | 5 | 3 | +2 | +66.7% | PM |
| Manager trust (monthly survey) | 4.1 | 4.1 | 0 | 0% | PM |

## Variance Analysis

| Metric | Variance | Classification | Detail |
|--------|----------|----------------|--------|
| Weekly active EMs | −9pp | Hypothesis | New blocked-PR highlight (Tue release) producing false positives; managers losing trust mid-draft and abandoning. Confirm or refute via AI-37. |
| Fields edited per digest | +2 (above 1–4 sweet spot) | Hypothesis | Same root cause: managers correcting false-positive blocked flags. |
| GitHub API error rate | +0.1pp | Known cause | Brief GitHub incident 2026-09-17 18:00–18:40 UTC. See INC-2026-09-17-01. |
| Drafts generated | −6 | No action needed because… | Within normal variance; smaller than the new-cohort onboarding fluctuation. |

## Known Events

- Blocked-PR highlight feature rolled out 2026-09-15 09:00 ET to 100% of teams.
- GitHub incident 2026-09-17 (status.github.com), ~40 min elevated 5xx. CoE in progress: INC-2026-09-17-01.
- Three new beta teams onboarded Monday (Northbeam, Pelt, Halo Labs).

## RICO

### Risks

- If the blocked-PR false-positive rate stays elevated through next week, weekly active EMs may drop below the 50% cancel threshold for cohort week 3. Severity: `high`. Likelihood: `possible`. Mitigation: feature-flag rollback ready. Owner: Eng.

### Issues

- Blocked-PR false positives in production. Owner: Eng. ETA: 2026-09-23 (after AI-37 audit).

### Challenges

- Pricing question for >50-EM orgs is blocking the Northbeam expansion conversation. Decision needed from Sales by 2026-10-01.

### Observations

- Time-to-publish improved this week despite trust dropping. Hypothesis: managers spending less time because they are giving up rather than because the draft is better. Worth watching, not actioning yet.
- New cohort onboarding rate (3 teams) was the highest since week 4. No clear cause; do not over-attribute.

## Decisions Needed

| # | Decision | Decision-maker | Needed by |
|---|----------|----------------|-----------|
| 1 | Whether to feature-flag-rollback the blocked-PR highlight pending AI-37 results | Eng lead | 2026-09-22 |
| 2 | Pricing tier for >50-EM orgs | Sales | 2026-10-01 |

## Action Items (this week)

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| AI-37 | Audit blocked-PR precision on a 100-PR sample, report false-positive rate | Eng | 2026-09-23 | open |
| AI-38 | Draft >50-EM pricing options memo | Sales | 2026-09-26 | open |
| AI-39 | Add "report false positive" inline action to blocked-PR flag | Eng | 2026-09-30 | open |

## Prior Action Items Review

| # | Action (from 2026-09-13) | Owner | Original due | Status |
|---|--------------------------|-------|--------------|--------|
| AI-34 | Onboard 2 new beta cohorts | PM | 2026-09-20 | done (3 onboarded) |
| AI-35 | Fix Linear webhook race condition | Eng | 2026-09-18 | done |
| AI-36 | Run trust survey for cohort 2 | PM | 2026-09-19 | slipped — now due 2026-09-22 |

> AI-36 re-justified: survey tool (Typeform) was down two days; survey ready to send 2026-09-22.
