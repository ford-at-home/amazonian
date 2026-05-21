---
name: ambitious-goal-grading
description: Grade goals on calibration, not just attainment. A target hit at 100% with no surprise is presumptive sandbagging — the skill demands a counter-argument before accepting that calibration was honest. Distinguishes goal-setting quality from outcome quality, separately from tenets-review (was the bet right?) and correction-of-errors (what broke?). The named failure mode is sandbagging laundering — "ambitious enough to motivate, achievable enough to hit" doublespeak. Use on quarterly or annual goal-grading, when targets are being set for next period, or when the user mentions "sandbagged", "stretch goal", "goal calibration", "OKR scoring", "graded the goals", "were our targets right".
category: interrogative
---

# Ambitious Goal Grading

Grade goals on **calibration**, not just on attainment. Asks one question:

> Were these targets set at the right difficulty level, *regardless* of whether the bet landed?

A team that sets sandbagged goals and hits them passes `tenets-review` (bet was right, outcome achieved) and passes `correction-of-errors` (nothing broke). The goal-setting was still bad. That failure mode is invisible to both existing LEARN skills. This is the skill that catches it.

The named failure mode is **sandbagging laundering**: targets set deliberately low and described as "ambitious enough to motivate, achievable enough to hit." Hitting 100% on a target the team was certain they would hit is not success — it is target-setting that taught the organization nothing.

## Quick start

1. Collect every goal from the period — including ones the team chose not to grade. Survival bias is the first failure mode.
2. For each goal, compute `attainment_score` (0.0–1.0). 1.0 is *not* the target; ~0.7 is.
3. For every 100% hit, demand a `surprise_evidence` field. If the team can't name what surprised them on the way to the target, the goal was sandbagged.
4. For every <50% hit, distinguish overreach (target was wrong) from execution failure (target was right; something else broke — route to `correction-of-errors`).
5. Check chronic patterns across periods. Three consecutive 100%-hits with no surprise evidence is a process failure on goal-setting, not a celebration.
6. Emit recalibration recommendations for the next period.

## When to use

- Quarterly or annual goal-grading is happening and someone needs to ask "were these targets honest" before "did we hit them."
- Targets are being set for the next period and the team's prior calibration history should inform them.
- A pattern is emerging — recurring 100% hits, or recurring near-misses — and the question is whether goal-setting itself is the problem.
- The user mentions: "sandbagged", "stretch goal", "goal calibration", "OKR scoring", "graded the goals", "were our targets right", "did we set the bar too low".

## When NOT to use

- The question is "was the bet right" — use `tenets-review`.
- A specific goal missed because something broke — use `correction-of-errors`.
- The team has not yet executed a full period against these goals. There is nothing to grade. Refuse.
- The team wants a celebration of having hit their targets. Refuse explicitly; offer to surface whether the targets were honest.
- The artifact is a single isolated goal with no comparison history and no team-stated difficulty expectation. The skill needs at least one of: prior periods, a `goal_setting_context` describing the team's stated difficulty intent, or sibling goals to pattern-match against.

## Inputs

```yaml
period:                         # REQUIRED — what period this grading covers
period_goals:                   # REQUIRED — every goal from the period, including unhit and abandoned
  - goal:                       # the goal statement
    target:                     # numeric target with units, OR explicit qualitative target
    actual:                     # actual outcome with units
    metric_type:                # input_metric | output_metric (see vocabulary.yaml)
    goal_setting_context:       # what the team said about this goal at authoring time:
                                #   "committed" | "stretch" | "aspirational" | "unstated"
    surprise_evidence:          # OPTIONAL — what surprised the team on the way to this target
                                #   (required when attainment_score >= 1.0)
original_prfaq:                 # REQUIRED — source of original targets and their rationale
abandoned_goals:                # REQUIRED (can be empty []) — goals dropped mid-period
  - goal:
    dropped_at:                 # when in the period
    reason:                     # why
mid_period_target_changes:      # REQUIRED (can be empty []) — any target that moved during the period
  - goal:
    original_target:
    revised_target:
    revision_date:
    justification:
prior_period_gradings:          # OPTIONAL — prior ambitious-goal-grading outputs, for chronic-pattern detection
review_period:                  # how much time this grading covers
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Survival bias check | All goals from the period are present in `period_goals` OR listed in `abandoned_goals` OR named in an explicit `excluded_with_rationale` list | Reject; demand the missing goals |
| 100% hits justified | Every goal with `attainment_score >= 1.0` carries a non-empty `surprise_evidence` field OR is flagged `calibration_assessment: sandbagged` | Force the sandbagged flag |
| Goalpost-moving disclosed | Every `mid_period_target_changes` entry is reflected in that goal's calibration assessment, not silently absorbed | Surface the change; recompute against original target |
| Overreach vs execution distinguished | Every `attainment_score < 0.5` carries either a `calibration_assessment: overreach` with target rationale, or a routing note to `correction-of-errors` | Route or classify |
| Pattern check ran when data available | If `prior_period_gradings` supplied, `pattern_assessment` is populated | Run the check |
| Goal-setting context preserved | Every goal carries its `goal_setting_context`; `unstated` is itself a finding | Demand the team state difficulty intent for next period |
| Outcome contamination not happening | The grading does not invoke whether the underlying bet was right — that's `tenets-review` | Strip outcome-quality language from the grading |

## Process

1. **Completeness check.** Survival bias is the first failure mode. Count `period_goals + abandoned_goals + excluded_with_rationale` and verify it matches the period's authorized goal set.
2. **Compute attainment.** For each goal: `attainment_score = actual / target` for numeric goals, clamped to [0.0, 1.5] (over-attainment past 1.5 is itself a calibration signal, not a credential). For qualitative goals, score on the rubric `met | partially_met | not_met` and map to {1.0, 0.5, 0.0} for pattern math.
3. **Classify calibration.** Apply the calibration table below. Do not soften.
4. **Run goalpost-moving check.** For each `mid_period_target_changes` entry, recompute attainment against the *original* target and disclose both numbers.
5. **Distinguish overreach from execution failure.** For attainment < 0.5: was the target set at a level no honest plan would have reached, or did a real plan break? Route execution failures to `correction-of-errors`.
6. **Chronic pattern detection.** If `prior_period_gradings` supplied, count consecutive periods of each calibration assessment per goal. Three in a row of the same pattern is the threshold for `chronic_*`.
7. **Recalibration recommendations.** For each goal that recurs into the next period, recommend a target. Cite the calibration assessment. Do not say "stretch by 10%" without a reason.
8. **Tenet violation check.** If `chronic_sandbagging` is present, flag `tenet_violation_candidate: true`. A team that systematically hits easy targets is not testing the bet's thesis — they are running a confirmation engine. Route to `tenets-review`.

## Hard rule (non-negotiable)

```text
A target hit at 100% with no named surprise is presumptive sandbagging.
The team must produce surprise_evidence to claim honest calibration.
"It was hard but we made it" is not surprise evidence.
Surprise evidence names something the team did NOT expect that changed the path —
  a method that worked when it shouldn't have, a constraint that vanished, a customer
  who behaved differently than predicted. Without that, the target was sandbagged.

Three consecutive 100%-hits without surprise evidence on the same recurring goal is
a tenet violation candidate. The team has stopped testing the thesis.
```

## Calibration assessment table

```text
attainment_score >= 1.0  AND surprise_evidence present                → well_calibrated
attainment_score >= 1.0  AND surprise_evidence absent                 → sandbagged
attainment_score in [0.6, 1.0)                                        → well_calibrated
attainment_score in [0.3, 0.6) AND honest plan existed                → well_calibrated (ambitious, partially landed)
attainment_score in [0.3, 0.6) AND no honest plan ever existed        → overreach
attainment_score < 0.3   AND execution broke                          → route to correction-of-errors
attainment_score < 0.3   AND no execution broke                       → overreach
goal_setting_context == "unstated"                                    → unknowable; demand stated intent for next period
mid_period_target_changes present AND not disclosed                   → goalpost_moving — supersedes other classifications
```

`well_calibrated` is the normal case. The skill exists to detect deviations from it.

## Output schema

```yaml
period:
review_period:
goals_graded:
  - goal:
    target:                      # original
    target_revised:              # only if mid_period_target_changes present
    actual:
    attainment_score:            # 0.0–1.5
    goal_setting_context:        # committed | stretch | aspirational | unstated
    calibration_assessment:      # sandbagged | well_calibrated | overreach | unknowable | goalpost_moving
    surprise_evidence:           # required when attainment_score >= 1.0
    rationale:                   # cite the calibration table row
    routes_to:                   # OPTIONAL — e.g., "correction-of-errors" for execution failure
goals_abandoned:                 # restated from input, with assessment
  - goal:
    reason:
    assessment:                  # honest_drop | abandoned_to_protect_hit_rate
excluded_with_rationale:         # goals not graded; rationale required
survival_bias_check:             # pass | fail
pattern_assessment:              # chronic_sandbagging | chronic_overreach | well_calibrated | mixed | insufficient_data
pattern_evidence:                # citations from prior_period_gradings when applicable
recalibration_recommendations:
  - goal:
    current_target:
    recommended_target_for_next_period:
    rationale:                   # cite calibration assessment
    stated_difficulty_for_next_period: # committed | stretch | aspirational — must be stated
tenet_violation_candidate:       # bool — true if chronic_sandbagging present
tenet_violation_basis:           # cited evidence if true
goalpost_moving_summary:         # all disclosed mid-period changes with assessment
prfaq_revision_needed:           # bool — true if recurring metrics' targets recommend revision
```

## Stop conditions

- No `original_prfaq` AND no `mechanism_spec` defining the metrics. There is no contract to grade against; refuse.
- The team has not completed a full period. Refuse.
- `period_goals` is a single goal with no prior history and no `goal_setting_context`. There is nothing to grade in isolation; require comparison data.
- The user requests confirmation that goal-setting was good. Refuse; offer to surface whether targets were honest.
- The user requests grading of effort or process. Refuse; that is a retrospective, not goal calibration.
- `abandoned_goals` is suspiciously large relative to `period_goals` and no rationale is provided. Surface this as `assessment: abandoned_to_protect_hit_rate` until rationale is supplied.

## Failure modes

- **Sandbagging laundering.** "Ambitious enough to motivate, achievable enough to hit" — language that sounds principled and is actually a confession. Detect by checking whether any goal labeled "stretch" was hit at 100% without surprise evidence.
- **Goalpost moving.** A target moved mid-period, the team grades against the revised target, and the original target disappears. The `mid_period_target_changes` gate exists to surface this. Recompute against the original.
- **Survival bias.** Only grading goals that were achieved. Abandoned and dropped goals are quietly dropped from the grading itself. The survival bias check is the gate.
- **Process-output confusion.** Grading the team's effort instead of the goal's calibration. "The team worked hard" is not a calibration signal. Strip from rationale.
- **Outcome contamination.** Grading whether the underlying bet was right instead of whether the target was set right. A team can hit a well-calibrated target on a doomed bet, and miss a well-calibrated target on a winning bet. Route bet-validity questions to `tenets-review`.
- **Execution failure dressed as overreach.** Calling a missed goal "overreach" when the real cause is something broke. Demand: was there ever a plan that could have hit this target? If yes, route to `correction-of-errors`.
- **Sandbagged-to-protect-hit-rate abandonment.** Dropping goals mid-period to protect the team's attainment percentage. The `abandoned_to_protect_hit_rate` assessment exists to name this.
- **Three-in-a-row blindness.** Reading each period's grading in isolation and missing that the same goal has been sandbagged for three quarters. The pattern_assessment gate is the safeguard.

## Reviewer pass

After emitting, run a second pass that checks:

- Every `attainment_score >= 1.0` either has `surprise_evidence` populated OR carries `calibration_assessment: sandbagged`. Never both empty.
- Every `mid_period_target_changes` entry has been recomputed against the original target.
- The `survival_bias_check` is `pass` only if accounted-for goals match the period's authorized goal set.
- `pattern_assessment` is `insufficient_data` only when `prior_period_gradings` is genuinely absent — never as a hedge when data is available.
- `tenet_violation_candidate: true` is paired with non-empty `tenet_violation_basis`.
- No `recalibration_recommendations` entry has `rationale: "stretch by 10%"` or equivalent uncited percentage move. Cite the calibration assessment.

## Follow-up mechanism

- `well_calibrated` → next period's target adjusts on normal cadence; no special action.
- `sandbagged` → next period's target moves up; `goal_setting_context` for next period must be stated by the team (no more `unstated`).
- `overreach` → next period's target moves down or the goal is reframed; the team owes a different plan.
- `goalpost_moving` → the team owes a process change on how mid-period revisions happen. The change itself is a `correction-of-errors` candidate against the goal-setting mechanism.
- `chronic_sandbagging` → route to `tenets-review`. The team is not testing the thesis.
- `chronic_overreach` → route to `tenets-review` or to a six-page-narrative on the team's capacity. The team is consistently planning beyond what it can execute.
- `routes_to: correction-of-errors` → trigger CoE on the specific goal that missed for execution reasons.

## Handoffs

**Consumes from**

- `working-backwards-prfaq`: `success_metrics` → `period_goals`; `decision_recommendation.rationale` → original target rationale
- `weekly-business-review`: aggregated period actuals → `period_goals[].actual`; variance classifications give context to misses
- `mechanism-designer`: when metrics were defined by an operating mechanism rather than authored in a PRFAQ → `mechanism.outputs` → `period_goals`
- Prior `ambitious-goal-grading`: full prior output → `prior_period_gradings` for chronic-pattern detection

**Feeds into**

- `working-backwards-prfaq`: `recalibration_recommendations` and `prfaq_revision_needed: true` → next PRFAQ's `success_metrics`; chronic patterns inform `customer.problem` and `mvp_boundary`
- `weekly-business-review`: `recalibration_recommendations` → next period's WBR target tables for recurring metrics
- `tenets-review`: `tenet_violation_candidate: true` → `review_trigger: named_concern` + `trigger_detail` citing the chronic pattern
- `correction-of-errors`: per-goal `routes_to: correction-of-errors` → individual CoE on execution failure
- `mechanism-designer`: when `goalpost_moving` appears, the underlying goal-setting mechanism needs redesign → mechanism revision

Enums used: `calibration_assessment`, `attainment_score`, `pattern_assessment`, `goal_setting_context`, `metric_types`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml). See [`GLOSSARY.md`](../../GLOSSARY.md#sandbagging-laundering) for the named failure mode this skill exists to catch. See [`calibration-patterns.yaml`](calibration-patterns.yaml) for detection heuristics.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
