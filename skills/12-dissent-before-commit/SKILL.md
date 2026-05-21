---
name: dissent-before-commit
description: Surface the strongest case against firing this mechanism right now, at execution time — not at authoring time. Distinct from the six-pager's authoring-time dissent gate ("who disagrees with this proposal?") and the leadership-principles-reviewer's proposal-time check ("has disconfirming evidence been sought?"). This skill asks one focused execution-time question and forces a `proceed` only when the strongest dissent has been either addressed (cite the change) or accepted (name the tradeoff). The named failure mode is stale dissent reuse — copying authoring-time concerns without checking what has changed since. Use when a mechanism is about to fire, when an irreversible action is queued, or when the user mentions "before we ship", "one-way door", "are we sure", "pre-commit review", "dissent check", "is this still the right call".
category: interrogative
---

# Dissent Before Commit

Pre-execution gate on a specific action — typically a mechanism about to fire, a launch about to happen, or an irreversible change about to be made. Asks one question:

> What is the strongest case against firing *this* mechanism *right now*?

The temporal axis is the differentiator. The six-pager's dissent gate fires at authoring time and surfaces *who disagrees with this proposal*. The leadership-principles-reviewer's `are_right_a_lot` check fires at proposal-review time and surfaces *whether disconfirming evidence was sought*. This skill fires at execution time and surfaces *what has changed since authoring, and whether the strongest current case against the action has been addressed or only acknowledged*.

The named failure mode is **stale dissent reuse**: the team points to the authoring-time dissent gate as proof that concerns were heard, and proceeds without checking whether anything has changed since that gate ran. Mechanisms accumulate state between authoring and execution. Dissent must be re-canvassed against current state.

## Quick start

1. Identify the proposed action precisely — the mechanism spec, launch decision, or irreversible change about to execute. Not a class of actions; this specific instance.
2. Run the reversibility check first. One-way doors raise the bar.
3. Canvass dissent from named perspectives (engineering, operations, support, security, customer-facing, finance, compliance) — see [`dissent-perspectives.yaml`](dissent-perspectives.yaml).
4. Identify the *strongest* case against execution. Force ranking. Not three cases; the strongest one.
5. Check state changes since authoring. Dissent canvassed before recent state changes is stale until re-checked.
6. Verify: has the strongest case been addressed in the action itself (cite the change), or accepted with a *named* tradeoff (cite the tradeoff)?
7. Emit recommendation: `proceed` / `proceed_with_changes` / `pause` / `escalate`.

## When to use

- A `mechanism-designer` output is about to begin executing and no narrative review sits between the spec and Build.
- A launch is queued and `launch-readiness-review` has returned `go` or `conditional_go` — confirm execution-time dissent has been surfaced before the ship event.
- An irreversible operational change is queued (deprecation, migration cut-over, hiring freeze, contract termination).
- The proposed action's authoring is more than 30 days old and material state changes have occurred since.
- The user mentions: "before we ship", "before we cut over", "one-way door", "are we sure", "pre-commit review", "dissent check", "is this still the right call", "any last objections".

## When NOT to use

- The artifact is still being authored. Use `six-page-narrative` or `leadership-principles-reviewer` instead.
- The artifact is post-execution and the question is what to learn. Use `correction-of-errors`, `ambitious-goal-grading`, or `tenets-review` depending on the question.
- The action has no irreversibility and no material stakes. The skill's overhead is greater than the value; proceed without it.
- The user wants confirmation that the action is fine. Refuse explicitly; offer to surface the strongest current case against it.
- The user wants a generic risk review. Refuse; route to `launch-readiness-review` (for launches) or `leadership-principles-reviewer` (for proposals).

## Inputs

```yaml
proposed_action:                # REQUIRED — the specific artifact about to execute
                                # mechanism spec, launch decision, deprecation plan, etc.
                                # not a class of actions; this instance
authoring_artifact:             # REQUIRED — the upstream PRFAQ / six-pager / mechanism spec that authorized the action
authoring_date:                 # when the authoring artifact was approved
proposed_execution_date:        # when the action is about to fire
irreversibility_assessment:     # REQUIRED — what is recoverable, what is not, time-cost of reversal
state_changes_since_authoring:  # REQUIRED (can be []) — incidents, customer-signal shifts,
                                # competitor moves, internal capacity changes since authoring
dissent_history:                # OPTIONAL — prior dissent surfaced in upstream skills:
                                #   six-page-narrative.dissent_section
                                #   leadership-principles-reviewer.are_right_a_lot
                                #   launch-readiness-review.predicted_failure_modes
dissent_perspectives_canvassed: # which functional viewpoints have been consulted for this review
                                # default set: engineering, operations, support, security,
                                # customer-facing, finance, compliance
                                # (skill demands at least three for non-trivial actions)
```

## Validation gates

| Gate | Pass criteria | If it fails |
|------|---------------|-------------|
| Action is specific | `proposed_action` refers to a single instance, not a class (e.g., "the v1.2 cut-over on Tuesday" not "the migration") | Reject; demand specificity |
| Reversibility assessed | `irreversibility_assessment` names recoverable vs not, with time-cost estimate | Reject; demand assessment before review |
| State changes documented | `state_changes_since_authoring` is non-empty OR the field carries a positive assertion "no material changes since authoring" with named scope | Demand the assertion or the changes |
| Strongest case named | `strongest_dissent_case` is a single argument, ranked above other dissent | Force ranking; multiple co-equal cases is a hedge |
| Named perspective | `dissent_perspective` is a named function/role/stakeholder, not "the team" or "people" | Demand specificity |
| Stale-dissent check | If `dissent_history` exists AND `state_changes_since_authoring` is non-empty, every prior dissent item carries a `still_applies` assessment against current state | Re-canvass against current state |
| Addressed-or-accepted | `proceed` recommendation requires `addressed_in_action: true` (with citation) OR `accepted_tradeoffs` populated with named tradeoff | Force `proceed_with_changes`, `pause`, or `escalate` |
| One-way-door bar | If `reversibility_check: one_way_door`, `proceed` requires `addressed_in_action: true` — accepted tradeoff is insufficient | Raise the bar; pause or escalate |
| Perspective coverage | For non-trivial actions, at least three perspectives in `dissent_perspectives_canvassed` | Canvass more |

## Process

1. **Pin the action.** "The migration" is not a reviewable artifact. "The v1.2 → v2 cut-over on Tuesday at 14:00 UTC" is.
2. **Reversibility check first.** Bezos's one-way / two-way door framing. A one-way door raises the dissent bar: accepted tradeoffs are insufficient; dissent must be addressed in the action itself.
3. **Re-canvass dissent against current state.** If `dissent_history` exists, walk each prior item and mark `still_applies: true | false | new`. Items marked `new` are dissent surfaced by state changes that weren't present at authoring.
4. **Force ranking to a single strongest case.** Asking for "all dissent" produces lists. Asking for the *strongest* case produces forced ranking. The strongest case is the one most likely to make the team regret the action if it goes ahead.
5. **Identify the dissent perspective by name.** Not "the team" — engineering, operations, support, security, customer-facing, finance, or compliance. The perspective's stake is what makes the dissent load-bearing.
6. **Check addressed vs accepted.** Addressed means the action has been modified to handle the dissent (cite the change). Accepted means the dissent stands and the action proceeds anyway (cite the named tradeoff). "Heard and considered" is neither and fails the gate.
7. **Emit the recommendation.** Use the table below. Do not soften.

## Hard rule (non-negotiable)

```text
"Heard and considered" is not addressing dissent. It is acknowledgment, which is
free. Addressing dissent costs something — a change to the action, a named
tradeoff the team will own publicly, or a delay to surface more evidence.

If the recommendation is proceed, exactly one of these must be true:
  - the strongest dissent has been addressed by a documented change to the action
  - the strongest dissent has been accepted, with a NAMED tradeoff the team owns

For one-way doors, the second is insufficient. Address it or pause.
```

## Recommendation logic

```text
strongest case addressed in action                                → proceed
strongest case accepted with named tradeoff, two-way door         → proceed
strongest case accepted with named tradeoff, one-way door         → pause (raise the bar)
strongest case neither addressed nor accepted with named tradeoff → proceed_with_changes
                                                                    (the changes are the addressing)
strongest case requires information the team doesn't have         → pause until information surfaces
strongest case is fundamentally about the underlying PRFAQ's
  thesis being wrong                                              → escalate to tenets-review
decision authority is above this review                           → escalate
```

## Output schema

```yaml
proposed_action:                # restated specifically
authoring_artifact:
authoring_date:
proposed_execution_date:
time_since_authoring:           # computed; >30 days raises stale-dissent risk
irreversibility_assessment:
reversibility_check:            # one_way_door | two_way_door | partial_reversal
reversibility_rationale:        # time/cost to reverse if attempted
state_changes_since_authoring:  # restated from input; if empty, the positive assertion
dissent_recanvassed:
  - prior_dissent:              # from dissent_history
    still_applies:              # true | false | new (new = surfaced by state change)
    rationale:
dissent_perspectives_canvassed:
  - perspective:                # engineering | operations | support | security |
                                # customer-facing | finance | compliance | other
    consulted:                  # bool
    raised_concerns:            # bool + summary if true
strongest_dissent_case:         # the single most compelling argument against execution
dissent_perspective:            # named function/role/stakeholder source
dissent_basis:                  # what evidence/reasoning supports it; cite
addressed_in_action:            # bool
addressed_citation:             # required if addressed_in_action == true
accepted_tradeoffs:             # list with rationale
  - tradeoff:
    accepted_by:                # named owner taking responsibility
    rationale:
recommendation:                 # proceed | proceed_with_changes | pause | escalate
if_proceed_with_changes:        # specific changes required
if_pause:                       # what additional information/work resolves the pause
  trigger_for_resume:
  estimated_resolution_time:
if_escalate:
  escalation_target:            # named individual or role
  decision_needed:              # specific question, not "what should we do"
  briefing_summary:             # 3-5 sentences leadership can act on
stale_dissent_warning:          # bool — true if dissent_history existed and state_changes were non-empty
                                # and re-canvass was performed
```

## Stop conditions

- `proposed_action` is a class of actions ("the migrations") rather than a specific instance. Refuse; demand a single action.
- `authoring_artifact` is absent. There is no contract to dissent against; route to the appropriate authoring skill first.
- `irreversibility_assessment` is missing. The reversibility check is the first move; refuse without it.
- The user requests confirmation that the action is fine. Refuse; offer the strongest case against.
- The user requests a generic risk review. Refuse; route to `launch-readiness-review` (launches) or `leadership-principles-reviewer` (proposals).
- The action has already executed. There is nothing to gate. Route to `correction-of-errors` (if it went badly) or `tenets-review` / `ambitious-goal-grading` (LEARN).
- The user attempts to use this skill to override `launch-readiness-review.no_go`. Refuse; `no_go` is its own gate.

## Failure modes

- **Stale dissent reuse.** The team points to authoring-time dissent as proof that concerns were heard, and proceeds without checking state changes. The `dissent_recanvassed` gate exists to prevent this. Items must be marked `still_applies` against current state, or `new` if surfaced by state changes.
- **Strawman dissent.** Naming concerns no one actually held, easy to dismiss. Detect by checking whether the named perspective has actually been consulted and whether the dissent has a documented basis.
- **Generic dissent.** "There are risks" without naming the perspective or the specific concern. The named-perspective gate and dissent_basis citation requirement prevent this.
- **"Heard and considered" laundering.** Claiming dissent was canvassed with no evidence of either addressing the concern or accepting a named tradeoff. The addressed-or-accepted gate is the hard rule.
- **Rubber-stamp pattern.** Every dissent review reads identically across actions; the process has become decorative. Detect by checking whether the `strongest_dissent_case` varies meaningfully across reviews; identical patterns suggest a checkbox.
- **One-way-door blindness.** Proceeding on irreversible actions with only acknowledged (not addressed) dissent. The one-way-door bar is the safeguard.
- **Forced-ranking dodge.** Producing three "co-equal" dissent cases to avoid ranking the strongest one. Force a single answer; co-equal is a hedge.
- **Dissent shopping.** Canvassing perspectives until one returns "no concerns" and stopping there. The minimum-three-perspectives gate and the requirement to surface concerns when they exist are the safeguards.

## Reviewer pass

After emitting, run a second pass that checks:

- `recommendation: proceed` is paired with exactly one of `addressed_in_action: true` or `accepted_tradeoffs` non-empty. Never both empty.
- One-way-door actions with `accepted_tradeoffs` only (no `addressed_in_action`) carry `recommendation: pause`, not `proceed`.
- `strongest_dissent_case` is a single statement, not a list.
- `dissent_perspective` is one of the named functional roles, not "the team" or "people".
- If `dissent_history` was non-empty AND `state_changes_since_authoring` non-empty, every prior dissent item appears in `dissent_recanvassed` with a `still_applies` assessment.
- `stale_dissent_warning: true` only when both conditions above hold.

## Follow-up mechanism

- `proceed` → action fires on schedule. The `addressed_citation` or `accepted_tradeoffs` are archived with the action's audit trail for post-execution review.
- `proceed_with_changes` → action does not fire until the named changes are in place. The skill re-runs against the updated action.
- `pause` → action does not fire. Trigger conditions (`trigger_for_resume`) are watched; when they resolve, the skill re-runs.
- `escalate` → briefing goes to the named target. The decision they make is appended to the audit trail.
- If `stale_dissent_warning: true` repeatedly across actions on the same initiative, route to `correction-of-errors` on the dissent mechanism itself. The team is treating authoring-time dissent as a one-time gate when it should be re-canvassed against state.
- If the strongest case turned out to be correct in retrospect (the addressed dissent or accepted tradeoff materialized), the action's `correction-of-errors` should reference the original dissent record. Dissent that proved right is the most valuable kind.

## Handoffs

**Consumes from**

- `mechanism-designer`: mechanism spec about to fire → `proposed_action`; `inspection_method`, `escalation_rule` → context for reversibility check
- `working-backwards-prfaq`: authorizing PRFAQ → `authoring_artifact`; `risks`, `mvp_boundary` → context for dissent re-canvass
- `six-page-narrative`: when six-pager authored the action → `authoring_artifact`; its `dissent_section` → `dissent_history`
- `leadership-principles-reviewer`: prior `are_right_a_lot` findings → `dissent_history`
- `launch-readiness-review`: `predicted_failure_modes` → `dissent_history` for launch actions
- `correction-of-errors`: prior incidents on the same mechanism or adjacent systems → `state_changes_since_authoring`
- `weekly-business-review`: recent variance or anomalies → `state_changes_since_authoring`

**Feeds into**

- `mechanism-designer`: `proceed_with_changes` recommendations → revisions to the mechanism spec before it fires
- `launch-readiness-review`: `pause` or `escalate` on a launch-adjacent action → informs the launch gate
- `working-backwards-prfaq`: when the strongest dissent surfaces a thesis-level issue → `escalate` routes to `tenets-review`, which may then route to a new PRFAQ
- `correction-of-errors`: when an action proceeded despite addressed dissent and the dissent proved correct → CoE references the original dissent record
- `tenets-review`: when `recommendation: escalate` because the dissent is fundamentally about the underlying thesis → `review_trigger: named_concern`

Enums used: `dissent_recommendation`, `reversibility`, `dissent_perspective`, `assumption_tags` — see [`vocabulary.yaml`](../../vocabulary.yaml). See [`GLOSSARY.md`](../../GLOSSARY.md#stale-dissent-reuse) for the named failure mode this skill exists to catch. See [`dissent-perspectives.yaml`](dissent-perspectives.yaml) for the functional perspectives canvassed by default.

---

This skill conforms to [`SKILL_DESIGN_PATTERN.md`](../../SKILL_DESIGN_PATTERN.md).
