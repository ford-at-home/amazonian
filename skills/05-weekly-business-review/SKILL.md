---
name: weekly-business-review
description: Generate a Weekly Business Review (WBR) from metrics and operating notes. Connects input metrics, output metrics, week-over-week variance, risks, issues, challenges, observations, and action items. Enforces that every negative variance maps to a specific cause or action. Use when the user mentions "WBR", "weekly review", "metrics review", "ops review", or when preparing a recurring metrics meeting.
category: constructive
required_reviews: []  # cadence-driven; reviewer friction harms weekly rhythm
---

# Weekly Business Review

Generate a WBR that connects inputs to outputs and turns variance into action. The WBR is not a status report; it is an inspection mechanism. Every negative variance must map to a cause or an action — no exceptions.

## Quick start

1. Collect this week's metrics and prior-week comparisons.
2. Run the variance analysis: every negative move must be classified.
3. Use [`wbr-template.md`](wbr-template.md) for the section structure.
4. Emit the WBR with explicit action items, each with an owner and a date.

## When to use

- The team holds a recurring metrics review.
- A WBR is overdue and needs assembling.
- A new mechanism produced by `mechanism-designer` needs its first inspection report.
- The user mentions: "WBR", "weekly review", "metrics review", "ops review", "weekly business review".

## When NOT to use

- The decision being made is one-time. Use `six-page-narrative`.
- The artifact needed is a post-incident review. Use `correction-of-errors`.
- The metrics have not been defined. Use `working-backwards-prfaq` or `mechanism-designer` to define them first.

## Inputs

```yaml
input_metrics:                # leading indicators the team controls
output_metrics:               # lagging indicators the customer experiences
week_over_week_changes:       # current week vs prior week
known_events:                 # planned changes, releases, holidays, outages
risks:                        # things that could harm metrics
issues:                       # things that ARE harming metrics
challenges:                   # things requiring decisions
observations:                 # noticed patterns without a clear action yet
action_items:                 # from prior WBRs, with status
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Every negative variance classified | Each maps to: Known cause / Hypothesis / Unknown / No action needed because… / Action item created | Classify the unclassified |
| No "trending" without numbers | Each direction claim has a magnitude | Add the number |
| Action items have owner + date | Every action item has both | Demand them |
| Inputs and outputs distinguished | Input metrics are not mixed with outputs in the same table | Re-sort |
| Prior actions reviewed | Last week's action items are reviewed with status | Add the review |

## Process

1. **Pull** input and output metrics for the period and the prior period.
2. **Compute** week-over-week variance.
3. **Classify** every negative variance (see hard rule below).
4. **Capture** known events that explain variance.
5. **Review** prior week's action items.
6. **Draft** RICO: Risks, Issues, Challenges, Observations.
7. **Decide** what decisions are needed and from whom.
8. **Assign** action items with owners and dates.
9. **Emit** the WBR.

## Hard rule (non-negotiable)

Every negative variance must map to exactly one of:

```text
Known cause
Hypothesis
Unknown
No action needed because…
Action item created
```

"Unknown" is acceptable for one week. Two weeks of "unknown" on the same metric is a process failure and should trigger `correction-of-errors` on the inspection mechanism itself.

## Output schema

```markdown
# Weekly Business Review — <date range>

## Executive Summary
<3–5 sentences. The single most important variance this week and what is being done about it.>

## Input Metrics
<table>

## Output Metrics
<table>

## Variance Analysis
<one row per negative variance, with classification>

## RICO

### Risks
### Issues
### Challenges
### Observations

## Decisions Needed
<what the reviewer is being asked to decide>

## Action Items
<owner, action, due date, status>

## Prior Action Items Review
<status of last week's items>
```

See [`wbr-template.md`](wbr-template.md). See [`examples/example-wbr.md`](examples/example-wbr.md) for a worked example.

## Stop conditions

- Metrics for the prior period are missing or inconsistent.
- A metric is defined but no one knows how it is measured.
- The variance table is empty *and* the executive summary claims "everything is fine".

## Failure modes

- **Status-report drift.** The WBR becomes a list of what people did. Discard verbs that describe activity; keep numbers that describe outcomes.
- **Variance hand-waving.** "Up a bit", "down slightly". Require numbers.
- **Action-item amnesia.** Action items are created and then never reviewed. The "Prior Action Items Review" section is the only protection.
- **Hero culture.** A metric saved by individual heroics is not a healthy metric. Note the heroics in Observations.
- **Cumulative-good-news skew.** Every report says everything is fine. Inspect the inspection mechanism via `correction-of-errors`.

## Follow-up mechanism

- A persistent negative variance triggers `correction-of-errors`.
- A new persistent pattern feeds into `working-backwards-prfaq` for a structural fix.
- Decisions needed feed into `six-page-narrative` when significant enough.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: `success_metrics` → `input_metrics` / `output_metrics` (caller classifies leading vs lagging)
- `mechanism-designer`: `mechanism.outputs` + `mechanism.inputs` → `input_metrics` / `output_metrics`; `mechanism.inspection_method` defines the WBR's structure
- Prior WBR: previous `action_items` → this week's `action_items` (with status)

**Feeds into**

- `correction-of-errors`: persistent negative variance on a metric → `contributing_factors` / `prior_incidents`
- `working-backwards-prfaq`: pattern requiring a structural fix → new PRFAQ
- `six-page-narrative`: a decision surfaced in "Decisions Needed" → `decision_needed`
- `tenets-review`: persistent variance the WBR cannot resolve at its cadence → `review_trigger: metric_anomaly` + `trigger_detail`
- `ambitious-goal-grading`: aggregated period actuals → `period_goals[].actual`; variance classifications provide context to misses
- `dissent-before-commit`: recent variance, anomalies, or unresolved action items → `state_changes_since_authoring`

Enums used: `variance_classifications`, `metric_types`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml).

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
