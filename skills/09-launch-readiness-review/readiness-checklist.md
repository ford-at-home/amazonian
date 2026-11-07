# Launch Readiness Checklist

Pre-flight checklist mapping PRFAQ fields to the artifacts launch-readiness-review needs. Use this before invoking the skill, not as a substitute for it.

> A checked box is not evidence. Each item below requires an artifact or measurement, not a yes.

## Customer outcome reconnection

- [ ] The PRFAQ's `desired_customer_outcome` has been quoted into the review inputs verbatim.
- [ ] At least one piece of `customer_outcome_evidence` exists — dogfood data, beta cohort behavior, or a documented synthetic test that produces the outcome end-to-end.
- [ ] The evidence is tagged honestly: `[fact]` requires measured behavior; `[inference]` is what you have from a small beta; `[assumption]` is what you have from internal opinion.

## Scope diff

- [ ] Every item in PRFAQ `mvp_boundary.in_scope` is located in either `features_shipped` or `features_deferred`. Nothing is unaccounted for.
- [ ] Every `features_deferred` item carries a reason and a re-commitment date or an explicit kill.
- [ ] Every `features_shipped` item that diverged materially from the PRFAQ description is flagged for drift severity.

## Metric instrumentation

- [ ] Every PRFAQ `success_metric` has an `instrumentation_status` of `not_built`, `built_untested`, or `validated`.
- [ ] Every `validated` metric has its baseline measured and recorded.
- [ ] Every `not_built` metric forces `defer`. Every `built_untested` forces `no_go` until validated.

## Rollback testability

- [ ] The rollback `mechanism` is named (feature flag, deploy revert, data rollback, none).
- [ ] The rollback has been `tested` — actually exercised, not "we believe it would work."
- [ ] The `propagation_time` is measured end-to-end (config push to customer-observable effect).
- [ ] A named `owner_on_call` exists and has acknowledged the responsibility in writing.

## Risk register delta

- [ ] Every PRFAQ `risks[]` entry has a current status: `mitigated`, `open`, or `materialized`.
- [ ] Every `materialized` risk has a documented outcome and a lesson incorporated into `predicted_failure_modes`.
- [ ] Every `open` risk has its mitigation re-stated and its owner re-confirmed.

## Pre-mortem

- [ ] At least one `predicted_failure_mode` exists per `materialized` risk or `significant` drift.
- [ ] Every predicted failure has a `leading_indicator` that is measurable (not "we'll know it when we see it").
- [ ] Every predicted failure has a `response` and a named owner who watches for the leading indicator.

## Conditions (only if conditional_go)

- [ ] Every condition has a specific `owner` and a specific `gate_date`.
- [ ] No condition fixes post-launch. Post-launch fixes are accepted risk, not conditions.
- [ ] A specific follow-up review is scheduled to confirm each condition is met.

## Launch narrative

- [ ] Only drafted if the gate decision is `go`. Otherwise null.
- [ ] 2–3 sentences. Surfaces `significant` drift; does not paper over it.
- [ ] Includes the named customer outcome and the evidence the build produces it.

---

A team that checks every box above and still gets `no_go` should treat that as a feature of the skill, not a bug. The checklist is the floor; the gates are the ceiling.
