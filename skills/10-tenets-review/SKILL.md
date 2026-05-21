---
name: tenets-review
description: Stress-test whether a product or initiative is still worth pursuing by checking its tenets ("if we're wrong about X, stop") against current external context and metrics. Emits one of continue / kill / pivot / escalate. Refuses to let metrics speak for the thesis — the named failure mode is metric satisficing, where output metrics sit within target while the underlying bet has collapsed. Use when external context shifts, on annual review, or when the user mentions "tenets review", "kill criteria", "thesis check", "should we still be doing this", or "pivot or kill".
category: interrogative
---

# Tenets Review

Stress-test whether a bet's original thesis is still worth pursuing. Checks each product tenet against external evidence — not just metrics. Refuses to confirm a continue when any tenet is invalid. The named failure mode is **metric satisficing**: metrics look fine while the underlying thesis has collapsed.

This skill is interrogative and event-driven. It is *not* a recurring quarterly review with a fixed cadence — that role is filled by `weekly-business-review` (operational) and by an annual variant if needed. Tenets-review fires when external context shifts or a tenet's validity becomes questionable.

## Quick start

1. Collect the inputs. `product_tenets` may be absent; if so, the skill synthesizes them from the PRFAQ rationale and flags them `[inference]` requiring ratification.
2. Identify the `review_trigger`. A review without a trigger risks becoming theater.
3. Check each tenet's validity against `external_context_changes`, not against metrics. Metrics are a secondary check.
4. Run the metric-satisficing check: if external context contradicts a tenet but metrics look fine, the tenet is `invalid`, not `valid`.
5. Emit the bet recommendation. `continue` requires zero `invalid` tenets.

## When to use

- An external context shift has occurred (market change, regulatory change, competitor move, technology shift) and the question is whether the bet is still valid.
- A tenet's validity has been openly questioned by someone close to the work.
- The bet is approaching an annual review and no one has asked "should this still exist?" in a year.
- A persistent metric anomaly that `weekly-business-review` cannot resolve at its cadence.
- The user mentions: "tenets review", "kill criteria", "thesis check", "should we still be doing this", "pivot or kill", "is this still the right bet".

## When NOT to use

- The artifact is operational performance over the last week. Use `weekly-business-review`.
- The artifact is a post-incident review. Use `correction-of-errors`.
- The bet was authorized last month. The PRFAQ is the contract; do not re-litigate the thesis without a trigger.
- The user wants confirmation that the bet is still right. Refuse; offer to surface evidence that it isn't.

## Inputs

```yaml
product_tenets:                 # OPTIONAL — list of "if we're wrong about X, stop" statements
                                # if absent, the skill synthesizes from original_prfaq and tags as [inference]
original_prfaq:                 # REQUIRED — source for tenet synthesis if product_tenets is empty
review_trigger:                 # market_shift | competitor_move | regulatory | technology_shift |
                                # metric_anomaly | scheduled_annual | named_concern
trigger_detail:                 # what specifically changed, with citations
metrics_snapshot:               # current state of the bet's success metrics
external_context_changes:       # documented external shifts since PRFAQ approval; required for tenet validity check
team_cost_this_period:          # quantified — headcount, dollars, opportunity time
competing_priorities_displaced: # named alternatives this team could be working on instead
review_period:                  # how much time the review covers (since last tenets review or PRFAQ approval)
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Trigger documented | `review_trigger` is one of the named values AND `trigger_detail` cites a specific change | Reject; reviews without triggers become theater |
| Tenets exist or are synthesized | `product_tenets` is non-empty, OR synthesized from `original_prfaq.decision_recommendation.rationale` and tagged `[inference]` with "ratification needed" flag | Synthesize and flag |
| External context cited per tenet | Each tenet's validity check cites `external_context_changes`, not just metrics | Re-check against external context |
| Metric satisficing check run | Each tenet has an explicit `metric_satisficing_check`: is metric agreement consistent with external evidence? | Run it; emit explicit `metric_satisficing: true` when caught |
| Recommendation matches tenet status | `continue` requires zero `invalid` tenets; any `invalid` forces `kill`, `pivot`, or `escalate` | Force the harder recommendation |
| Opportunity cost named | `competing_priorities_displaced` is non-empty and the recommendation cites stronger alternatives if relevant | Demand specific alternatives |
| Escalate has a target | When recommendation is `escalate`, `escalation_target`, `decision_needed`, and `briefing_summary` are all populated | Populate them |

## Process

1. **Confirm the trigger.** A scheduled-annual review still requires `trigger_detail` to say what *specifically* prompted asking now versus six months ago.
2. **Locate or synthesize tenets.** If absent, derive them from `original_prfaq.decision_recommendation.rationale` and any "we assume that" statements in the PRFAQ. Tag synthesized tenets `[inference]` and flag them for team ratification before this review's recommendation is acted on.
3. **For each tenet, check external evidence first.** What in `external_context_changes` supports or contradicts this tenet? Cite the change.
4. **Then check metric correlation.** Do the metrics agree with the external evidence?
5. **Run the metric satisficing check.** If external context contradicts the tenet but metrics look fine, the tenet is `invalid`. The metrics are measuring something narrower than the bet.
6. **Write the thesis drift narrative.** Two paragraphs. How has the original bet evolved? What is the team actually shipping versus what they promised in the PRFAQ?
7. **Assess opportunity cost.** Name specific competing priorities. "Other things" does not count.
8. **Derive the recommendation.** Use the rules below. Do not soften it.
9. **If `escalate`:** write the briefing. Three to five sentences a leader can use to make the call.

## Hard rule (non-negotiable)

```text
External context speaks before metrics.
A tenet is invalid if external evidence contradicts it, regardless of what the dashboard says.
A single invalid tenet forces kill, pivot, or escalate. It does not collapse to continue.
A review without a documented trigger is review theater.
```

## Recommendation logic

```text
all tenets valid                                 → continue
some tenets unknown, none invalid                → continue with active monitoring (named in output)
one or more tenets invalid, scope is local       → pivot
one or more tenets invalid, thesis broken        → kill
decision authority is above this review          → escalate
```

## Output schema

```yaml
review_trigger:
trigger_detail:                 # cited
review_period:
tenets:
  - tenet:                      # the "if we're wrong about X, stop" statement
    source:                     # written | inferred_from_prfaq
    needs_ratification:         # bool — true if synthesized
    validity:                   # valid | invalid | unknown
    external_evidence:          # citations from external_context_changes — REQUIRED
    metric_correlation:         # do metrics agree with the external evidence?
    metric_satisficing_check:   # bool — true means metrics look fine but tenet is failing
    confidence:                 # [fact] | [assumption] | [inference] | [open question]
thesis_drift_narrative:         # 2 paragraphs prose; how the original bet has evolved
recommendation:                 # continue | kill | pivot | escalate
rationale:                      # citations from tenet validity AND external context
if_pivot:                       # only when recommendation == pivot
  pivot_hypothesis:
  validation_needed:            # what evidence would confirm the new hypothesis
  timeline:
if_escalate:                    # only when recommendation == escalate
  escalation_target:            # named individual or role
  decision_needed:              # specific question, not "what should we do"
  briefing_summary:             # 3-5 sentences leadership can act on
opportunity_cost_assessment:
  team_cost_this_period:        # restated from input
  competing_priorities:         # named alternatives, with reasoning why each is stronger
  if_killed_what_replaces:      # specific work the team could do instead
metric_satisficing_warning:     # bool — true if any tenet failed metric_satisficing_check
prfaq_revision_needed:          # bool — true if recommendation forces PRFAQ changes
```

## Stop conditions

- No `original_prfaq` AND no `product_tenets`. There is no bet to review; refuse.
- `review_trigger` is absent or vague ("just checking in"). Reject; require a specific trigger.
- `external_context_changes` is empty. Without external context, tenet validity reduces to metric checking, which is what `weekly-business-review` is for. Refuse and route to WBR.
- The user requests confirmation that the bet is still right. Refuse; offer to surface evidence it isn't.
- The team has not yet executed the original PRFAQ's MVP. A bet that has not been tested cannot have its tenets falsified by reality.

## Failure modes

- **Metric satisficing.** Output metrics within target while input metrics or external context reveal the thesis is dead. The team has narrowed what they measure to what is still working. Caught only by checking external context first, metrics second.
- **Tenet absence laundering.** Synthesizing tenets from the PRFAQ and presenting them as if they were written by the team. The `needs_ratification` flag exists to prevent this; do not strip it.
- **Soft continue.** Recommendation of `continue` when one or more tenets are `unknown` without naming the active monitoring required. `continue` with unknown tenets is acceptable only with a named monitoring mechanism — otherwise force `escalate`.
- **Pivot as kill avoidance.** Recommending `pivot` when the honest answer is `kill` because the team has political capital invested. The thesis drift narrative is the safeguard; if the pivot hypothesis is a different bet, that is a kill, not a pivot.
- **Escalate as decision avoidance.** Recommending `escalate` because the reviewer doesn't want to commit. `escalate` requires that the decision is genuinely above the review's authority, not that the reviewer is uncomfortable.
- **Opportunity cost handwaving.** "We could be doing other things" without naming them. The point of opportunity cost is comparison; without alternatives, the assessment is decorative.
- **Sunk cost rationalization in the rationale.** "We've invested so much already" is not a tenet. Strip from rationale.

## Reviewer pass

After emitting, run a second pass that checks:

- Every tenet's `external_evidence` cites something from `external_context_changes`, not from `metrics_snapshot`.
- `recommendation` is consistent with the recommendation logic — no `continue` with an `invalid` tenet.
- `metric_satisficing_warning` is `true` if any tenet's `metric_satisficing_check` is `true`.
- `if_pivot` is populated only when `recommendation == pivot`; same for `if_escalate`.
- Synthesized tenets carry `needs_ratification: true`.

## Follow-up mechanism

- `continue` → next tenets-review fires on the next external context shift or at annual review, whichever is sooner.
- `kill` → the bet is wound down; the team's competing priorities surface a new PRFAQ via `working-backwards-prfaq`.
- `pivot` → the pivot hypothesis becomes input to a new PRFAQ; the validation_needed becomes the new bet's `success_metrics`.
- `escalate` → the briefing goes to the named target; the decision they make becomes a follow-up artifact tracked back to this review.
- If `metric_satisficing_warning: true`, the WBR's metric set should be re-examined — the team is measuring the wrong things.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: full packet → `original_prfaq`; `decision_recommendation.rationale` → tenet synthesis basis when written tenets are absent
- `mechanism-designer`: when the bet's operating mechanism is the artifact being reviewed → `metrics_snapshot` from the mechanism's outputs
- `weekly-business-review`: persistent variance flagged in WBR → `review_trigger: metric_anomaly` + `trigger_detail`
- External: market reports, competitor analyses, regulatory updates → `external_context_changes`

**Feeds into**

- `working-backwards-prfaq`: `kill` or `pivot` recommendations → new PRFAQ for whatever replaces this bet (or a revised PRFAQ if `pivot`)
- `mechanism-designer`: when the recommendation requires a new operating mechanism for a pivot
- `weekly-business-review`: `metric_satisficing_warning: true` → the WBR's metric set itself needs revision; flag as a `decision needed`

Enums used: `tenet_status`, `bet_recommendations`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml). See [`GLOSSARY.md`](../../GLOSSARY.md#metric-satisficing) for the named failure mode this skill exists to catch.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
